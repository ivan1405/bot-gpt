import os
import logging
import traceback
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters
)
# https://github.com/jiaaro/pydub#installation
from pydub import AudioSegment
from open_ai.openai_client import OpenAIClient
from telegram_bot.bot import TelegramBot, send_action


class ChatGptBot(TelegramBot):

    def __init__(self, token, openai_org, openai_key):
        super().__init__(token)
        self.openai = OpenAIClient(openai_org, openai_key)
        self.logger = self._init_logger()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="""
                Hey {}, this is Chat GPT! \n\nI'm a bot powered with the most advanced artificial intelligence available. \n\nHow can I help you?
            """.format(user.first_name)
        )

    @send_action(ChatAction.TYPING)
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = self.openai.send_message(message=update.message.text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    @send_action(ChatAction.UPLOAD_PHOTO)
    async def generate_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = ' '.join(context.args)
        img_url = self.openai.generate_image_from_text(message=text)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url)

    @send_action(ChatAction.TYPING)
    async def speech_to_text(self, update: Update, context: CallbackContext):
        voice_file = await context.bot.getFile(update.message.voice.file_id)
        voice_file_mp3 = await self._read_and_convert_voice_message(voice_file, 'mp3')
        transcript = self.openai.speech_to_text(voice_file_mp3)
        answer_chat_gpt = self.openai.send_message(transcript)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_chat_gpt)

    @send_action(ChatAction.TYPING)
    async def translate_audio(self, update: Update, context: CallbackContext):
        voice_file = await context.bot.getFile(update.message.voice.file_id)
        voice_file_mp3 = await self._read_and_convert_voice_message(voice_file, 'mp3')
        transcript = self.openai.translate_audio(voice_file_mp3)
        answer_chat_gpt = self.openai.send_message(transcript)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer_chat_gpt)

    async def photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive("picture.jpg")
        self.logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
        await update.message.reply_text(
            "Amazing picture {}! I'd love to describe it, but this functionality is not yet supported... :( ".format(
                user.first_name)
        )

    @send_action(ChatAction.TYPING)
    async def moderation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = ' '.join(context.args)
        response = self.openai.create_moderation(text=text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    @send_action(ChatAction.TYPING)
    async def fix_spelling(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = ' '.join(context.args)
        response = self.openai.fix_spelling_mistakes(text=text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    # supuestamente esto manda una imagen

    def send_about(self, update: Update, context: CallbackContext) -> None:
        context.bot.send_document(chat_id=update.message['chat']['id'], document=open(
            'about.png', 'rb'), filename='about.png')

    @send_action(ChatAction.TYPING)
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    @send_action(ChatAction.TYPING)
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.logger.error(msg="Exception while handling an self, update:",
                          exc_info=context.error)
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__)
        error_message = "Wooops, it looks like there was an error:{}".format(
            tb_list[-1].rsplit(':', 1)[1])
        await context.bot.send_message(chat_id=update.message['chat']['id'], text=error_message)

    def start_bot(self):
        application = ApplicationBuilder().token(self.token).build()

        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler(
            'generate_image', self.generate_image))
        application.add_handler(CommandHandler('moderation', self.moderation))
        application.add_handler(CommandHandler(
            'fix_spelling', self.fix_spelling))

        application.add_handler(MessageHandler(
            filters.TEXT & (~filters.COMMAND), self.echo))
        application.add_handler(MessageHandler(filters.COMMAND, self.unknown))
        application.add_handler(MessageHandler(filters.PHOTO, self.photo))
        application.add_handler(MessageHandler(
            filters.VOICE, self.speech_to_text))

        application.add_error_handler(self.error_handler)

        application.run_polling()

    async def _read_and_convert_voice_message(self, voice_file_id: str, dest_format: str):
        try:
            os.makedirs("./tmp")
        except FileExistsError:
            # directory already exists
            pass
        await voice_file_id.download_to_drive('./tmp/voice_message.ogg')
        voice_file_ogg = AudioSegment.from_ogg('./tmp/voice_message.ogg')
        voice_file_ogg.export(
            './tmp/voice_message.{}'.format(dest_format), format=dest_format)
        return open('./tmp/voice_message.{}'.format(dest_format), 'rb')

    def _init_logger(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        return logging.getLogger(__name__)