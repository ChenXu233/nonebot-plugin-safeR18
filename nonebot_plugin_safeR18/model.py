import abc
import os
from PIL import Image

from pathlib import Path
from torchvision import transforms, models
import torch
from torch import nn
from torch.autograd import Variable

from nonebot import logger
from .config import plugin_config


class BaseModel(abc.ABC):
    def __init__(self):
        self.model = None
        self.classes = ["drawings", "hentai", "neutral", "porn", "sexy"]

    @abc.abstractmethod
    def predict(self, image: Image.Image) -> dict:
        raise NotImplementedError("Subclasses must implement this method")

    def is_R18(self, image: Image.Image) -> bool:
        """
        判断图片是否为R18
        :param image: 图片
        :return: 是否为R18
        """
        result = self.predict(image)
        return max(result.items(), key=lambda x: x[1])[0] in ["porn", "hentai", "sexy"]


class RestNet50Model(BaseModel):
    def __init__(self):
        test_transforms = transforms.Compose(
            [
                transforms.Resize(224),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.model = models.resnet50()
        self.model.fc = nn.Sequential(  # type: ignore
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 10),
            nn.LogSoftmax(dim=1),
        )
        current_script_path = os.path.abspath(__file__)
        path = Path(current_script_path)
        model_path = path.parent / "models/ResNet50_nsfw_model.pth"

        self.model.load_state_dict(
            torch.load(
                os.path.abspath(model_path),
                map_location=torch.device("cpu"),
                weights_only=True,
            )
        )
        self.model.eval()

    def predict(self, image: Image.Image) -> dict:
        with torch.inference_mode():
            image_tensor = self.test_transforms(image).float()  # type: ignore
            image_tensor = image_tensor.unsqueeze_(0)
            if torch.cuda.is_available():
                image_tensor.cuda()
            input = Variable(image_tensor)
            output = self.model(input)
            index = output.data.numpy()
            logger.debug(index)
            index = index[0][:5]
            logger.debug(index)
            logger.debug(output.data.numpy().argmax())
            return {self.classes[i]: index[i] for i in range(5)}


class YOLOV11Model(BaseModel):
    def __init__(self):
        self.model = None
        self.threshold = 0.5
