# Pitch Visualizer: From Words to Storyboard 🎨

## Project Overview
The **Pitch Visualizer** is an AI-powered service that transforms short narrative paragraphs into cinematic storyboard sequences. By leveraging NLP for text segmentation and state-of-the-art Image Generation models, it allows users to instantly see their ideas brought to life visually.

## Features
- **Sentence Segmentation**: Automatically breaks down paragraphs into meaningful scenes using `spaCy`.
- **Intelligent Prompt Engineering**: Enhances simple sentences into detailed, descriptive prompts for higher quality AI images.
- **AI Image Generation**: Integrated support for Stability AI (SDXL) and OpenAI (DALL-E 3), with a fallback mock system for instant testing.
- **Dynamic Storyboard UI**: A sleek, responsive dashboard to view scenes and their corresponding captions.
- **Cinematic Consistency**: Appends styling markers to ensure generated images maintain a consistent artistic feel.

## Architecture
1. **Frontend**: HTML5, CSS3 (Modern Glassmorphism), JavaScript (Fetch API).
2. **Backend**: FastAPI (Python) for robust API handling.
3. **NLP Module** (`text_parser.py`): Uses `spaCy`'s `en_core_web_sm` model for precise sentence tokenization.
4. **Prompt Engine** (`prompt_engine.py`): Rule-based augmentation logic to add visual depth to text segments.
5. **Image Module** (`image_generator.py`): Handles API interaction and local storage of generated assets.

## Installation

### 1. Prerequisites
- Python 3.9+
- API Keys (Optional but recommended: Stability AI or OpenAI)

### 2. Setup
```bash
# Clone the repository (or navigate to folder)
cd pitch-visualizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Spacy model
python -m spacy download en_core_web_sm
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
STABILITY_API_KEY=your_stability_key_here
OPENAI_API_KEY=your_openai_key_here
```
*(If no keys are provided, the system will use atmospheric technical placeholders for demonstration purposes.)*

### 4. Run the Project
```bash
python app.py
```
Visit `http://localhost:8000` in your browser.

## API Usage
**Endpoint**: `POST /generate-storyboard`
**Input**:
```json
{
  "text": "A startup builds a smart bottle. The app reminds users to drink water."
}
```

## Prompt Engineering Methodology
Our engine uses a multi-layered approach:
1. **Core Subject**: Extracted from the original sentence.
2. **Contextual Expansion**: Rules identify keywords like "startup" or "app" and inject visual descriptors (e.g., "modern office", "clean UI design").
3. **Style Injection**: Global style tokens (e.g., "modern digital art", "4k", "cinematic lighting") are appended to maintain a cohesive storyboard look.

---
*Created for Challenge 2: The Pitch Visualizer.*
