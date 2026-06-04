import os
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
import httpx
import modal

app = modal.App("data-analysis-api")

image = (
    modal.Image.debian_slim()
    .pip_install("aiohttp", "h2", "protobuf", "grpcio", "psutil", "fastapi", "httpx")
    .add_local_file("main.py", remote_path="/root/app/main.py")
    .add_local_file("index.html", remote_path="/root/app/index.html")
)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    os.chdir("/root/app")
    os.environ["PORT"] = "3000"
    print("[INFO] Loading analytical models... (Starting background Python node)")
    subprocess.Popen(["python", "main.py"])
    yield
    print("[INFO] Shutting down...")

fastapi_app = FastAPI(lifespan=lifespan)

@fastapi_app.api_route(
    "/{path:path}", 
    methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy_to_main(request: Request, path: str):
    url = f"http://127.0.0.1:3000/{path}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                request.method,
                url,
                headers=request.headers,
                data=await request.body(),
                timeout=10.0
            )
            headers = dict(resp.headers)
            headers.pop("content-encoding", None)
            headers.pop("content-length", None)
            return Response(content=resp.content, status_code=resp.status_code, headers=headers)
        except Exception as e:
            return Response(content=f"System initializing... please refresh. (Error: {e})", status_code=503)

@app.function(
    image=image,
    min_containers=1,
    timeout=86400
)
@modal.asgi_app()
def web_server():
    return fastapi_app
