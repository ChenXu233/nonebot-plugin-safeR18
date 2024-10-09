import os
import httpx
from io import BytesIO
from PIL import Image
from typing import Dict
from pathlib import Path
from torchvision import transforms, models

import torch
from torch import nn
from torch.autograd import Variable

from nonebot import logger
from nonebot.adapters import Event

CLASSES = ["drawings", "hentai", "neutral", "porn", "sexy"]

test_transforms = transforms.Compose(
    [
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)
model = models.resnet50()
model.fc = nn.Sequential( # type: ignore
    nn.Linear(2048, 512),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(512, 10),
    nn.LogSoftmax(dim=1),
)
current_script_path = os.path.abspath(__file__)
path = Path(current_script_path)
model_path = path.parent / "models/ResNet50_nsfw_model.pth"

model.load_state_dict(
    torch.load(os.path.abspath(model_path), map_location=torch.device("cpu"),weights_only=True)
)
model.eval()
# TODO :异步优化图片获取


async def get_images(event: Event) -> Dict[int, Image.Image]:
    """
    获取event内所有的图片并以字典方式返回
    """
    try:
        msg_images = event.message["image"]  # type: ignore
    except AttributeError:
        return {}
    images: dict[int, Image.Image] = {}
    for idx, seg in enumerate(msg_images):
        url = seg.data["url"]
        r = httpx.get(url)
        if r.status_code != 200:
            logger.error(f"Cannot fetch image from {url} msg#{event.message_id}")  # type: ignore
            continue
        images[idx] = Image.open(BytesIO(r.content))
    return images


def R18_rate(img: Image.Image) -> Dict[str, float]:
    """
    获取图片R18评分
    """
    with torch.inference_mode():
        image_tensor = test_transforms(img).float()  # type: ignore
        image_tensor = image_tensor.unsqueeze_(0)
        if torch.cuda.is_available():
            image_tensor.cuda()
        input = Variable(image_tensor)
        output = model(input)
        index = output.data.numpy()
        logger.debug(index)
        index = index[0][:5]
        logger.debug(index)
        logger.debug(output.data.numpy().argmax())
    return {CLASSES[i]: index[i] for i in range(5)}


def is_R18(img: Image.Image) -> bool:
    """
    判断图片是否为R18
    """
    rate = R18_rate(img)
    max_item = max(rate.items(), key=lambda x: x[1])
    if max_item[0] == "hentai" or max_item[0] == "porn" or max_item[0] == "sexy":
        return True
    return False


if __name__ == "__main__":
    image = Image.open("./test.jpg")
    R18_rate(image)
