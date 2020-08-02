FROM python:3.7.5-alpine

WORKDIR /app

RUN apk --update-cache \
    add musl \
    linux-headers \
    gcc \
    g++ \
    make \
    gfortran \
    openblas-dev \
    curl 

RUN pip3 install --upgrade pip setuptools

RUN pip3 install cython numpy scipy

# RUN curl -O "https://github.com/scipy/scipy/releases/download/v1.5.2/scipy-1.5.2-cp37-cp37m-manylinux1_i686.whl"

# RUN pip install scipy-1.5.2-cp37-cp37m-manylinux1_i686.whl

ADD setup.py .
ADD setup.cfg .

# requirements.txtにリストされたPythonパッケージをインストールする
RUN python3 setup.py install

COPY ./audearch-web/ /app/

RUN ls

# FastAPIを8000ポートで待機
CMD [ "python3", "run.py" ]