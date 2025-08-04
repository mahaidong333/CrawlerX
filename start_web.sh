#!/bin/bash

# 启动Web服务
echo "Starting CrawlerX Web Server..."
export FLASK_APP=web/app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000