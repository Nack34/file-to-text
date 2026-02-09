--------------------No usar-----------------------
### Crear entorno virtual
 - uv .venv
 - Activar
    - .venv\Scripts\activate 

### Sincronizar dependencias
 - uv sync

### Uso:
 - uv run uv run server.py --server_type=sse
 - uv run uv run .\ollama_client.py
------------------------------------------
### Crear la imagen
 - docker build -t mcp_prueba .

### Levantar el contenedor
 #- docker compose run mcp_client (No usar)
 - docker compose up -d mcp_client