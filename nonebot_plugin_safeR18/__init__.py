import os
from typing import Dict
from PIL import Image

from nonebot import on_message, require
from nonebot.params import Depends
from nonebot.adapters.onebot.v11 import MessageEvent

require("nonebot_plugin_nsfw")
from nonebot_plugin_nsfw.deps import detect_nsfw

from .functions import get_images
from .config import plugin_config

safeR18 = on_message(priority=plugin_config.safeR18_priority)


@safeR18.handle()
async def _saving_img(
    event: MessageEvent,
    has_nsfw: bool = Depends(detect_nsfw),
    images: Dict[int, Image.Image] = Depends(get_images),
):
    if not has_nsfw:
        return
    if not os.path.exists(plugin_config.safeR18_storage_path):
        os.makedirs(plugin_config.safeR18_storage_path)
    for index, i in images.items():
        i.save(plugin_config.safeR18_storage_path / f"{event.message_id}-{index}.png")
