import requests, os


class ElevenLabsClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def text_to_speech(self, text, voice_id):
        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/{}".format(voice_id)

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v1",
            "voice_settings": {
                "stability": 0.8,
                "similarity_boost": 0.8
            }
        }

        response = requests.post(url, json=data, headers=headers)
        try:
            os.makedirs("./tmp/elevenlabs")
        except FileExistsError:
            # directory already exists
            pass
        with open('tmp/elevenlabs/output.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
