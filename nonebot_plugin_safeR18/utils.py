import ssl
from io import BytesIO
from typing import List

import httpx
from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna.uniseg import Image, Reference, UniMsg
from PIL import Image as Img

from .config import plugin_config

HTTPX_CLIENT = None

ssl_context = ssl.create_default_context()
ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # 降低安全级别以兼容老旧服务器


async def get_httpx_client():
    global HTTPX_CLIENT
    if HTTPX_CLIENT is None:
        HTTPX_CLIENT = httpx.AsyncClient(verify=ssl_context)  # Disable SSL verification
    return HTTPX_CLIENT


async def get_images(msg: UniMsg, event: Event, bot: Bot) -> List[Img.Image]:
    """
    获取event内所有的图片并以字典方式返回
    """
    img_urls = []
    images: List[Img.Image] = []
    for i in msg:
        if isinstance(i, Reference):
            forward = await bot.call_api("get_forward_msg", id=i.id)
            for j in forward["messages"]:
                for k in j["message"]:
                    if k["type"] == "image":
                        img_url = k["data"]["url"]
                        img_urls.append(img_url)
        elif isinstance(i, Image):
            img_url = i.data["url"]
            img_urls.append(img_url)

    for img_url in img_urls:
        async with await get_httpx_client() as client:
            r = await client.get(img_url)
            img = Img.open(BytesIO(r.content))
            images.append(img)

    logger.debug(f"获取到图片：{len(images)}")

    return images
