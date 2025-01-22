import typing


class Config(typing.TypedDict):
    """
    All app configuration that needs to be set ahead of time
    """

    secret_twitch_app_id: str
    secret_twitch_app_secret: str
    twitch_channel: str
