from functools import wraps


class TelegramBot:

    def __init__(self, token):
        self.token = token


def send_action(action):
    """Sends typing action while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(self, update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(self, update, context,  *args, **kwargs)
        return command_func

    return decorator
