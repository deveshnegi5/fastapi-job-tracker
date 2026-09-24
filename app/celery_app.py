import os
from dotenv import load_dotenv
from celery import Celery
load_dotenv()
redis_url=os.getenv("REDIS_URL")

celery_app = Celery(
    "job_tracker",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks"],
)

celery_app.conf.timezone ="UTC"