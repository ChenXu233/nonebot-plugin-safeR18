import ssl
from io import BytesIO
from pathlib import Path
from typing import List

import httpx
from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna.uniseg import Image, Reference, UniMsg
from PIL import Image as Img

HTTPX_CLIENT = None
EXISTS_MODELS_NAMES = [
    "yolo11x-cls_nsfw.pt",
    "ResNet50_nsfw_model.pth",
]

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


async def ensure_file_from_github() -> bool:
    """
    确保指定文件夹下有完整的 filename 文件，否则从 github_url 下载
    """
    folder = Path(__file__).parent / "models"
    for filename in EXISTS_MODELS_NAMES:
        file_path = Path(folder) / filename
        # 判断文件是否存在且大小大于0
        if not file_path.exists() or file_path.stat().st_size == 0:
            logger.info(f"模型文件 {filename} 不存在或大小为0，正在下载...")
            Path(folder).mkdir(parents=True, exist_ok=True)
            try:
                async with await get_httpx_client() as client:
                    # 拼接原始文件直链
                    raw_url = f"https://raw.githubusercontent.com/ChenXu233/nonebot-plugin-safeR18/main/nonebot_plugin_safeR18/models/{filename}"
                    resp = await client.get(raw_url)
                    resp.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(resp.content)
                logger.info(f"已成功下载模型文件: {filename}")
            except Exception as e:
                logger.error(f"下载模型文件 {filename} 失败: {e}")
                return False
    return True
