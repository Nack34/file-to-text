import argparse
from mcp.server.fastmcp import FastMCP

server = FastMCP("Saludo", port=21000, host="0.0.0.0")

@server.tool()
def greet(name: str) -> str:
    """
    Saluda a la persona con el nombre dado.

    Ejemplo:
        >>> greet("Juan")
        'Hola, Juan!'
    """
    return f"Hola, {name}!"

@server.tool()
def un_poema_de_amor() -> str:
    """
    Devuelve un poema de amor corto.

    Ejemplo:
        >>> un_poema_de_amor()
        'Eres la luz en mi oscuridad,
         el latido de mi corazón,
         mi amor por ti es infinito,
         mi dulce inspiración.'
    """
    return (
        "Eres la luz en mi oscuridad,\n"
        "el latido de mi corazón,\n"
        "mi amor por ti es infinito,\n"
        "mi dulce inspiración."
    )

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
