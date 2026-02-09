# mcp_servers/server_wikipedia.py
import argparse
import wikipedia
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

server = FastMCP("WebSearchTools", port=21000, host="0.0.0.0")

@server.tool()
def consultar_articulo_wikipedia(articulo: str) -> str:
    """
        Consulta un articulo de wikipedia y devuelve un resumen del mismo.
        Ejemplo:
            >>> consultar_articulo_wikipedia("Python")
    """
    wikipedia.set_lang("es")
    try:
        resultado = wikipedia.summary(articulo, sentences=3) #Devuelve solo 3 oraciones.
        return resultado
    except wikipedia.DisambiguationError as e:
        return f"Artículo ambiguo: {e.options[:5]}"
    except wikipedia.PageError as e:
        return f"Artículo no encontrado: {e}"


@server.tool()
def consultar_a_un_sitio(
    url: str,
    metodo: str = "GET",
    headers: dict | None = None,
    params: dict | None = None,
    data: dict | None = None,
    max_chars: int = 4000,
    timeout: int = 15
) -> str:
    """
    Consulta un sitio web (HTML) y devuelve el contenido textual relevante.

    Parámetros:
    - url: URL del sitio
    - metodo: GET o POST
    - headers: headers HTTP opcionales
    - params: parámetros de query
    - data: body de la request

    Ejemplo:
        >>> consultar_a_un_sitio("https://google.com")
    """

    try:
        metodo = metodo.upper()

        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; IA-Agent/1.0)"
            }

        response = requests.request(
            method=metodo,
            url=url,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        # Si es HTML limpiar y extraer texto
        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
        else:
            text = response.text

        if len(text) > max_chars:
            text = text[:max_chars]

        return text

    except requests.exceptions.RequestException as e:
        return f"Error al consultar el sitio: {str(e)}"


if __name__ == "__main__":
    # Start the server
    print("🚀Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()

    server.run(args.server_type)
