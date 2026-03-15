class PromptEngine:
    def __init__(self, global_style="cinematic, ultra detailed, digital art, hyperrealistic, 8k, highly composition"):
        self.global_style = global_style

    def enhance_prompt(self, sentence):
        """
        Converts a sentence into a detailed prompt for Stable Diffusion.
        Adds visual details and cinematic style keywords.
        """
        # Dictionary of scene-specific visual enhancements
        scene_keywords = {
            "city": "futuristic skyline, glowing neon lights, floating structures",
            "drone": "high-tech delivery drone, sleek metallic design, blinking LEDs",
            "girl": "detailed character portrait, expressive face, modern tech-wear",
            "balcony": "overlooking a sprawling metropolis, high altitude sunset",
            "package": "mysterious glowing container, intricate holographic locks",
            "startup": "modern tech office, innovative workspace, creative team",
            "bottle": "sleek ergonomic smart water bottle, premium glass and metal",
            "water": "refreshing liquid drops, splashing, clear hydration",
        }
        
        enhancements = []
        lower_sentence = sentence.lower()
        
        for key, value in scene_keywords.items():
            if key in lower_sentence:
                enhancements.append(value)
        
        # Combine original sentence with enhancements and global style
        if enhancements:
            prompt = f"{sentence}, {', '.join(enhancements)}, {self.global_style}"
        else:
            prompt = f"{sentence}, {self.global_style}"
            
        return prompt

if __name__ == "__main__":
    engine = PromptEngine()
    test_sent = "A futuristic city uses drones for delivery."
    print(f"Original: {test_sent}")
    print(f"Enhanced: {engine.enhance_prompt(test_sent)}")
