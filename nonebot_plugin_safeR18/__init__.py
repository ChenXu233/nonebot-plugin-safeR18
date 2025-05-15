import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from nonebot import get_driver, require
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from nonebot.message import event_postprocessor
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from PIL import Image

require("nonebot_plugin_localstore")
require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")
from nonebot_plugin_localstore import get_plugin_data_dir
from nonebot_plugin_uninfo import Session, get_session

from .config import Config, plugin_config
from .model import BaseModel, RestNet50Model, YOLOV11Model
from .utils import ensure_file_from_github, get_images

__plugin_meta__ = PluginMetadata(
    name="涩涩保存器",
    homepage="https://github.com/ChenXu233/nonebot-plugin-safeR18",
    description="保存涩涩图片的插件",
    usage="插上就用",
    type="application",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    config=Config,
    extra={},
)

MODEL: BaseModel

driver = get_driver()


@driver.on_startup
async def _():
    logger.info("正在检查模型文件是否存在")
    await ensure_file_from_github()


if plugin_config.model == "yolo-V11":
    MODEL = YOLOV11Model()
elif plugin_config.model == "resnet-50":
    MODEL = RestNet50Model()


@event_postprocessor
async def save_images(
    bot: Bot,
    event: Event,
    imgs: List[Image.Image] = Depends(get_images),
    session: Session = Depends(get_session),
):
    if not imgs:
        return
    if not plugin_config.save_path:
        dir = get_plugin_data_dir()
    else:
        dir = Path(plugin_config.save_path)
    for i in imgs:
        if MODEL.is_R18(i):
            name = session.user.id + str(datetime.now().timestamp())
            img_id = uuid.uuid5(uuid.NAMESPACE_DNS, name)
            img_name = f"{img_id}.jpg"
            save_dir = dir / img_name
            i.save(save_dir)
            logger.info(f"发现色图！已保存到{save_dir}")
        else:
            logger.info("未发现色图")
