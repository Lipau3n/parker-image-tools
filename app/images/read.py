from dataclasses import dataclass
from fractions import Fraction
from io import BytesIO
from typing import Any, Dict, Tuple

from PIL import ExifTags, Image as PILImage


@dataclass
class ImageMeta:
    format: str
    width: int
    height: int
    file_size: int
    file_size_mb: str
    exif: Dict = None


class ImageExif:
    """
    Read EXIF data from image.
    Use class property TAGS to filter EXIF tags in response.
    """

    TAGS: Tuple[str] = (
        'Make',
        'Model',
        'LensMake',
        'LensModel',

        'Software',
        'DateTime',  # Date of export, e.g. from Adobe Lightroom
        'OffsetTime',
        'DateTimeOriginal',  # Date of shoot
        'OffsetTimeOriginal',
        'XResolution',
        'YResolution',

        'ShutterSpeedValue',  # 35mm equiv values
        'ApertureValue',  # 35mm equiv value
        'FocalLength',  # 35mm equiv value
        'FocalLengthIn35mmFilm',  # Converted value if sensor size is smaller or bigger than 35 mm
        'ExposureBiasValue',
        'ExposureTime',
        'FNumber',
        'ISOSpeedRatings',
    )

    _data: Dict[str, Any]  # TODO: convert ANY to concrete data types

    def __init__(self, image: PILImage.Image):
        self.image = image
        self._data = self._read()

    def _read(self) -> Dict[str, Any]:
        data = {}
        for k, v in self.image._getexif().items():
            tag = ExifTags.TAGS[k]
            if not tag or tag not in self.TAGS:
                continue
            data[tag] = str(v)
        data.update(self._custom_calc(data))
        data = {k: v for k, v in sorted(data.items())}
        return data

    @staticmethod
    def _custom_calc(data: Dict) -> Dict[str, Any]:
        """ Calculate here custom image properties, like human-understandable shutter speed value """
        if 'ExposureTime' in data.keys():
            et = float(data.get('ExposureTime', 0))
            ss = Fraction(et).limit_denominator()
            data['_ExposureTime'] = str(ss)
        return data

    def get(self):
        return self._data


class ImageRead:
    """
    Read information about image including EXIF data
    """
    uploaded_image: BytesIO
    image: PILImage.Image
    meta: ImageMeta
    _size: int = 0

    def __init__(self, file: BytesIO, size: int = 0):
        self._size = size
        file.seek(0)
        self.image = PILImage.open(file)

    def read(self) -> ImageMeta:
        self.meta = ImageMeta(
            format=self.image.format,
            width=self.image.width,
            height=self.image.height,
            file_size=self._size,
            file_size_mb='%.2f' % (self._size / 10 ** 6),
            exif=ImageExif(self.image).get(),
        )
        return self.meta
