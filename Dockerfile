FROM python:3.7.5-buster

WORKDIR /app

RUN pip3 install --upgrade pip setuptools

RUN pip3 install cython numpy scipy

RUN apt-get update
RUN apt-get install libsndfile1-dev -y

ADD requirements.txt .
ADD audearch-config.toml .

# requirements.txtにリストされたPythonパッケージをインストールする
RUN pip3 install -r requirements.txt

COPY ./audearch-web/ /app/

CMD [ "python3", "run.py" ]