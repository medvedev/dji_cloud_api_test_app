import os
import sys

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

required_env_vars = ["MQTT_HOST_ADDR", "MQTT_USERNAME", "MQTT_PASSWORD", "DJI_LICENSE", "DJI_APP_KEY"]

missing_vars = [var for var in required_env_vars if os.getenv(var) is None]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

host_addr = os.environ["MQTT_HOST_ADDR"]

app = FastAPI()

@app.get("/login")
async def pilot_login():
    file_path = "./couldhtml/login.html"
    with open(file_path, 'r') as file:
        file_content = (file.read()
                        .replace("%mqtt_hostname%", host_addr)
                        .replace("%mqtt_user_login%", os.environ["MQTT_USERNAME"])
                        .replace("%mqtt_user_password%", os.environ["MQTT_PASSWORD"])
                        .replace("%dji_license%", os.environ["DJI_LICENSE"])
                        .replace("%dji_appkey%", os.environ["DJI_APP_KEY"]))
    return HTMLResponse(file_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == "__main__":
    uvicorn.run(app, host=host_addr, port=5000)
