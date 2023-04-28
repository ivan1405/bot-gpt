import openai


class OpenAIClient:

    def __init__(self, openai_org, openai_key):
        openai.organization = openai_org
        openai.api_key = openai_key

    def send_message(self, message):
        """Send a message to Chat-GPT for completion

            This is the basic functionality that sends a message to Chat-GPT and 
            expects a response to start a new conversation

            Args:
                message (srt): The message to send

            Returns:
                str: The completion message returned by Chat-GPT
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            #model="gpt-3.5-turbo",
            #max_tokens=150,
            temperature=0.7,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response['choices'][0]['message']['content']

    def generate_image_from_text(self, message):
        """Generates a picture based on a text

            This uses OpenAI integration with Dall-E to generate a picture
            based on the description used as input

            Args:
                message (str): The message to generate a picture from

            Returns:
                str: The url of picture generated
        """
        response = openai.Image.create(
            prompt=message,
            n=1,
            size="512x512",
        )
        return (response['data'][0].url)

    def speech_to_text(self, audio_file):
        """Converts a voice file into text

            This function receives an audio file (normally in mp3 format) and
            converts it into text using OpenAI APIs

            Args:
                audio_file (File): The audio file that has to be converted into text

            Returns:
                str: The text message generated from the voice message
        """
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']

    def translate_audio(self, audio_file):
        """Translates a voice message to english

            This function receives an audio file in any language and translates it into english

            Args:
                audio_file (File): The audio file that has to be translated

            Returns:
                str: The text message translated from the voice message
        """
        translation = openai.Audio.translate("whisper-1", audio_file)
        return translation['text']

    def create_moderation(self, text):
        """Moderates a text

            This function receives a text and extract topics related to its moderation,
            like 'violence', 'sexual', 'self-harm' etc

            Args:
                text (str): The input text to be moderated

            Returns:
                str: The list of categories extracted from the text or a successful response if message is ok
        """
        moderation_result = openai.Moderation.create(
            input=text, model='text-moderation-latest')
        if moderation_result['results'][0]['flagged']:
            categories_list = moderation_result['results'][0]['categories']
            response = dict(filter(self._extract_positive_categories, categories_list.items()))
            return ",".join(response.keys())
        else: 
            return 'All good with this message :)'

    def fix_spelling_mistakes(self, text):
        """Fix spelling mistakes

            This function receives a text with gramatical errors and returns the same text but corrected

            Args:
                text (str): The input text to be corrected

            Returns:
                str: The corrected text
        """
        result = openai.Edit.create(
            model="text-davinci-edit-001",
            input=text,
            instruction="Fix the spelling mistakes"
        )
        return result['choices'][0]['text']

    def _extract_positive_categories(self, categories):
        result = []
        key, value = categories
        if value:
            result.append(key)
        return result