import base64
import io
import logging
import os
from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from gtts import gTTS
import requests


router = APIRouter()

# Setup environment and logger
load_dotenv()  # This automatically finds the .env file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_openai_headers():
    return {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }


async def process_image_with_gpt4_vision(upload_file: UploadFile, prompt: str) -> str:
    try:
        image_data = await upload_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        prompt = prompt or "Describe the image in Arabic language"

        logger.info(f"prompt: {prompt}")

        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}, {
                    "type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]},
            ],
            "max_tokens": 300
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=get_openai_headers(), json=data)
        response.raise_for_status()
        output = response.json()
        return output['choices'][0]['message']['content']
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        raise


def generate_tts_audio(text, lang='ar'):
    """Generator function to yield audio chunks from gTTS."""
    tts = gTTS(text=text, lang=lang)
    with io.BytesIO() as audio_buffer:
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        while chunk := audio_buffer.read(1024):
            yield chunk


@router.post("/chat-with-image-gpt4")
async def chat_with_image_gpt4_vision(file: UploadFile = File(...),
                                      prompt: str = ""):
    try:
        full_description = await process_image_with_gpt4_vision(file, prompt)

        # response = requests.post("https://api.openai.com/v1/audio/speech", headers=get_openai_headers(
        # ), json={"model": "tts-1", "input": full_description, "voice": "onyx"})
        # response.raise_for_status()
        # return StreamingResponse(response.iter_content(chunk_size=1024 * 1024), media_type="audio/mpeg")

        # Stream the TTS response
        return StreamingResponse(generate_tts_audio(full_description), media_type="audio/mpeg")

    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        raise HTTPException(status_code=500, detail=str(http_err))
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()
