import logging


from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import simpleobsws

from interfaces.Config import Config

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

logger = logging.Logger(__name__)


class ChatOBS:
    ws: simpleobsws.WebSocketClient | None = None
    config: Config
    chat: Chat | None = None
    twitch: Twitch | None = None

    def __init__(self, config: Config):
        self.config = config

    async def main(self):
        """
        Main asyncio function
        >>>  asyncio.run(my_chatobs.main())
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

        logger.info("Connecting to OBS...")
        self.ws = simpleobsws.WebSocketClient(
            url=self.config["obs_url"], password=self.config["secret_obs_password"]
        )
        await self.ws.connect()  # Make the connection to obs-websocket
        await self.ws.wait_until_identified()  # Wait for the identification handshake to complete
        try:
            input("press ENTER to stop\\n")
        finally:
            # now we can close the chat bot and the twitch api client
            self.chat.stop()
            await self.twitch.close()

    async def activate_object(self, target_object_name: str):
        pass

    async def get_object_scene_uuids(self) -> list[str]:
        pass

    async def get_object_scene_activation_state(self, object_uuid) -> bool:
        pass

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
        if self.ws:
            await self.ws.disconnect()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        return self.close()
