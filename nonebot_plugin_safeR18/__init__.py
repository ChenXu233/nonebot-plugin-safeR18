from nonebot import on_message
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent

from .functions import str2img, luckycola_api
from .config import plugin_config

safeR18 = on_message(priority=plugin_config.safeR18_priority)


@safeR18.handle()
async def _saving_img(matcher: Matcher, event: MessageEvent, bot: Bot):
    for i in event.message:
        if i.type == "image":
            image, name = await str2img(i.data["file"])
            if await luckycola_api(image):
                with open(plugin_config.safeR18_storage_path / name, "xb") as f:
                    f.write(image.getvalue())
