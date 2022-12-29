from dataclasses import asdict
from io import BytesIO
import gc

from fastapi import FastAPI, File, Query, Request, UploadFile
from fastapi_utils.tasks import repeat_every
from starlette.responses import StreamingResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.images.process.core import ImageProcess
from app.images.read import ImageRead

gc.enable()

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


@app.on_event("startup")
@repeat_every(seconds=60)
def remove_expired_tokens_task() -> None:
    gc.collect()


@app.post("/export/")
async def export(
        file: UploadFile,
        width: int = size_q,
        height: int = size_q,
        background: str = background_q,
):
    background = f'#{background.upper()}'
    source_content = await file.read()

    def iter():
        with BytesIO(source_content) as source, BytesIO() as target:
            ip = ImageProcess(source, width=width, height=height, background=background)
            ip.save(target)
            yield from target

    await file.close()
    return StreamingResponse(content=iter(), media_type='image/jpeg')


@app.post("/preview/")
async def preview():
    return {}
