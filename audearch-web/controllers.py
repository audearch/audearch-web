import uuid

from audearch.analyzer import librosa_analyzer
from audearch.database import MongodbFactory
from audearch.search import librosa_search
from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from database import SearchMongodbFactory
from cruds import music_metadata_register, music_register
from schemas import MusicData, MusicMetadata

app = FastAPI(
    title='audearch',
    description='audearch is a audio fingerprinting system',
    version='0.2.0'
)

templates = Jinja2Templates(directory="templates")
jinja_env = templates.env


def write_hash(files: UploadFile, title: str, music_id: int, duration: int, size: int) -> None:
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    file_object = files.file
    list_landmark = librosa_analyzer(file_object, size)

    music = MusicData(music_id, list_landmark)
    music_meta = MusicMetadata(music_id, title, duration)

    music_register(imongo, music)
    music_metadata_register(imongo, music_meta)


def search_music(sfiles: UploadFile, search_hash: str, size: int):
    smongodb = SearchMongodbFactory()
    smongo = smongodb.create()

    imongodb = MongodbFactory()
    imongo = imongodb.create()

    search_file = sfiles.file
    ansid = librosa_search(search_file, size, imongo)

    smongo.update_search_queue(search_hash, ansid)


async def regist_queue(search_hash: str):
    mongodb = SearchMongodbFactory()
    imongo = mongodb.create()

    imongo.add_search_queue(search_hash)


def get_search_queue(search_hash: str):
    mongodb = SearchMongodbFactory()
    imongo = mongodb.create()

    cur = imongo.get_search_queue(search_hash)

    return cur


def get_music_metadata(music_id: int):
    mongodb = MongodbFactory()
    imongo = mongodb.create()

    cur = imongo.find_music_metadata(filter={'music_id': str(music_id)})

    return cur


async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/upload_file/", status_code=201)
async def upload_file(background_tasks: BackgroundTasks, files: UploadFile = File(...), music_id: str = Form(...), title: str = Form(...), duration: str = Form(...), size: int = Form(...)):

    background_tasks.add_task(write_hash, files, title,
                              music_id, duration, int(size))

    return RedirectResponse('/upload-complate')


@app.post("/upload_search_music", status_code=201)
async def upload_search_music(background_tasks: BackgroundTasks, sfiles: UploadFile = File(...), size: int = Form(...)):
    h = str(uuid.uuid4())
    await regist_queue(str(h))
    background_tasks.add_task(search_music, sfiles, str(h), size)

    return RedirectResponse(f'/search/{str(h)}')


@app.get('/search/{search_hash}')
@app.post('/search/{search_hash}')
async def search_detail(request: Request, search_hash: str):
    cur1 = get_search_queue(str(search_hash))
    if cur1 is None:
        return templates.TemplateResponse('search-result.html',
                                          {"request": request,
                                           "id": "None",
                                           "status": "None",
                                           "progress": "None",
                                           "title": "None",
                                           "duration": "None"})
    elif int(cur1['status']) == 0:
        return templates.TemplateResponse('search-result.html',
                                          {"request": request,
                                           "id": "None",
                                           "status": "searching",
                                           "progress": "None",
                                           "title": "None",
                                           "duration": "None"})
    elif int(cur1['status']) == 1:
        cur2 = get_music_metadata(cur1['answer'])
        return templates.TemplateResponse('search-result.html',
                                          {"request": request,
                                           "id": cur1['answer'],
                                           "status": "finish",
                                           "progress": "None",
                                           "title": str(cur2[0]['music_title']),
                                           "duration": cur2[0]['music_duration']})
    else:
        return {"message": "something went wrong"}


@app.get('/upload')
async def upload(request: Request):
    return templates.TemplateResponse('upload.html', {'request': request})


@app.get('/search')
async def search(request: Request):
    return templates.TemplateResponse('search.html', {'request': request})


@app.get('/upload-complate')
@app.post('/upload-complate')
async def upload_complate(request: Request):
    return templates.TemplateResponse('upload-complate.html', {'request': request})
