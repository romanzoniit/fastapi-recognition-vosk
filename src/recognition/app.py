import os.path
from src.recognition.methods import *
from src.recognition.settings import UPLOADED_FILES_PATH, MODELS_FILES_PATH
from fastapi import FastAPI, Response, status, UploadFile, File
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
            wav_parse(file_name, media_type, model, format_type)
        zfile = zipfiles(UPLOADED_FILES_PATH, file_name, normalize_flag)
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
