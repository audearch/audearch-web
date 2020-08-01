FROM python:3.7.5-slim

WORKDIR /app

RUN pip install --upgrade pip  

ADD setup.py .
ADD setup.cfg .

# requirements.txtにリストされたPythonパッケージをインストールする
RUN python3 setup.py install

ADD audearch-web/ .
# FastAPIを8000ポートで待機

RUN python audearch-web/run.py