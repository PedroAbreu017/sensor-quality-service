import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.quality import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.consumer import consume_quality_events

    async def handle_event(message: dict):
        logging.getLogger("quality.consumer").info(
            f"[consumer] Quality event received: job={message.get('job_id')} tenant={message.get('tenant')}"
        )

    task = asyncio.create_task(consume_quality_events(handle_event))
    yield
    task.cancel()


app = FastAPI(
    title="Sensor Quality Service",
    description="Data quality analysis and reporting for industrial sensor data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)