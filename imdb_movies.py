from playwright.sync_api import sync_playwright
import json
import re

movies = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
    locale="en-US",
    timezone_id="America/New_York",
    geolocation={"longitude": -73.935242, "latitude": 40.730610},
    permissions=["geolocation"],
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36",
    viewport={"width":1280,"height":720},
    java_script_enabled=True,
    bypass_csp=True,
    ignore_https_errors=True
)

    page = context.new_page()
    context.clear_cookies()

    search_url = "https://www.imdb.com/search/title/?title_type=feature&user_rating=2.0,7.0&sort=release_date,desc"

    page.goto(search_url)
    page.wait_for_selector("li.ipc-metadata-list-summary-item")

    items = page.query_selector_all("li.ipc-metadata-list-summary-item")[:25]

    movie_data = []

    for item in items:
        link = item.query_selector("a.ipc-title-link-wrapper")
        href = link.get_attribute("href")
        imdb_id = href.split("/")[2]
        title = link.inner_text().strip()

        rating_tag = item.query_selector("span.ipc-rating-star--rating")
        rating = rating_tag.inner_text() if rating_tag else ""

        movie_data.append((imdb_id, title, rating, href))

    # Now visit each movie page WITHOUT reloading search page
    for imdb_id, title, rating, href in movie_data:

        movie_page = context.new_page()
        movie_page.goto("https://www.imdb.com" + href)
        movie_page.wait_for_selector("body")

        text = movie_page.inner_text("body")
        year_match = re.search(r"\b(19|20)\d{2}\b", text)
        year = year_match.group(0) if year_match else ""

        movies.append({
            "id": imdb_id,
            "title": title,
            "year": year,
            "rating": rating
        })

        movie_page.close()

    browser.close()

print(json.dumps(movies, indent=2))