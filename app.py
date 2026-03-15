import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

from text_parser import TextParser
from prompt_engine import PromptEngine
from image_generator import ImageGenerator

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pitch Visualizer - Stability Edition")

# Add CORS middleware with explicit Vercel support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pitch-visualizer-p6h8.vercel.app", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Handle favicon and root issues
@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})

# Determine if we are on a production-like environment (Vercel or Render)
IS_PRODUCTION = os.environ.get("VERCEL") == "1" or os.environ.get("RENDER") == "true"

# ALWAYS use /tmp for generated assets in production for reliability
# Use local static folder only for local development
OUTPUT_DIR = os.path.join("/tmp", "generated_images") if IS_PRODUCTION else os.path.join("static", "generated_images")

# Ensure directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files (for CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the generated images directory (mapping both local and cloud paths to /generated)
app.mount("/generated", StaticFiles(directory=OUTPUT_DIR), name="generated")

templates = Jinja2Templates(directory="templates")

# Initialize modules
parser = TextParser()
engine = PromptEngine()
# Pass the unified OUTPUT_DIR to the generator
generator = ImageGenerator(output_dir=OUTPUT_DIR)

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
    print(f"Received request for storyboard: {request.text[:50]}...")
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please enter a paragraph of at least 3-5 sentences.")

    # 1. Sentence Segmentation
    try:
        sentences = parser.split_into_sentences(request.text)
    except Exception as e:
        print(f"Text parsing error: {e}")
        sentences = [request.text] # Fallback to whole text
    
    if not sentences:
        sentences = [request.text]

    # Limit to 5 scenes
    sentences = sentences[:5]
    scenes = []
    
    # Static Reliable Fallback Images (Ensures storyboard always works)
    fallbacks = [
        "https://images.unsplash.com/photo-1614850523296-d8c1af93d400?auto=format&fit=crop&w=1024&q=80", # Cyber / Abstract
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1024&q=80", # Tech / Retro
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1024&q=80", # Space / Future
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1024&q=80", # Robotics
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1024&q=80"  # Motherboard
    ]

    for i, sentence in enumerate(sentences):
        enhanced_prompt = engine.enhance_prompt(sentence)
        filename = f"scene_{i+1}_{os.urandom(4).hex()}.png"
        
        try:
            # Try Real AI Generation
            image_filename = generator.generate(enhanced_prompt, filename)
            image_url = f"/generated/{image_filename}"
        except Exception as e:
            print(f"⚠️ API Error on scene {i+1}: {e}")
            # Use Fallback URL directly to ensure the UI is beautiful
            image_url = fallbacks[i % len(fallbacks)]
            enhanced_prompt = f"Note: Using themed fallback because API is unavailable. (Original: {enhanced_prompt})"

        scenes.append({
            "image": image_url,
            "caption": sentence,
            "prompt": enhanced_prompt
        })

    return {"scenes": scenes}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
