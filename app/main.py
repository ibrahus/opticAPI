from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database import init_db
from app.llava import api as llava
from app.gpt4 import api as gpt4

app = FastAPI()

# Define startup event handler
async def startup():
    await init_db()

# Define shutdown event handler
async def shutdown():
    # Perform any cleanup or shutdown tasks here
    pass

# Register the event handlers
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

# Set up CORS middleware options
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llava.router)
app.include_router(gpt4.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
