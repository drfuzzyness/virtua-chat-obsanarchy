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

    async def begin(self):
        """
        Begins OBS connection
        """
        logger.info("Connecting to OBS...")
        self.ws = simpleobsws.WebSocketClient(
            url=self.config["obs_url"], password=self.config["secret_obs_password"]
        )
        await self.ws.connect()
        logger.info("Waiting for identification handshake...")
        await self.ws.wait_until_identified()

    async def activate_object(self, target_object_name: str):
        pass

    async def get_object_scene_uuids(self) -> list[str]:
        pass

    async def get_object_scene_activation_state(self, object_uuid) -> bool:
        pass

    async def close(self):
        """Code to cleanup the app once finished"""
        if self.ws:
            await self.ws.disconnect()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        return self.close()
