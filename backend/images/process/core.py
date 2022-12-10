from io import BytesIO
from typing import Tuple
import math

from PIL import (
    Image as PILImage,
    ImageColor,
)


class ImageProcess:
    MODE = 'RGB'

    _file: BytesIO
    image: PILImage.Image
    width: int
    height: int
    _size: Tuple[int, int]
    background: str

    def __init__(self, file: BytesIO,
                 width: int, height: int, background: str,
                 ):
        file.seek(0)
        self._file = file
        self.image = PILImage.open(file)
        self.width = width
        self.height = height
        self._size = (width, height)
        self.background = background

    def get_fit_image_size(self, image_w: int, image_h: int) -> Tuple[int, int]:
        """ Counting image size for fit version of image """
        if image_w >= image_h:
            w_ratio = image_w / self.width
            return self.width, math.ceil(image_h / w_ratio)
        h_ratio = image_h / self.height
        return math.ceil(image_w / h_ratio), self.height

    def get_fit_image(self) -> Tuple[PILImage.Image, Tuple[int, int]]:
        """ Resizing uploaded image to layout and calculate padding from center position """
        w, h = self.get_fit_image_size(self.image.width, self.image.height)
        resized_image = self.image.resize(size=(w, h), resample=PILImage.Resampling.LANCZOS)
        offset = ((self.width - w) // 2, (self.height - h) // 2)
        return resized_image, offset

    def process(self) -> PILImage.Image:
        layout = PILImage.new(mode=self.MODE, size=self._size, color=ImageColor.getrgb(self.background))
        resized_image, offset = self.get_fit_image()
        layout.paste(resized_image, box=offset)
        return layout

    def save(self) -> BytesIO:
        """ Return BytesIO object of processed image """
        output = BytesIO()
        image = self.process()
        image.save(output, format='JPEG', quality=100, optimize=True)
        image.show()
        return output

    def preview(self) -> BytesIO:
        """ Return BytesIO object of processed image preview """
        output = BytesIO()
        image = self.process()
        image.save(output, format='JPEG', quality=80)
        return output
