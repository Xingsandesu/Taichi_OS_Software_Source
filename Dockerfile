FROM python:3.10.13-slim-bookworm
LABEL authors="Fushin"


# 设置工作目录
WORKDIR /app

# 复制应用
COPY . /app

# 安装依赖

RUN pip install -r requirements.txt

EXPOSE 10010

# 入口命令
CMD ["python", "app.py"]