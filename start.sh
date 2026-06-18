#!/bin/bash
# Zeabur 启动脚本
PORT=${PORT:-8080}
uvicorn main:app --host 0.0.0.0 --port $PORT
