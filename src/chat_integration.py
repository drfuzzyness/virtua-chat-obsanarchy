import asyncio
import logging
import typing
import pathlib
import os.path

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
import platformdirs

USER_SCOPE = [AuthScope.CHAT_READ]

logger = logging.getLogger(__name__)


class TriggerCallback(typing.Protocol):
    async def __call__(self, message: ChatMessage):
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

    async def begin(self):
        """
        Main asyncio function
        >>>  asyncio.run(my_chat.main())
        """
        logger.debug("Creating local OAuth storage...")
        twitch_auth_file_dir = pathlib.Path(
            os.path.join(
                platformdirs.user_config_dir(
                    "drfuzzyness", "virtua_chat_obsanarchy", ensure_exists=True
                ),
                "twitch.json",
            )
        )
        twitch_auth_file_dir.touch()

        logger.debug("Setting up Twitch OAuth Handling in %s...", twitch_auth_file_dir)
        self.twitch = await Twitch(
            self.config["secret_twitch_app_id"], self.config["secret_twitch_app_secret"]
        )
        helper = UserAuthenticationStorageHelper(
            self.twitch,
            USER_SCOPE,
            storage_path=pathlib.PurePath(twitch_auth_file_dir),
        )
        logger.info("Authenticating to Twitch...")
        await helper.bind()

        logger.info("Connecting to Twitch Chat...")
        self.chat = await Chat(self.twitch)

        self.chat.register_event(ChatEvent.READY, self._on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self._on_message)

        self.chat.start()

    async def _on_message(self, msg: ChatMessage):
        """
        Whenever anyone sends a message in chat, this is called. If this bot sends a message, this will be called
        """
        logger.debug('%s: "%s": "%s"', msg.room.name, msg.user.name, msg.text)
        tasks = []

        for [matcher, callback] in self.triggers:
            if matcher.match(msg.text):
                tasks.append(callback(msg))

        await asyncio.gather(*tasks)

    async def _on_ready(self, ready_event: EventData):
        await ready_event.chat.join_room(self.config["twitch_channel"])
        logger.info("Connected to Twitch Chat")

    async def close(self):
        """Code to cleanup the app once finished"""
        if self.chat and self.chat.is_connected():
            self.chat.stop()
        if self.twitch:
            await self.twitch.close()
