import os
import requests
import base64
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class ImageGenerator:
    def __init__(self, output_dir=None):
        # Default to /tmp for serverless environments (like Vercel)
        if output_dir is None:
            output_dir = os.path.join("/tmp", "generated_images")
            
        self.output_dir = output_dir
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_host = "https://api.stability.ai"
        
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create output dir {self.output_dir}: {e}")

    def generate(self, prompt: str, filename: str) -> str:
        """
        Generates an image using the Stability AI API (Stable Diffusion XL).
        """
        if not self.api_key:
            raise Exception("STABILITY_API_KEY not found in environment variables.")

        print(f"Requesting Stability AI for: {prompt[:50]}...")
        
        url = f"{self.api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        body = {
            "steps": 40,
            "width": 1024,
            "height": 1024,
            "seed": 0,
            "cfg_scale": 7,
            "samples": 1,
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                },
                {
                    "text": "blurry, distorted, low quality, bad anatomy",
                    "weight": -1
                }
            ],
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            raise Exception(f"Stability AI API Error ({response.status_code}): {response.text}")
            
        data = response.json()
        
        filepath = os.path.join(self.output_dir, filename)
        
        for i, image in enumerate(data["artifacts"]):
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image["base64"]))
        
        return filename

if __name__ == "__main__":
    # Test generation
    gen = ImageGenerator()
    try:
        res = gen.generate("A cinematic view of a futuristic city with drones", "test_scene.png")
        print(f"Success! Image saved as {res}")
    except Exception as e:
        print(f"Test failed: {e}")
