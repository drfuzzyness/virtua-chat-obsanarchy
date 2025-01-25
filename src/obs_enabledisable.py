import typing
import logging

import simpleobsws

logger = logging.Logger(__name__)

class ObsEnableDisableConfig(typing.TypedDict):
    """
    OBS specific configuration
    """
    obs_url: str
    secret_obs_password: str
    target_object_names: list[str]

class ObsEnableDisable:
    ws: simpleobsws.WebSocketClient | None = None
    config: ObsEnableDisableConfig

    def __init__(self, config: ObsEnableDisableConfig):
        self.config = config

    async def main(self):
        """
        Main asyncio function
        >>>  asyncio.run(my_chat.main())
        """
        logger.info("Connecting to OBS...")
        self.ws = simpleobsws.WebSocketClient(
            url=self.config["obs_url"], password=self.config["secret_obs_password"]
        )
        await self.ws.connect()
        logger.info("Waiting for identification handshake...")
        await self.ws.wait_until_identified()
