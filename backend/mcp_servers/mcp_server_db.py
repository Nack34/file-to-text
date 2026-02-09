# mcp_servers/server_db.py
import argparse
from mcp.server.fastmcp import FastMCP
import psycopg

server = FastMCP("DBTools", port=21000, host="0.0.0.0")

def get_connection():
    conn = psycopg.connect(
        host="db",
        port=5432,
        dbname="mcp_database",
        user="admin",
        password="admin123"
    )
    return conn

#Podria hacer una tool por cada instruccion sql pero queria probar inicialmente si de esta forma funciona bien.
@server.tool()
def execute_query(query: str) -> str:
    """
    Ejecuta una consulta SQL de tipo (INSERT | DELETE | UPDATE) en la base de datos y devuelve los resultados.

    Ejemplo:
        >>> execute_query("INSERT INTO users (username, password_hash) VALUES ('Juan', 'clave1234');")
        
    """

    query_upper = query.strip().upper()

    if not query_upper.startswith(("INSERT", "UPDATE", "DELETE")):
        return "Solo se permiten queries de escritura"

    try :
        conn = get_connection() #Funcion que crea la conexion a la base de datos
        cursor = conn.cursor() #Crea el cursor
        cursor.execute(query) #Ejecuta la consulta
        
        conn.commit()
        affected = cursor.rowcount

        cursor.close() #Cierra el cursor
        conn.close() #Cierra la conexion
        return f"filas afectadas: {affected}"
    except Exception as e:
        return f"Error al ejecutar la consulta: {e}"


@server.tool()
def get_users(query : str = "SELECT * FROM users;") -> str:
    """
    Realiza una consulta SQL de tipo (SELECT) a la base de datos.
    
    Ejemplo:
        >>> get_users("SELECT * FROM users WHERE age > 30;")
        
    """
    query_upper = query.strip().upper()

    if not query_upper.startswith("SELECT"):
        return "Solo se permiten SELECT"

    try :
        conn = get_connection() #Funcion que crea la conexion a la base de datos
        cursor = conn.cursor() #Crea el cursor
        cursor.execute(query) #Ejecuta la consulta
        results = cursor.fetchall() #Obtiene los resultados
        cursor.close() #Cierra el cursor
        conn.close() #Cierra la conexion
        return str(results)
    except Exception as e:
        return f"Error al ejecutar la consulta: {e}"


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