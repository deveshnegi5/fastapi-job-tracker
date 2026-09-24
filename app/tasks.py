import os
import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from app.celery_app import celery_app
from app.database import session_local
from app import models


ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# @celery_app.task
# def scrape_jobs():
#     url = "https://www.linkedin.com/jobs/"
#     resposnse =requests.get(url,timeout=10)
#     soup=BeautifulSoup(resposnse.text,"html.parser")

#     listings=soup.select(".job-listing")
#     db=session_local()
#     new_count=0

#     try:
#         for listing in listings:
#             job=models.Job(
#                 title=listing.select_one(".job-title").text.strip(),
#                 company = listing.select_one(".job-company").text.strip(),
#                 url=listing.select_one("a")["href"]
#             )
#             db.add(job)
#             try:
#                 db.commit()
#                 new_count+=1
#             except IntegrityError:
#                 db.rollback()
#     finally:
#         db.close()

#     return f"Scraped {len(listings)} listings, {new_count} new"



@celery_app.task
def scrape_jobs():
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": "python developer",
        "where": "india",
        "results_per_page": 20,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    listings = data.get("results", [])
    db = session_local()
    new_count = 0

    try:
        for listing in listings:
            job = models.Job(
                title=listing["title"],
                company=listing.get("company", {}).get("display_name", "Unknown"),
                url=listing["redirect_url"],
            )
            db.add(job)
            try:
                db.commit()
                new_count += 1
            except IntegrityError:
                db.rollback()
    finally:
        db.close()

    return f"Fetched {len(listings)} listings, {new_count} new"