import time

from audearch.analyzer import analyzer
from audearch.database import MongodbFactory
from fastapi import BackgroundTasks, FastAPI, File, UploadFile
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


async def write_hash(files: UploadFile, title: str, music_id: int, duration: int) -> None:
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    file_object = files.file
    list_landmark = analyzer(file_object)

    music = MusicData(music_id, list_landmark)
    music_meta = MusicMetadata(music_id, title, duration)

    music_register(imongo, music)
    music_metadata_register(imongo, music_meta)


def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file/", status_code=201)
async def upload_file(background_tasks: BackgroundTasks, files: UploadFile = File(...)):
    music_id = int(str(time.time())[-6:])

    title = "test"
    duration = 0

    background_tasks.add_task(write_hash, files, title, music_id, duration)

    return {"music_id": music_id}


@app.get('/upload')
def upload(request: Request):
    return templates.TemplateResponse('upload.html', {'request': request})
