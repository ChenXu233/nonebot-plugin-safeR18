from nonebot import get_plugin_config
from pydantic import BaseModel


class SafeR18Config(BaseModel): ...


class Config(BaseModel):
    safeR18: SafeR18Config


plugin_config = get_plugin_config(Config).safeR18
