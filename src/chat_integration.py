import logging
import typing

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage

USER_SCOPE = [AuthScope.CHAT_READ]

logger = logging.Logger(__name__)


class TriggerCallback(typing.Protocol):
    def __call__(self, message: ChatMessage) -> None:
        pass


type Trigger = tuple[typing.Pattern, TriggerCallback]


class TwitchConfig(typing.TypedDict):
    secret_twitch_app_id: str
    secret_twitch_app_secret: str
    twitch_channel: str


class ChatIntegration:
    config: TwitchConfig
    chat: Chat | None = None
    twitch: Twitch | None = None
    triggers: list[Trigger]

    def __init__(self, config: TwitchConfig, triggers: list[Trigger]):
        self.config = config
        self.triggers = triggers

    async def main(self):
        """
        Main asyncio function
        >>>  asyncio.run(my_chat.main())
        """

        logger.info("Connecting to Twitch...")
        self.twitch = await Twitch(
            self.config["secret_twitch_app_id"], self.config["secret_twitch_app_secret"]
        )
        auth = UserAuthenticator(self.twitch, USER_SCOPE)
        logger.info("Authenticating to Twitch...")
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

        logger.info("Connecting to Twitch Chat...")
        self.chat = await Chat(self.twitch)

        self.chat.register_event(ChatEvent.READY, self._on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self._on_message)

        self.chat.start()

    async def _on_message(self, msg: ChatMessage):
        """
        Whenever anyone sends a message in chat, this is called. If this bot sends a message, this will be called
        """
        logger.info('Room %s: "%s": "%s"', msg.room.name, msg.user.name, msg.text)

    async def _on_ready(self, ready_event: EventData):
        logger.info("Connected to Twitch Chat, joining channel...")
        await ready_event.chat.join_room(self.config["twitch_channel"])

    async def close(self):
        """Code to cleanup the app once finished"""
        if self.chat:
            self.chat.stop()
        if self.twitch:
            await self.twitch.close()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        return self.close()
