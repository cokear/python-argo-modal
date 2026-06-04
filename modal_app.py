import os
import subprocess
import modal

app = modal.App("data-analysis-api")

image = (
    modal.Image.debian_slim()
    .pip_install("aiohttp", "h2", "protobuf")
    .add_local_file("main.py", remote_path="/root/app/main.py")
    .add_local_file("index.html", remote_path="/root/app/index.html")
)

@app.function(
    image=image,
    min_containers=1,   
    timeout=86400
)
@modal.web_server(port=3000)
def start_web_service():
    os.chdir("/root/app")
    os.environ["PORT"] = "3000"
    
    print("[INFO] Starting data API service on port 3000...")
    print("[INFO] Loading analytical models...")
    
    subprocess.run(["python", "main.py"])
