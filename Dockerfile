# 使用 Python 3.12 輕量版作為執行環境
FROM python:3.12-slim

# 設定容器內工作目錄
WORKDIR /app

# 複製套件需求檔
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案到容器
COPY . .

# 開放 Flask 預設 port
EXPOSE 5000

# 啟動 Flask 程式
CMD ["python", "app.py"]