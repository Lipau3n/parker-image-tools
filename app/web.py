from dataclasses import asdict
from io import BytesIO

from fastapi import FastAPI, File, Query, Request
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.images.process.core import ImageProcess
from app.images.read import ImageRead

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(name="index.html", context={'request': request})


@app.post("/read/")
async def read(file: bytes = File()):
    size = len(file)
    file = BytesIO(file)
    img = ImageRead(file, size=size)
    meta = img.read()
    file.close()
    return asdict(meta)


size_q = Query(gt=0, le=7680)
background_q = Query(default='000000', regex='[0-9a-fA-F]{6}')


@app.post("/export/")
async def export(
        width: int = size_q,
        height: int = size_q,
        background: str = background_q,
        file: bytes = File(),
):
    background = f'#{background.upper()}'
    file = BytesIO(file)
    ip = ImageProcess(file, width=width, height=height, background=background)
    image = ip.save()
    image.seek(0)
    file.close()
    image.close()
    return StreamingResponse(content=image, media_type='image/jpeg')


@app.post("/preview/")
async def preview():
    return {}
