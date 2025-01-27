import typing


class CurrentProgramSceneChanged(typing.TypedDict):
    sceneName: str
    sceneUuid: str


class GetCurrentProgramScene(typing.TypedDict):
    sceneName: str
    sceneUuid: str


class SceneItemTransform(typing.TypedDict):
    alignment: int
    boundsAlignment: int
    boundsHeight: float
    boundsType: str
    boundsWidth: float
    cropBottom: int
    cropLeft: int
    cropRight: int
    cropToBounds: bool
    cropTop: int
    height: float
    positionX: float
    positionY: float
    rotation: float
    scaleX: float
    scaleY: float
    sourceHeight: float
    sourceWidth: float
    width: float


class SceneItem(typing.TypedDict):
    inputKind: str
    isGroup: bool
    sceneItemBlendMode: str
    sceneItemEnabled: bool
    sceneItemId: int
    sceneItemIndex: int
    sceneItemLocked: bool
    sceneItemTransform: SceneItemTransform
    sourceName: str
    sourceType: str
    sourceUuid: str


class GetSceneItemList(typing.TypedDict):
    sceneItems: list[SceneItem]


class BaseFilter(typing.TypedDict):
    filterEnabled: bool
    filterIndex: int
    filterKind: str
    filterName: str
    filterSettings: dict[str, typing.Any]


class ColorKeyFilterV2Settings(typing.TypedDict):
    key_color_type: typing.NotRequired[
        typing.Literal["green"]
        | typing.Literal["red"]
        | typing.Literal["blue"]
        | typing.Literal["custom"]
    ]
    key_color: typing.NotRequired[int]
    """The Hex color when using key_color_type: custom"""
    brightness: typing.NotRequired[float]
    opacity: typing.NotRequired[float]
    contrast: typing.NotRequired[float]
    gamma: typing.NotRequired[float]
    similarity: typing.NotRequired[int]
    smoothness: typing.NotRequired[int]


class ColorKeyFilterV2(BaseFilter):
    filterKind: typing.Literal["color_key_filter_v2"]
    filterSettings: ColorKeyFilterV2Settings


class GetSourceFilterList(typing.TypedDict):
    filters: list[ColorKeyFilterV2]
