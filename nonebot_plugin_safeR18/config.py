from nonebot import get_plugin_config, get_driver
from pydantic import BaseModel


class ScopedConfig(BaseModel):
    save_path: str = "./data/safeR18"


class Config(BaseModel):
    SafeR18: ScopedConfig = ScopedConfig()


global_config = get_driver().config
plugin_config = get_plugin_config(Config).SafeR18
