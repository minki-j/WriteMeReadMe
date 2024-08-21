import modal 
from modal import asgi_app, Secret

from app.common import app, image, main_vol
from app.fasthtml_app import app as web_app


@app.function(
    image=image,
    gpu=False,
    secrets=[
        Secret.from_name("my-openai-secret"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("my-github-secret"),
        Secret.from_name("my-langsmith-secret"),
        Secret.from_name("my-custom-secret"),
        Secret.from_name("backend_base_url"),
    ],
    volumes={"/vol": main_vol},
    timeout=600,  # 10 minutes
    container_idle_timeout=600,
)
@asgi_app()
def fastapi_asgi():
    return web_app
