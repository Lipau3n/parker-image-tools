from dataclasses import asdict
from io import BytesIO

from fastapi import FastAPI, File, Query
from starlette.responses import StreamingResponse

from images.process.core import ImageProcess
from images.read import ImageRead

app = FastAPI()


@app.get("/")
async def root():
    return "health check"


@app.post("/read/")
async def read(file: bytes = File()):
    size = len(file)
    file = BytesIO(file)
    img = ImageRead(file, size=size)
    return asdict(img.read())


size_q = Query(gt=0, le=7680)
background_q = Query(default='#000000', regex=r'#[0-9A-F]{6}')


@app.post("/export/")
async def export(
        width: int = size_q,
        height: int = size_q,
        background: str = background_q,
        file: bytes = File(),
):
    file = BytesIO(file)
    ip = ImageProcess(file, width=width, height=height, background=background)
    image = ip.save()
    image.seek(0)
    return StreamingResponse(content=image, media_type='image/jpeg')


@app.post("/preview/")
async def preview():
    return {}
