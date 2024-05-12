import io
import re
import base64
import requests
import urllib.request
from typing import Tuple

from nonebot.log import logger


async def str2img(string: str) -> Tuple[io.BytesIO, str]:
    """
    将传入的MessageSegment中的file的字符串转换流文件
    """
    base64_pattern = r"base64://[a-zA-Z0-9+/]+"
    other_pattern = r"(?:http|https)://\S+"
    file_pattern = r"file:///\S+"
    image_bytes = int(0).to_bytes()
    name = None

    if matcher := re.search(base64_pattern, string):

        string = matcher.group()
        string = string.replace("base64://", "")
        name = string[:100] + "png"

        if base64_miss_padding := (4 - len(string) % 4):
            string += "=" * base64_miss_padding
        image_bytes = base64.b64decode(string)

    elif matcher := re.search(other_pattern, string) or (
        matcher := re.search(file_pattern, string)
    ):
        string = matcher.group()
        if name := re.search(r"/[^/]*\.(?:png|jpg|jpeg|gif|bmp)$", string):
            name = name.group()
        image_bytes = urllib.request.urlopen(string).read()

    image = io.BytesIO(image_bytes)
    name = name if name else "?.file"

    return image, name


async def luckycola_api(file: io.BytesIO) -> bool:

    files = {"files": file}
    response = requests.post(url="https://luckycola.com.cn/tools/checkImg", files=files)
    return response.json()["data"]["isSafe"]
