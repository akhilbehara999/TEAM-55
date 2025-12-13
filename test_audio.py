import os
from gtts import gTTS

# Create audio directory
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Test text-to-speech
text = "Hello, this is a test of the text-to-speech functionality."
tts = gTTS(text, lang='en')
tts.save(os.path.join(AUDIO_DIR, "test.mp3"))

print("Audio file created successfully!")