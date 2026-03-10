import os
import asyncio
from typing import Optional
import shutil
import time

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from llama_index.core.agent import ReActAgent
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import Settings

from file_to_text import pdf_to_text

SYSTEM_PROMPT = """
Usa herramientas cuando sea necesario.
Si la información ya está en el contexto de la conversación, puedes responder sin usar tools.
Si no sabes la respuesta, responde con "No sé".
"""

app = FastAPI()

_agent: Optional[ReActAgent] = None
_mcp_tools = None
_llm = None

MODEL = os.environ.get("MODEL") 
OLLAMA_URL = os.environ.get("OLLAMA_URL") 
KEEP_CONTEXT = os.environ.get("KEEP_CONTEXT", "False").lower() == "true"
API_KEY = os.environ.get("API_KEY")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class MessageRequest(BaseModel):
    message: str

async def write_tools(tools): 
    for tool in tools:
        print(f"Tool detectada: {tool.metadata.name}")
        
def get_agent(tools, llm):
    return ReActAgent(
        tools=tools,
        llm=llm,
        verbose=True,
        system_prompt=SYSTEM_PROMPT
    )

async def gather_tools_from_urls(urls, retry_seconds=2, max_retries=10):
    mcp_tools = []
    for url in urls:
        try:
            client = BasicMCPClient(url)
            spec = McpToolSpec(client=client)
            tools = await spec.to_tool_list_async()
            print(f"[ok] Conectado a {url}, tools: {len(tools)}")
            mcp_tools.extend(tools)
        except Exception as e:
            print(f"[error] No se pudo conectar a {url}: {e}")
    return mcp_tools

@app.on_event("startup")
async def startup_event():
    global _agent
    _llm = OpenAILike(
        model=MODEL,                  
        api_key=API_KEY,                    
        api_base=OLLAMA_URL,    
        is_chat_model=True,
        timeout=600)

    Settings.llm = _llm

    # 3. CARGA DE TOOLS
    mcp_urls_env = os.environ.get("MCP_SERVERS")
    mcp_urls = [u.strip() for u in mcp_urls_env.split(",") if u.strip()] if mcp_urls_env else []
    _mcp_tools = await gather_tools_from_urls(mcp_urls)

    _agent = get_agent(_mcp_tools, _llm)
    print("[info] Agent inicializado.")

def validate_pfd(file_path):
    return file_path.lower().endswith(".pdf") and os.path.getsize(file_path) > 0

def validate_file(file_name):
    upload_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(upload_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    files = os.listdir(upload_path)
    file_path = os.path.join(upload_path, files[0])
    return file_path

@app.post("/load_file")
def load_file(file: UploadFile = File(...)):
    file_time = str(time.time())
    temp_path = os.path.join(UPLOAD_DIR, file_time)
    os.makedirs(temp_path, exist_ok=True)
    file_path = os.path.join(temp_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_time": file_time}

@app.post("/api/agent")
async def api_agent(req: MessageRequest, file_name: Optional[str] = None):
    global _agent
    if _agent is None:
        raise HTTPException(status_code=500, detail="Agent no inicializado.")

    user_query = req.message.strip()
    inicio = time.time()

    if file_name:
        file_path = validate_file(file_name)
        extracted_text = pdf_to_text(file_path)
        user_query = f"DOCUMENTO:\n{extracted_text}\n\nPREGUNTA:\n{user_query}"
        #print(user_query)
    try:
        if not KEEP_CONTEXT:
            _agent = get_agent(_mcp_tools, _llm)
        
        print(f"user_query:")
        print(user_query)
        response = await _agent.run(user_query)
        
        print(f"Tiempo total: {time.time() - inicio:.2f}s")
        return {"response": str(response)}
    
    except Exception as e:
        print("[error] Error en la petición:", e)
        raise HTTPException(status_code=500, detail=str(e))