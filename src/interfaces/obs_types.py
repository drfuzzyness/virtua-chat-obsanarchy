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
