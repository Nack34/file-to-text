(prueba2) PS C:\Users\sueyr\OneDrive\Desktop\Joako\Trabajo\agentes\prueba2> uv run .\ollama_client.py
greet 
Escribe tu mensaje: Hola soy Joaquin, usa la tool 
User:  Hola soy Joaquin, usa la tool
Agent:  No sé.

Escribe tu mensaje: Hola soy Joaquin             
User:  Hola soy Joaquin
Agent:  No sé.

Escribe tu mensaje: usa la tool con un valor aleatorio 
User:  usa la tool con un valor aleatorio
Agent:  No sé.

Escribe tu mensaje: usa la tool con un valor aleatorio
User:  usa la tool con un valor aleatorio
Agent:  No sé.

Escribe tu mensaje: usa la tool 'greet' con un valor aleatorio 
User:  usa la tool 'greet' con un valor aleatorio
--
debug
Tool greet respondio con tool_name='greet' tool_kwargs={'name': 'Joaquin'} tool_id='greet' tool_output=ToolOutput(blocks=[TextBlock(block_type='text', text="meta=None content=[TextContent(type='text', text='Hola, Joaquin!', annotations=None, meta=None)] structuredContent={'result': 'Hola, Joaquin!'} isError=False")], tool_name='greet', raw_input={'args': (), 'kwargs': {'name': 'Joaquin'}}, raw_output=CallToolResult(meta=None, content=[TextContent(type='text', text='Hola, Joaquin!', annotations=None, meta=None)], structuredContent={'result': 'Hola, Joaquin!'}, isError=False), is_error=False) return_direct=False

Agent:  Hola, Joaquin!

Escribe tu mensaje:


server.py

           server.py:713
INFO:     127.0.0.1:54085 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:54087 - "POST /messages/?session_id=99b4364489e3471c86c712e185a93be2 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:54087 - "POST /messages/?session_id=99b4364489e3471c86c712e185a93be2 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:54087 - "POST /messages/?session_id=99b4364489e3471c86c712e185a93be2 HTTP/1.1" 202 Accepted
[12/22/25 22:36:41] INFO     Processing request of type ListToolsRequest                                                                 server.py:713                                                                  
INFO:     127.0.0.1:54089 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:54091 - "POST /messages/?session_id=4cccda3250254aed8e6f9603370ac7d4 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:54091 - "POST /messages/?session_id=4cccda3250254aed8e6f9603370ac7d4 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:54091 - "POST /messages/?session_id=4cccda3250254aed8e6f9603370ac7d4 HTTP/1.1" 202 Accepted
                    INFO     Processing request of type ListToolsRequest                                                                 server.py:713                                                                  
INFO:     127.0.0.1:56395 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:61625 - "POST /messages/?session_id=e9280410231541adbcd675c79e2cb23a HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:61625 - "POST /messages/?session_id=e9280410231541adbcd675c79e2cb23a HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:61625 - "POST /messages/?session_id=e9280410231541adbcd675c79e2cb23a HTTP/1.1" 202 Accepted
[12/22/25 22:37:48] INFO     Processing request of type    server.py:713
                             ListToolsRequest                           
INFO:     127.0.0.1:61627 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:61629 - "POST /messages/?session_id=068d5503ac2d4862a831f43345b869f9 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:61629 - "POST /messages/?session_id=068d5503ac2d4862a831f43345b869f9 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:61629 - "POST /messages/?session_id=068d5503ac2d4862a831f43345b869f9 HTTP/1.1" 202 Accepted
[12/22/25 22:37:49] INFO     Processing request of type    server.py:713
                             ListToolsRequest                           
INFO:     127.0.0.1:52840 - "GET /sse HTTP/1.1" 200 OK
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
[12/22/25 22:38:39] INFO     Processing request of type    server.py:713                                                      
                             CallToolRequest                   
INFO:     127.0.0.1:52842 - "POST /messages/?session_id=3fcd72564d86403e86719b3cfb6872e8 HTTP/1.1" 202 Accepted
                    INFO     Processing request of type    server.py:713                                                      
                             ListToolsRequest                  
