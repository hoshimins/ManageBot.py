FROM python:3

WORKDIR /app/bot

RUN apt-get install locales && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

# 仮想環境の構築
RUN python -m venv /src/venv
# 仮想環境の起動
RUN source /src/venv/bin/activate
# pip のアップデート
RUN pip install --upgrade pip
# パッケージのインストール
RUN pip install --nocache-dir -r requirements.txt

# ファイルのコピー
COPY . /app/bot

# 起動
CMD ["python", "/app/bot/src/main.py"]