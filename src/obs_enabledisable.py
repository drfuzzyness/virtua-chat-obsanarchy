import typing
import logging
import asyncio

from simpleobsws import WebSocketClient, Request, RequestResponse

from interfaces import obs_types

logger = logging.getLogger(__name__)


class ObsEnableDisableConfig(typing.TypedDict):
    """
    OBS specific configuration
    """

    obs_url: str
    secret_obs_password: str
    target_object_names: list[str]


class TargetSceneItemState:
    name: str
    scene_item: obs_types.SceneItem
    filter_list: obs_types.GetSourceFilterList
    color_filter: obs_types.ColorKeyFilterV2
    is_active: bool

    def __str__(self):
        return str(
            {
                "name": self.name,
                "scene_item": self.scene_item,
            }
        )


class ObsEnableDisable:
    ws: WebSocketClient | None = None
    config: ObsEnableDisableConfig
    current_scene_uuid: str
    retry_sec = 5
    target_object_names: list[str]

    def __init__(self, config: ObsEnableDisableConfig):
        self.config = config
        self.target_object_names = self.config["target_object_names"]

    async def begin(self) -> None:
        """
        Begins OBS connection
        """
        logger.info("Connecting to OBS...")
        self.ws = WebSocketClient(
            url=self.config["obs_url"], password=self.config["secret_obs_password"]
        )

        try:
            await self.ws.connect()
            logger.info("Waiting for OBS identification handshake...")
            await self.ws.wait_until_identified()
        except ConnectionRefusedError:
            logger.error("Failed to connect to OBS %s", self.config["obs_url"])
            logger.info("Waiting for retry %isec", self.retry_sec)
            await asyncio.sleep(self.retry_sec)
            return await self.begin()

        self.ws.register_event_callback(
            self._on_switchscenes, "CurrentProgramSceneChanged"
        )
        scene = await self.get_current_scene()
        self.current_scene_uuid = scene["sceneUuid"]
        logger.info("Connected to OBS")

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
        scene_list = await self._get_scene_item_list()
        items: TargetSceneItemState = []

        # Fetch the target objects from the items in the current scene
        # logger.debug("Finding objects in scene: %s", self.target_object_names)
        for target in self.target_object_names:
            new_item = TargetSceneItemState()
            new_item.name = target
            new_item.scene_item = self._find_sceneitem(scene_list, object_name=target)
            items.append(new_item)
            # logger.debug("activate_object: new_item=%s", new_item)
        filters = await self._batch_get_object_filters(
            map(lambda x: x.scene_item["sourceUuid"], items)
        )

        # Apply the filter objects to the correct items
        for index, item in enumerate(items):
            item.filter_list = filters[index]
            enabled, color_filter = self._is_object_active(item.filter_list)
            item.is_active = enabled
            item.color_filter = color_filter

        # Activate only the correct items
        for item in items:
            self._set_object_active(item.color_filter, item.name == target_object_name)

        # Send the changes back
        logger.debug("Sending filter changes to OBS")
        await self._batch_set_object_filters(
            map(lambda x: (x.scene_item["sourceUuid"], x.color_filter), items)
        )

    async def _get_scene_item_list(self) -> obs_types.GetSceneItemList:
        response = await self.ws.call(
            Request("GetSceneItemList", {"sceneUuid": self.current_scene_uuid})
        )
        return response.responseData

    def _is_object_active(
        self,
        filter_list: obs_types.GetSourceFilterList,
    ) -> tuple[bool, obs_types.ColorKeyFilterV2 | None]:
        # logger.debug("_is_object_active: %s", filter_list)
        try:
            first_color_filter = next(
                (
                    filter
                    for filter in filter_list["filters"]
                    if filter["filterKind"] == "color_key_filter_v2"
                ),
                None,
            )
            if first_color_filter:
                return (
                    first_color_filter["filterSettings"].get("opacity", 1.0) > 0.9,
                    first_color_filter,
                )
            return False, None
        except ValueError as exception:
            logger.warning(exception)
            return False, None

    def _set_object_active(
        self, color_filter: obs_types.ColorKeyFilterV2, active: bool
    ):
        color_filter["filterSettings"]["opacity"] = 1.0 if active else 0.0

    async def _batch_get_object_filters(
        self, object_uuids: typing.Iterable[str]
    ) -> list[obs_types.GetSourceFilterList | None]:
        batch_response: list[RequestResponse] = await self.ws.call_batch(
            map(
                lambda uuid: Request("GetSourceFilterList", {"sourceUuid": uuid}),
                object_uuids,
            )
        )
        # logger.debug("_batch_get_object_filters: %s", batch_response)
        responses = []
        for response in batch_response:
            if response.requestStatus.comment:
                logger.error(
                    "_batch_get_object_filters: %s", response.requestStatus.comment
                )
            responses.append(response.responseData)
        return responses

    async def _batch_set_object_filters(
        self, objects: typing.Iterable[tuple[str, obs_types.ColorKeyFilterV2]]
    ) -> list[obs_types.GetSourceFilterList | None]:
        requests = []
        for uuid, color_filter in objects:
            requests.append(
                Request(
                    "SetSourceFilterSettings",
                    {
                        "sourceUuid": uuid,
                        "filterName": color_filter["filterName"],
                        "filterSettings": color_filter["filterSettings"],
                    },
                )
            )
        batch_response: list[RequestResponse] = await self.ws.call_batch(requests)
        # logger.debug("_batch_set_object_filters: %s", batch_response)
        for response in batch_response:
            if response.requestStatus.comment:
                logger.warning(
                    "_batch_set_object_filters: %s", response.requestStatus.comment
                )

    def _find_sceneitem(
        self,
        scene_list: obs_types.GetSceneItemList,
        object_name: str | None = None,
        object_uuid: str | None = None,
    ):
        # logger.debug(
        #     'Seeking Item (object_name="%s", object_uuid="%s")',
        #     object_name,
        #     object_uuid,
        # )
        if object_uuid is not None:
            items = [
                item
                for item in scene_list["sceneItems"]
                if item["sourceUuid"] == object_uuid
            ]
        else:
            items = [
                item
                for item in scene_list["sceneItems"]
                if item["sourceName"] == object_name
            ]
        count = len(items)
        if count > 1:
            raise ValueError(f"Too many OBS objects {object_name or object_uuid} found")
        if count < 1:
            raise ValueError(f"No OBS objects {object_name or object_uuid} found")
        return items[0]

    async def close(self):
        """Code to cleanup the app once finished"""
        if self.ws:
            await self.ws.disconnect()
