"""Quick test: verify JSearch API key works."""
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("JSEARCH_API_KEY", "")
print(f"Key: {key[:8]}...{key[-6:]}" if len(key) > 14 else f"Key: {key}")

r = httpx.get(
    "https://jsearch.p.rapidapi.com/search",
    headers={
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    },
    params={"query": "Software Developer", "page": "1", "num_pages": "1"},
    timeout=15,
)
print(f"Status: {r.status_code}")
data = r.json()
if r.status_code != 200:
    print(f"Error: {data}")
else:
    jobs = data.get("data", [])
    print(f"Jobs found: {len(jobs)}")
    for j in jobs[:3]:
        print(f"  - {j['job_title']} @ {j['employer_name']}")
