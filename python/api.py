# api.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
from pydantic import BaseModel
import yaml
import os
import secrets

from generate_config_multi import update_and_reload_config


app = FastAPI()
security = HTTPBasic()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

class Node(BaseModel):
    proxy: str
    port: int

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/nodes", response_model=List[Node], dependencies=[Depends(verify_credentials)])
def get_nodes():
    config_path = "/app/mihomo/config/config_multi.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        listeners = config.get('listeners', [])
        nodes = [{'proxy': listener['proxy'], 'port': listener['port']} for listener in listeners]
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", dependencies=[Depends(verify_credentials)])
def read_root():
    return {"message": "API 正在运行。"}

@app.get("/refresh", dependencies=[Depends(verify_credentials)])
def refresh_config():
    try:
        update_and_reload_config()
        return {"message": "配置已刷新。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
