import os
import asyncio
from typing import Optional
import shutil
import time

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ToolCallResult,
    ToolCall,
                                             )
from llama_index.core.workflow import Context

from file_to_text import pdf_to_text

SYSTEM_PROMPT = """
Usa herramientas cuando sea necesario.
Si la información ya está en el contexto de la conversación, puedes responder sin usar tools.
Si no sabes la respuesta, responde con "No sé".
"""


app = FastAPI()

_agent: Optional[FunctionAgent] = None
_agent_ctx: Optional[Context] = None
MODEL = os.environ.get("MODEL") #"qwen3:32b"
OLLAMA_URL = os.environ.get("OLLAMA_URL") 
KEEP_CONTEXT = os.environ.get("KEEP_CONTEXT", "False").lower() == "true"

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class MessageRequest(BaseModel):
    message: str


async def write_tools(tools): 
    for tool in tools:
        print(tool.metadata.name, tool.metadata.description)
        
def get_agent(tools, llm: Ollama):
    agent = FunctionAgent(
        name="Jorge",
        description="Un asistente que puede responder",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT
    )
    return agent


async def handle_user_message(
        message_content: str,
        agent : FunctionAgent,
        agent_context : Context,
        verbose : bool = False
):
    handler = agent.run(message_content, ctx = agent_context)
    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            print(f" -- Llamando a la tool '{event.tool_name}' con los argumentos '{event.tool_kwargs}' --")
        elif verbose and type(event) == ToolCallResult:
            print(f"Tool {event.tool_name} respondio con {event}")
    response = await handler
    return str(response)


async def gather_tools_from_urls(urls, retry_seconds=2, max_retries=30):
    mcp_tools = []
    for url in urls:
        #Inicializa el cliente MCP y crea el agente.
        client = BasicMCPClient(url)
        spec = McpToolSpec(client=client)

        retries = 0
        while True:
            try:
                tools = await spec.to_tool_list_async()
                print(f"[ok] Conectado a {url}, tools: {len(tools)}")
                mcp_tools.extend(tools)
                break
            except Exception as e:
                retries += 1
                print(f"[warn] No se pudo conectar a {url}: {e} (intento {retries})")
                if retries >= max_retries:
                    print(f"[error] Max retries alcanzado para {url}, lo omito.")
                    break
                await asyncio.sleep(retry_seconds)
    return mcp_tools


@app.on_event("startup")
async def startup_event():
    global _agent, _agent_ctx

    #Setup llm Ollama
    llm = Ollama(model= MODEL,
                 base_url=OLLAMA_URL
                 ,requests_timeout=300)
    Settings.llm = llm

    #Setup tools
    mcp_urls_env = os.environ.get("MCP_SERVERS")
    if not mcp_urls_env:
        print("[warn] No se encontró MCP_SERVERS en variables de entorno. No se cargarán tools.")
        mcp_urls = []
    else:
        mcp_urls = [u.strip() for u in mcp_urls_env.split(",") if u.strip()]
            
    mcp_tools = await gather_tools_from_urls(mcp_urls)
    if not mcp_tools:
        print("[error] No se obtuvieron tools desde ningun MCP. Revisar servidores.")
    else:
        await write_tools(mcp_tools)

    #Setup Agent
    _agent = get_agent(mcp_tools, llm)
    _agent_ctx = Context(_agent)
    print("[info] Agent inicializado. Endpoint /api/agent listo.")



@app.post("/load_file")
def load_file(file: UploadFile = File(...)):
    file_time = str(time.time())
    temp_path = os.path.join(UPLOAD_DIR, file_time)
    os.makedirs(temp_path, exist_ok=True)
    file_path = os.path.join(temp_path, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if (not validate_pfd(file_path)):
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            raise HTTPException(status_code=400, detail="El archivo enviado no es un pdf valido")

        return {"file_time": file_time}
    except Exception as e:
        # limpieza en caso de cualquier excepción inesperada
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
        try:
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
        except OSError:
            pass
        try:
            if os.path.isdir(temp_path) and not os.listdir(temp_path):
                os.rmdir(temp_path)
        except OSError:
            pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            file.file.close()
        except Exception:
            pass


def validate_pfd(file_path):
    return file_path.lower().endswith(".pdf") and os.path.getsize(file_path) > 0

def validate_file(file_name): #Por ahora solo PDFs
    upload_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(upload_path):
        raise HTTPException(status_code=404, detail=f"El archivo a procesar no existe ({upload_path})")
    files = os.listdir(upload_path)
    if len(files) != 1:
        raise HTTPException(status_code=400, detail="Error al intentar procesar el archivo, intente cargarlo nuevamente.")
    file_path = os.path.join(upload_path, files[0])
    if (not validate_pfd(file_path)):
        raise HTTPException(status_code=400, detail="El archivo enviado no es un pdf valido")
    
    return file_path


@app.post("/api/agent")
async def api_agent(req: MessageRequest, file_name: Optional[str] = None):
    
    global _agent, _agent_ctx
    if _agent is None or _agent_ctx is None:
        raise HTTPException(status_code=500, detail="Agent no inicializado aún o no hay tools cargadas.")

    user_query = req.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="El campo 'message' no puede estar vacío.")
    
    inicio = time.time()
    if (file_name!=None):

        file_path = validate_file(file_name)

        extracted_text = pdf_to_text(file_path)
        user_query = f"""
            Sos un asistente que responde preguntas usando texto proporcionado.

            TEXTO DEL DOCUMENTO:
            -------------------
            {extracted_text}
            -------------------

            PREGUNTA:
            {user_query}
            """
        print(f"Tiempo transcurrido en la extraccion del texto del pdf: {inicio-time.time():.4f} segundos")

    try:
        if (not KEEP_CONTEXT):
            _agent_ctx = Context(_agent)
        response = await handle_user_message(user_query, _agent, _agent_ctx, verbose=True)
        print(f"Tiempo total transcurrido: {inicio-time.time():.4f} segundos")
        return {"response": response}
    
    except Exception as e:
        print("[error] Al procesar la petición:", e)
        raise HTTPException(status_code=500, detail=str(e))
