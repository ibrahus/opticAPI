import logging
import os
import shutil
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import tempfile
from typing import Tuple
import replicate
from deep_translator import GoogleTranslator
from gtts import gTTS
from dotenv import load_dotenv

# Setup environment and logger
load_dotenv()  # This automatically finds the .env file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure APIRouter and constants
router = APIRouter()
TRANSLATOR = GoogleTranslator(source='en', target='ar')
MODEL = "yorickvp/llava-13b:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591"


@router.get("/health")
async def health():
    return {"status": "ok"}


def remove_file(file_path: str):
    try:
        os.remove(file_path)
        logger.info(f"Successfully deleted {file_path}")
    except OSError as e:
        logger.error(f"Failed to delete {file_path}: {e}")


async def save_upload_file(upload_file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(upload_file.file, temp_file)
        temp_file_path = temp_file.name
    return temp_file_path


async def process_image(file_path: str, prompt: str) -> Tuple[str, str]:
    with open(file_path, "rb") as image_file:
        output = replicate.run(
            MODEL, input={"image": image_file, "prompt": prompt})
    full_description = "".join(output)
    translation = TRANSLATOR.translate(full_description)
    return full_description, translation


async def create_audio_file(translation: str) -> str:
    tts = gTTS(text=translation, lang='ar')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp:
        tts.save(temp.name)
    return temp.name


@router.post("/chat-with-image")
async def chat_with_image(background_tasks: BackgroundTasks, file: UploadFile = File(...), prompt: str = ""):
    try:
        file_path = await save_upload_file(file)
        full_description, translation = await process_image(file_path, prompt)
        audio_file_path = await create_audio_file(translation)
        response = FileResponse(
            audio_file_path, media_type="audio/mpeg", filename=os.path.basename(audio_file_path))
        # Schedule the file to be deleted after the response
        background_tasks.add_task(remove_file, audio_file_path)
        return response
    except Exception as e:
        logger.error(
            f"An error occurred during processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        remove_file(file_path)
        await file.close()


@router.post("/chat-with-image-test")
async def chat_with_image_test(file: UploadFile = File(...), prompt: str = ""):
    try:
        file_path = await save_upload_file(file)
        full_description, translation = await process_image(file_path, prompt)

        audio_file_path = await create_audio_file(translation)

        response_data = {
            "audio_url": os.path.basename(audio_file_path),
            "text": full_description,
            "translated_text": translation,
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(
            f"An error occurred during processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        remove_file(file_path)
        await file.close()


@router.get("/download/{filename}")
async def download_audio(background_tasks: BackgroundTasks, filename: str):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    if os.path.isfile(file_path):
        response = FileResponse(
            path=file_path, media_type='audio/mpeg', filename=filename)
        background_tasks.add_task(remove_file, file_path)
        return response
    else:
        raise HTTPException(status_code=404, detail="File not found.")
