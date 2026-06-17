from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.templating import _TemplateResponse as TemplateResponse

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=True,
)

async def render(name: str, context: dict):
    """渲染模板并返回 Starlette TemplateResponse"""
    template = env.get_template(name)
    html = await template.render_async(context)
    from starlette.responses import HTMLResponse
    return HTMLResponse(html)
