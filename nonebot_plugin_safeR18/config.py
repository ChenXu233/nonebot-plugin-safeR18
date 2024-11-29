from typing import Optional
from nonebot import get_plugin_config, get_driver
from pydantic import BaseModel


class ScopedConfig(BaseModel):
    save_path: Optional[str] = None

class Config(BaseModel):
    safer18: ScopedConfig = ScopedConfig()


global_config = get_driver().config
plugin_config = get_plugin_config(Config).safer18
