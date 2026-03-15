import nltk

class TextParser:
    def __init__(self):
        # Ensure NLTK data is downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        # Workaround for newer NLTK versions/environments
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')

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
