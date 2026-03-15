import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

from text_parser import TextParser
from prompt_engine import PromptEngine
from image_generator import ImageGenerator

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pitch Visualizer - Stability Edition")

# Add CORS middleware - simplified for maximum compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine if we are on Vercel
IS_VERCEL = os.environ.get("VERCEL") == "1"

# Set output directory to /tmp if on Vercel, else local static folder
OUTPUT_DIR = os.path.join("/tmp", "generated_images") if IS_VERCEL else os.path.join("static", "generated_images")

# Ensure static directories exist locally (skipped on Vercel since it's read-only)
if not IS_VERCEL:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# If on Vercel, we need to serve the /tmp folder manually or use a different mount
if IS_VERCEL:
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.mount("/generated", StaticFiles(directory=OUTPUT_DIR), name="generated")

templates = Jinja2Templates(directory="templates")

# Initialize modules
parser = TextParser()
engine = PromptEngine()
generator = ImageGenerator()

class StoryboardRequest(BaseModel):
    text: str

@app.get("/health")
def home():
    return {"message": "Pitch Visualizer running"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-storyboard")
async def generate_storyboard(request: StoryboardRequest):
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please enter a paragraph of at least 3-5 sentences.")

    # 1. Sentence Segmentation
    sentences = parser.split_into_sentences(request.text)
    
    if not sentences:
        raise HTTPException(status_code=400, detail="Could not parse sentences from text.")

    # Limit to 5 scenes for safety
    sentences = sentences[:5]
    scenes = []
    
    for i, sentence in enumerate(sentences):
        # 2. Prompt Engineering
        enhanced_prompt = engine.enhance_prompt(sentence)
        
        # 3. Image Generation (Stability AI)
        filename = f"scene_{i+1}_{os.urandom(4).hex()}.png"
        try:
            image_filename = generator.generate(enhanced_prompt, filename)
            # Adjust path for UI
            image_url = f"/generated/{image_filename}" if IS_VERCEL else f"/static/generated_images/{image_filename}"
            scenes.append({
                "image": image_url,
                "caption": sentence,
                "prompt": enhanced_prompt
            })
        except Exception as e:
            print(f"Error generating scene {i+1}: {e}")
            # Show a clear error in the UI for that scene
            scenes.append({
                "image": "https://via.placeholder.com/1024x1024.png?text=Generation+Failed",
                "caption": sentence,
                "prompt": f"Error: {str(e)}"
            })

    return {"scenes": scenes}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
