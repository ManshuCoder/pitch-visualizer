import os
import nltk

class TextParser:
    def __init__(self):
        # Set NLTK data path to /tmp which is writable on Vercel
        nltk_data_path = os.path.join("/tmp", "nltk_data")
        if nltk_data_path not in nltk.data.path:
            nltk.data.path.append(nltk_data_path)
            
        if not os.path.exists(nltk_data_path):
            os.makedirs(nltk_data_path, exist_ok=True)

        # Ensure NLTK data is downloaded to the writable path
        try:
            nltk.data.find('tokenizers/punkt', paths=[nltk_data_path])
        except LookupError:
            nltk.download('punkt', download_dir=nltk_data_path)
        
        try:
            nltk.data.find('tokenizers/punkt_tab', paths=[nltk_data_path])
        except LookupError:
            nltk.download('punkt_tab', download_dir=nltk_data_path)

    def split_into_sentences(self, text):
        """
        Splits a paragraph into a list of sentences.
        Enhanced to handle newlines and commas if typical sentence 
        structure (periods) is missing.
        """
        if not text:
            return []
        
        # 1. Try standard NLTK sentence tokenization
        sentences = nltk.sent_tokenize(text)
        
        # 2. If we only got 1 sentence but text is long, try splitting by newlines
        if len(sentences) <= 1:
            sentences = [s.strip() for s in text.split('\n') if s.strip()]
            
        # 3. If still only 1 "sentence" and it has many commas, 
        # it's likely a descriptive list. Split by comma to create scenes.
        if len(sentences) <= 1 and text.count(',') >= 2:
            # We split by comma but group bits together so scenes aren't TOO short
            parts = [p.strip() for p in text.split(',') if p.strip()]
            new_scenes = []
            # Group every 2-3 descriptors into a scene if needed, 
            # but for a pitch, every major comma break is usually a scene.
            sentences = parts

        # Final cleanup and limit
        final_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        # Ensure we have at least something
        return final_sentences if final_sentences else [text]

if __name__ == "__main__":
    parser = TextParser()
    sample_text = "A futuristic city uses drones for delivery. A young girl watches a drone land on her balcony. She receives a mysterious package."
    sentences = parser.split_into_sentences(sample_text)
    for i, sent in enumerate(sentences):
        print(f"Scene {i+1}: {sent}")
