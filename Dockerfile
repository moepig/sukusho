# ベースイメージを指定
FROM python:3.11-slim-buster

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip

# Chrome Driver のインストール
RUN wget -P /opt/chrome/ https://chromedriver.storage.googleapis.com/111.0.5563.64/chromedriver_linux64.zip 
RUN cd /opt/chrome/ && \
    unzip chromedriver_linux64.zip && \
    rm -f chromedriver_linux64.zip

# Chrome のインストール
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable=111.0.5563.64-1 && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

# 日本語フォントのインストール
RUN apt-get update && \
    apt-get install -y fonts-ipafont

# Pythonのパッケージをインストール
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install chromedriver-binary==111.0.5563.64

# スクリプトをコピー
COPY main.py config.yml /app/

# タイムゾーンを設定
ENV TIME_ZONE Asia/Tokyo

# パスの設定
ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome

# スクリプトを実行
CMD ["python", "main.py"]