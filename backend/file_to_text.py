import base64
import os
import sys
import shutil
import tempfile
from pdf2image import convert_from_path
from openai import OpenAI

OLLAMA_URL = os.environ.get("OLLAMA_URL")
MODEL = os.environ.get("MODEL")
API_KEY = os.environ.get("API_KEY")

def encode_image_to_data_url(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/jpeg;base64,{b64}" 

def pdf_to_images(pdf_path, dpi=150): 
    tmpdir = tempfile.mkdtemp(prefix="pdf_images_")
    pages = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, page in enumerate(pages):
        img_path = os.path.join(tmpdir, f"page_{i+1}.jpg")
        page.save(img_path, "JPEG", quality=80)
        image_paths.append(img_path)
    return image_paths, tmpdir

def ocr_single_image(img_path, client):
    data_url = encode_image_to_data_url(img_path)
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extraé el texto de esta página respetando el formato."},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=2000, 
    )
    return resp.choices[0].message.content

def images_to_text(image_paths):
    client = OpenAI(
        api_key=API_KEY,
        base_url=OLLAMA_URL
    )
    
    full_text = []
    print(f"--- Procesando {len(image_paths)} páginas con {MODEL} ---")

    for i, img_path in enumerate(image_paths):
        try:
            print(f"Procesando página {i+1}...")
            page_text = ocr_single_image(img_path, client)
            full_text.append(f"--- PÁGINA {i+1} ---\n{page_text}")
        except Exception as e:
            print(f"Error en página {i+1}: {e}", file=sys.stderr)
            continue 
            
    return "\n\n".join(full_text)

def pdf_to_text(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Archivo no encontrado: {pdf_path}", file=sys.stderr)
        return ""

    image_paths, tmpdir = pdf_to_images(pdf_path, dpi=150)
    
    try:
        text = images_to_text(image_paths)
    finally:
        shutil.rmtree(tmpdir)

    return text