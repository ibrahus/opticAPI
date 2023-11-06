import logging
import os
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import replicate
from deep_translator import GoogleTranslator
from gtts import gTTS
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # Read local .env file

router = APIRouter()

logger = logging.getLogger(__name__)

# The root directory for audio files
AUDIO_FILES_DIRECTORY = "audio-files"
TRANSLATOR = GoogleTranslator(source='en', target='ar')
MODEL = "yorickvp/llava-13b:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591"


@router.get("/health")
async def health():
    return {"status": "ok"}


# Helper function to delete a file
def remove_file(file_path: str):
    try:
        os.remove(file_path)
    except OSError as e:
        logger.error(f"Failed to delete {file_path}: {e}")


@router.post("/chat-with-image")
async def chat_with_image(file: UploadFile = File(...), prompt: str = ""):
    # Using 'with' statements ensures proper resource management, especially for I/O operations.
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, file.filename)
            with open(temp_file_path, "wb") as buffer:
                # Directly saving the incoming file data, avoiding reading it into memory.
                buffer.write(await file.read())

            # Avoid reopening the file by keeping it open and passing the file object directly.
            with open(temp_file_path, "rb") as image_file:
                # Not clear what 'replicate' does as it's not a standard library. Assuming it's a third-party service for processing.
                output = replicate.run(
                    MODEL, input={"image": image_file, "prompt": prompt})

            # 'output' is assumed to be a list; if it's not, the join operation will fail.
            full_description = "".join(output)

            translation = TRANSLATOR.translate(full_description)

        tts = gTTS(text=translation, lang='ar')

        # Using 'with' for automatic file handling.
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp:
            # Directly using 'temp.name' as 'tts.save' doesn't require file object, but the name.
            tts.save(temp.name)
            # Storing the file name for the response.
            temp_file_name = temp.name

        return FileResponse(temp_file_name, media_type="audio/mpeg")

    except Exception as e:
        logger.error(
            f"An error occurred during processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred during processing.") from e

    finally:
        # Ensure the file is closed even if an error occurs.
        await file.close()


@router.post("/chat-with-image-test")
async def chat_with_image_test(file: UploadFile = File(...), prompt: str = ""):
    # Using 'with' statements ensures proper resource management, especially for I/O operations.
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file_path = os.path.join(tempdir, file.filename)
            with open(temp_file_path, "wb") as buffer:
                # Directly saving the incoming file data, avoiding reading it into memory.
                buffer.write(await file.read())

            # Avoid reopening the file by keeping it open and passing the file object directly.
            with open(temp_file_path, "rb") as image_file:
                # Not clear what 'replicate' does as it's not a standard library. Assuming it's a third-party service for processing.
                output = replicate.run(
                    MODEL, input={"image": image_file, "prompt": prompt})

            # 'output' is assumed to be a list; if it's not, the join operation will fail.
            full_description = "".join(output)

            translation = TRANSLATOR.translate(full_description)

        tts = gTTS(text=translation, lang='ar')

        os.makedirs(AUDIO_FILES_DIRECTORY, exist_ok=True)
        # Using 'with' for automatic file handling.
        with tempfile.NamedTemporaryFile(delete=False, dir=AUDIO_FILES_DIRECTORY, suffix='.mp3') as temp:
            # Directly using 'temp.name' as 'tts.save' doesn't require file object, but the name.
            tts.save(temp.name)
            # Storing the relative file path for the response.
            relative_file_path = os.path.relpath(
                temp.name, start=AUDIO_FILES_DIRECTORY)

            audio_url = relative_file_path

            response_data = {
                "audio_url": audio_url,
                "text": full_description,
                "translated_text": translation,
            }

            return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(
            f"An error occurred during processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred during processing.") from e

    finally:
        # Ensure the file is closed even if an error occurs.
        await file.close()


# You will need to add an endpoint to serve the audio file if it's not already present
@router.get("/download/{filename}")
async def download_audio(background_tasks: BackgroundTasks, filename: str):
    file_path = os.path.join(AUDIO_FILES_DIRECTORY, filename)
    if os.path.isfile(file_path):
        response = FileResponse(
            path=file_path, media_type='audio/mpeg', filename=filename)

        # Add background task to delete the file after sending the response
        background_tasks.add_task(remove_file, file_path)

        return response
    else:
        raise HTTPException(status_code=404, detail="File not found.")
