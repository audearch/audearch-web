import time

from audearch.analyzer import analyzer
from audearch.database import MongodbFactory
from fastapi import FastAPI, File, UploadFile
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from cruds import music_metadata_register, music_register
from schemas import MusicData, MusicMetadata

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

    music_id = int(str(time.time())[-6:])

    file_object = files.file
    list_landmark = analyzer(file_object)

    title = "test"
    duration = 0

    music = MusicData(music_id, list_landmark)
    music_meta = MusicMetadata(music_id, title, duration)

    music_register(imongo, music)
    music_metadata_register(imongo, music_meta)

    return {"music_id": music_id}


@app.get('/upload')
def upload(request: Request):
    return templates.TemplateResponse('upload.html', {'request': request})
