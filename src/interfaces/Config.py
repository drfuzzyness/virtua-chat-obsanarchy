import typing

from ..obs_enabledisable import ObsEnableDisableConfig
from ..chat_integration import TwitchConfig

class Config(TwitchConfig, ObsEnableDisableConfig):
    """
    All app configuration that needs to be set ahead of time
    """
