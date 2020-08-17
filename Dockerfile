FROM python:3.7.5-buster

WORKDIR /app

RUN pip3 install --upgrade pip setuptools

RUN pip3 install cython numpy scipy

ADD requirements.txt .
ADD audearch-config.ini .

# requirements.txtにリストされたPythonパッケージをインストールする
RUN pip3 install -r requirements.txt

COPY ./audearch-web/ /app/

CMD [ "python3", "run.py" ]