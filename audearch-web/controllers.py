import time

from audearch.analyzer import analyzer
from audearch.database import MongodbFactory
from fastapi import FastAPI, File, UploadFile
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI(
    title='audearch',
    description='audearch is a audio fingerprinting system',
    version='0.2.0'
)

templates = Jinja2Templates(directory="templates")
jinja_env = templates.env


def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file/", status_code=201)
async def upload_file(files: UploadFile = File(...)):
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    id = int(str(time.time())[-6:])

    file_object = files.file
    list_landmark = analyzer(file_object)

    for landmark in list_landmark:
        imongo.insert(id, int(landmark[0]), int(landmark[1]))

    return {"music_id": id}


@app.get('/upload')
def upload(request: Request):
    return templates.TemplateResponse('upload.html', {'request': request})
