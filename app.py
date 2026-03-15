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

    # 1. Sentence Segmentation (Lazy Load inside parser)
    try:
        sentences = parser.split_into_sentences(request.text)
    except Exception as e:
        print(f"Text parsing error: {e}")
        raise HTTPException(status_code=500, detail="Error splitting text into sentences.")
    
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
            # Both Vercel and Render will now use the /generated mount point
            image_url = f"/generated/{image_filename}"
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
