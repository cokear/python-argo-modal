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


@fastapi_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE
