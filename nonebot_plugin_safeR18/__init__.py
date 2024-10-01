import uuid
from typing import Dict
from PIL import Image

from nonebot import require
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.message import event_postprocessor
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_saa")
require("nonebot_plugin_localstore")
require("nonebot_plugin_uninfo")
import nonebot_plugin_saa as saa
from nonebot_plugin_localstore import get_data_dir
from nonebot_plugin_uninfo import get_session, Session

from .utils import get_images, is_R18
from .config import plugin_config, Config

__plugin_meta__ = PluginMetadata(
    name="涩涩保存器",
        homepage="https://github.com/ChenXu233/nonebot-plugin-safeR18",
    description="保存涩涩图片的插件",
    usage="插上就用",
    type="application",
    config=Config,
    extra={},
)


@event_postprocessor
async def save_images(
    event: Event,
    imgs: Dict[int, Image.Image] = Depends(get_images),
    session: Session = Depends(get_session),
):  
    if not imgs:
        return

    dir = get_data_dir("Nonebot-plugin-safeR18")
    for i in imgs.items():
        if is_R18(i[1]):
            name = session.user.id
            img_id = uuid.uuid5(uuid.NAMESPACE_DNS, name)
            img_name = f"{img_id}.jpg"
            save_dir = dir / img_name
            i[1].save(save_dir)
            logger.info(f"发现色图！已保存到{save_dir}")
        else:
            logger.info("未发现色图")
