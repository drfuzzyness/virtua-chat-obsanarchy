import typing
import logging

from simpleobsws import WebSocketClient, Request

from interfaces import obs_types

logger = logging.getLogger(__name__)


class ObsEnableDisableConfig(typing.TypedDict):
    """
    OBS specific configuration
    """

    obs_url: str
    secret_obs_password: str
    target_object_names: list[str]


class ObsEnableDisable:
    ws: WebSocketClient | None = None
    config: ObsEnableDisableConfig
    current_scene_uuid: str

    def __init__(self, config: ObsEnableDisableConfig):
        self.config = config

    async def begin(self):
        """
        Begins OBS connection
        """
        logger.info("Connecting to OBS...")
        self.ws = WebSocketClient(
            url=self.config["obs_url"], password=self.config["secret_obs_password"]
        )
        await self.ws.connect()
        logger.info("Waiting for OBS identification handshake...")
        await self.ws.wait_until_identified()
        self.ws.register_event_callback(
            self._on_switchscenes, "CurrentProgramSceneChanged"
        )
        scene = await self.get_current_scene()
        self.current_scene_uuid = scene["sceneUuid"]

    async def _on_switchscenes(self, event_data: obs_types.CurrentProgramSceneChanged):
        self.current_scene_uuid = event_data["sceneUuid"]
        logger.debug(
            "Active scene changed to %s: %s",
            event_data["sceneName"],
            self.current_scene_uuid,
        )

    async def get_current_scene(self) -> obs_types.GetCurrentProgramScene:
        response = await self.ws.call(Request("GetCurrentProgramScene"))
        return response.responseData

    async def activate_object(self, target_object_name: str):
        pass

    async def get_scene_item_list(self) -> obs_types.GetSceneItemList:
        response = await self.ws.call(
            Request("GetSceneItemList", {"sceneUuid": self.current_scene_uuid})
        )
        return response.responseData

    async def get_object_scene_activation_state(self, object_uuid) -> bool:
        pass

    async def close(self):
        """Code to cleanup the app once finished"""
        if self.ws:
            await self.ws.disconnect()
