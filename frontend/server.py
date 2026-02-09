from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import BytesIO
from pydantic import BaseModel
import requests
import os
import mimetypes

BACKEND_URL = os.getenv("BACKEND_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = "output"
os.makedirs(OUTPUT, exist_ok=True)

app = FastAPI()

app.mount(
    "/pdf_to_text/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)
app.mount(
    "/pdf_to_text/scripts",
    StaticFiles(directory=os.path.join(BASE_DIR, "scripts")),
    name="scripts",
)

templates = Jinja2Templates(directory="templates")


@app.get("/pdf_to_text", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/pdf_to_text/send_file")
async def send_file(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        response = requests.post(f"{BACKEND_URL}/load_file", files=files)

        if response.status_code != 200:
            try:
                err_json = response.json()
                return {"error": err_json.get("detail", str(response.text))}
            except:
                return {"error": response.text or response.reason}

        result = response.json()
        return {"file_time": result.get("file_time")}
    
    except requests.RequestException as e:
        return {"error": str(e)}
    
@app.get("/pdf_to_text/proc_file/{file_time}")
def proc_file(file_time: str):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/agent",
            params={"file_name": file_time},
            json={
                "message": (
                    "Convierte el contenido en un JSON limpio y bien estructurado. "
                    "Incluye únicamente información relevante y datos explícitos. "
                    "Elimina explicaciones, comentarios, relleno y cualquier texto que no aporte valor informativo. "
                    "No agregues texto fuera del JSON. "
                )
            }
        )

        if response.status_code != 200:
            try:
                err_json = response.json()
                return {"error": err_json.get("detail", str(response.text))}
            except:
                return {"error": response.text or response.reason}

        result = response.json()

        new_filename = f"{file_time}_res.txt"
        file_path = os.path.join(OUTPUT, new_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.get("response", ""))

        return {"new_filename": new_filename}
    
    except requests.RequestException as e:
        return {"error": str(e)}

@app.get("/pdf_to_text/download_file/{filename}")
def download_file(filename: str):
    try:
        file_path = os.path.join(OUTPUT, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        return StreamingResponse(
            BytesIO(file_bytes),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
