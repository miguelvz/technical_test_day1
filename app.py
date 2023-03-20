from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from scripts.validate_url import validate_urls

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process_urls", response_class=HTMLResponse)
async def process_urls(request: Request, urls: str = Form(...)):
    validation_list = validate_urls(urls=urls)
    return templates.TemplateResponse(
        "response.html", {"request": request, "urls": urls, "validation_list": validation_list}
    )
