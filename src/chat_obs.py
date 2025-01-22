import logging


from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

from interfaces.Config import Config

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

logger = logging.Logger(__name__)


async def _on_message(msg: ChatMessage):
    """
    Whenever anyone sends a message in chat, this is called. If this bot sends a message, this will be called
    """
    logger.info('Room %s: "%s": "%s"', msg.room.name, msg.user.name, msg.text)


async def main(config: Config):
    twitch = await Twitch(
        config["secret_twitch_app_id"], config["secret_twitch_app_secret"]
    )
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    # this will be called when the event READY is triggered, which will be on bot start
    async def on_ready(ready_event: EventData):
        logger.debug("Bot is ready for work, joining channels")
        await ready_event.chat.join_room(config["twitch_channel"])

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, _on_message)

    chat.start()
    try:
        input("press ENTER to stop\\n")
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()
