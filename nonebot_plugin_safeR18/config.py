from typing import Literal, Optional

from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel


class ScopedConfig(BaseModel):
    save_path: Optional[str] = None
    model: Literal["yolo-V11-1.0", "resnet-50"] = "yolo-V11-1.0"


class Config(BaseModel):
    safer18: ScopedConfig = ScopedConfig()


global_config = get_driver().config
plugin_config = get_plugin_config(Config).safer18
