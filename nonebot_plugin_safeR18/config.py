from nonebot import get_plugin_config
from pydantic import BaseModel, field_validator
from pathlib import Path


class Config(BaseModel):
    safeR18_priority: int = 10
    safeR18_storage_path: Path = Path("./images")

    @field_validator("safeR18_priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v >= 1:
            return v
        raise ValueError("safeR18 priority must greater than 1")

    @field_validator("safeR18_storage_path")
    @classmethod
    def check_safeR18_storage_path(cls, v) -> Path:
        v = Path(v)
        return v


plugin_config = get_plugin_config(Config)
