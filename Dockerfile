# ベースイメージ
FROM python:3.13-slim

# 環境変数の設定（非対話的インストール）
ENV DEBIAN_FRONTEND=noninteractive

# 必要なパッケージをインストール（日本語フォント + 依存ツール）
RUN apt-get update && \
    apt-get install -y \
    fonts-ipafont-gothic \
    fonts-noto-cjk \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの作成
WORKDIR /app

# 必要ファイルのコピー
COPY requirements.txt ./
COPY app.py ./

# Pythonパッケージのインストール
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Streamlitを実行
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
