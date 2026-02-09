import base64
import requests
from pdf2image import convert_from_path
import tempfile
import os
import shutil
import sys
from ollama import Client


OLLAMA_URL = os.environ.get("OLLAMA_URL")
MODEL = os.environ.get("MODEL")

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def pdf_to_images(pdf_path, dpi=300):
    tmpdir = tempfile.mkdtemp(prefix="pdf_images_")
    pages = convert_from_path(pdf_path, dpi=dpi, output_folder=tmpdir)
    image_paths = []
    for i, page in enumerate(pages):
        img_path = os.path.join(tmpdir, f"page_{i+1}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)
    return image_paths, tmpdir

def ocr_images(image_paths, client, timeout=300):
    resp = client.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": "Extraé TODO el texto del documento. Mantené el orden de lectura y respetá saltos de línea.",
            "images": image_paths
        }]
    )
    print(resp)
    message_content = resp.message.content 

    return message_content

def images_to_text(image_paths):
    #Setup llm Ollama
    client = Client(host=OLLAMA_URL)

    try:
        text = ocr_images(image_paths, client)
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a Ollama ({OLLAMA_URL}): {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(3)
    return text

def pdf_to_text(pdf_path):
    if not pdf_path:
        print(f"No se encontró ningún .pdf en '{pdf_path}'.", file=sys.stderr)
        sys.exit(1)

    image_paths, tmpdir = pdf_to_images(pdf_path)
    text = images_to_text(image_paths)

    try:
        shutil.rmtree(tmpdir)
    except Exception:
        pass

    return text
