import os.path

import rarfile

from recognition.methods import *
from recognition.settings import UPLOADED_FILES_PATH, MODELS_FILES_PATH
from fastapi import FastAPI, Response, status, UploadFile, File, BackgroundTasks
from typing import Optional
from starlette.responses import FileResponse


app = FastAPI()
model = Model(MODELS_FILES_PATH)


@app.get("/api/download", tags=["Download"], status_code=status.HTTP_200_OK)
async def download_file(response: Response,
                        file_name: str,
                        media_type: str
                        ):
    if os.path.exists(UPLOADED_FILES_PATH+file_name):
        file_resp = FileResponse(UPLOADED_FILES_PATH + file_name, media_type=media_type,
                                 filename=file_name)
        response.status_code = status.HTTP_200_OK
        return file_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'File not found'}


@app.get("/api/recognize_rar", tags=["Recognize rar"], status_code=status.HTTP_200_OK)
async def recognize_zip_file(response: Response,
                             file_name: str,
                             archive_type: str,
                             media_type: str,
                             normalize_flag: bool,
                             format_type: bool,
                             ):
    if not os.path.exists(UPLOADED_FILES_PATH+os.path.splitext(file_name)[0]):
        os.mkdir(UPLOADED_FILES_PATH+os.path.splitext(file_name)[0])
    if os.path.exists(UPLOADED_FILES_PATH+file_name and archive_type == "rar"):
        unrar_files(UPLOADED_FILES_PATH+file_name)
        zfile = None
        for f in os.scandir(UPLOADED_FILES_PATH + os.path.splitext(file_name)[0]):
            if f.is_file() and f.path.split('.')[-1].lower() == 'wav':
                wav_parse(os.path.splitext(file_name)[0] + "/" + f.name, media_type, model)
                zipfiles(UPLOADED_FILES_PATH, os.path.splitext(f.name)[0], normalize_flag, file_name)
            zfile = save_all_zip(ARCHIVED_FILES_PATH+os.path.splitext(file_name)[0], f.name, normalize_flag, file_name)
        file_resp = (FileResponse(zfile, media_type="application/x-zip-compressed", filename=zfile))
        response.status_code = status.HTTP_200_OK
        return file_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'File not found'}


@app.get("/api/recognize", tags=["Recognize"], status_code=status.HTTP_200_OK)
async def recognize_file(response: Response,
                         file_name: str,
                         media_type: str,
                         normalize_flag: bool,
                         format_type: bool,
                         ):
    if os.path.exists(UPLOADED_FILES_PATH+file_name):
        if media_type == "mp3":
            mp3_parse(normalize_flag, file_name, media_type, model)
        elif media_type == "wav":
            wav_parse(file_name, media_type, model)
        zfile = zipfiles(UPLOADED_FILES_PATH, file_name, normalize_flag, file_name)
        file_resp = (FileResponse(zfile, media_type="application/x-zip-compressed", filename=zfile))
        response.status_code = status.HTTP_200_OK
        return file_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'File not found'}


@app.post("/api/upload", tags=["Upload"], status_code=status.HTTP_200_OK)
async def upload_file(
        file_id: int,
        name: Optional[str] = None,
        tag: Optional[str] = None,
        file: UploadFile = File(...)
                    ):

    full_name = format_filename(file, file_id, name)
    await save_file_to_uploads(file, full_name)

    return {'file_id': file_id,
            'name': name,
            'tag': tag,
            'file': file
            }


@app.post("/api/uprecognize", tags=["Upload and recognize"], status_code=status.HTTP_200_OK)
async def upload_recognize(
        response: Response,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
                        ):
    full_name = split_filename(file)
    if not is_archive_file(file):
        return {'msg': 'File must be RAR or ZIP format'}
    else:
        await save_file_to_uploads(file, full_name)
    if not os.path.exists(UPLOADED_FILES_PATH+os.path.splitext(full_name)[0]):
        os.mkdir(UPLOADED_FILES_PATH+os.path.splitext(full_name)[0])
    if os.path.exists(UPLOADED_FILES_PATH+full_name) and rarfile.is_rarfile(UPLOADED_FILES_PATH+full_name):
        unrar_files(UPLOADED_FILES_PATH+full_name)
    elif os.path.exists(UPLOADED_FILES_PATH+full_name) and zipfile.is_zipfile(UPLOADED_FILES_PATH+full_name):
        unzip_files(UPLOADED_FILES_PATH+full_name)
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'msg': 'File not found'}
    for f in os.scandir(UPLOADED_FILES_PATH + os.path.splitext(full_name)[0]):
        if f.is_file() and f.path.split('.')[-1].lower() == 'wav':
            wav_parse(os.path.splitext(full_name)[0] + "/" + f.name, "wav", model)
            print(f"Recognize: {f.name}")
    result_file = merge_json_file(os.path.splitext(full_name)[0])
    background_tasks.add_task(delete_files,
                              UPLOADED_FILES_PATH + os.path.splitext(full_name)[0],
                              UPLOADED_FILES_PATH + full_name)
    return FileResponse(result_file, media_type="json",
                        filename=result_file,
                        background=background_tasks)


@app.post("/api/speed", tags=["stats"], status_code=status.HTTP_200_OK)
async def speed(
        response: Response,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
                ):
    full_name = split_filename(file)
    if not is_json_file(file):
        return {'msg': 'File must be json format'}
    else:
        await save_file_to_uploads(file, full_name)
    if not os.path.exists(UPLOADED_FILES_PATH + os.path.splitext(full_name)[0]):
        os.mkdir(UPLOADED_FILES_PATH + os.path.splitext(full_name)[0])
    data = file_to_json_data(UPLOADED_FILES_PATH+full_name)
    result_data = find_speed(data)
    result_file = json_to_file(result_data, UPLOADED_FILES_PATH+full_name)
    background_tasks.add_task(delete_files,
                              UPLOADED_FILES_PATH + os.path.splitext(full_name)[0],
                              UPLOADED_FILES_PATH + full_name)
    return FileResponse(result_file, media_type="json",
                        filename=result_file,
                        background=background_tasks)

