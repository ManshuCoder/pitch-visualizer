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
        """Splits a paragraph into a list of sentences using NLTK."""
        if not text:
            return []
        
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]

if __name__ == "__main__":
    parser = TextParser()
    sample_text = "A futuristic city uses drones for delivery. A young girl watches a drone land on her balcony. She receives a mysterious package."
    sentences = parser.split_into_sentences(sample_text)
    for i, sent in enumerate(sentences):
        print(f"Scene {i+1}: {sent}")
