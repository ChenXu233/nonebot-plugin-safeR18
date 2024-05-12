from io import BytesIO
from typing import Dict

import httpx
from nonebot import logger
from nonebot.adapters.onebot.v11.event import MessageEvent
from PIL import Image


async def get_images(event: MessageEvent) -> Dict[int, Image.Image]:
    """
    获取event内所有的图片并以字典方式返回
    """
    msg_images = event.message["image"]
    images: dict[int, Image.Image] = {}
    for idx, seg in enumerate(msg_images):
        url = seg.data["url"]
        r = httpx.get(url)
        if r.status_code != 200:
            logger.error(f"Cannot fetch image from {url} msg#{event.message_id}")
            continue
        images[idx] = Image.open(BytesIO(r.content))
    return images
