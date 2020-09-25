import hashlib

from audearch.analyzer import librosa_analyzer
from audearch.database import MongodbFactory
from audearch.search import librosa_search
from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
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


async def write_hash(files: UploadFile, title: str, music_id: int, duration: int, size: int) -> None:
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    file_object = files.file
    list_landmark = librosa_analyzer(file_object, size)

    music = MusicData(music_id, list_landmark)
    music_meta = MusicMetadata(music_id, title, duration)

    music_register(imongo, music)
    music_metadata_register(imongo, music_meta)


async def search_music(sfiles: UploadFile, search_hash: str, size: int) -> int:
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    search_file = sfiles.file
    ansid = librosa_search(search_file, size, imongo)

    imongo.update_search_queue(search_hash, ansid)

    return ansid


async def regist_queue(search_hash: str):
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    imongo.add_search_queue(search_hash)


def get_search_queue(search_hash: str):
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    cur = imongo.get_search_queue(search_hash)

    return cur


async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file/", status_code=201)
async def upload_file(background_tasks: BackgroundTasks, files: UploadFile = File(...), music_id: str = Form(...), title: str = Form(...), duration: str = Form(...), size: int = Form(...)):

    background_tasks.add_task(write_hash, files, title, music_id, duration, int(size))

    return {"music_id": music_id}


@app.post("/upload_search_music", status_code=201)
async def upload_search_music(background_tasks: BackgroundTasks, files: UploadFile = File(...), size: int = Form(...)):
    h = hashlib.new('ripemd160')
    regist_queue(str(h.hexdigest))
    background_tasks.add_task(search_music, files, str(h.hexdigest), size)

    return RedirectResponse(f'/search/{h.hexdigest}')


@app.get('search/{search_hash}')
async def search_detail(search_hash: str):
    cur = get_search_queue(search_hash)

    if cur['status'] == 0:
        return "searching"
    elif cur['status'] == 1:
        return str(cur['answer'])
    else:
        return "something went wrong"


@app.get('/upload')
async def upload(request: Request):
    return templates.TemplateResponse('upload.html', {'request': request})


@app.get('/search')
async def search(request: Request):
    return templates.TemplateResponse('search.html', {'request': request})
