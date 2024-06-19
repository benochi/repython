import requests

# API Key for ScraperAPI
api_key = "31fecb85a35e9ccb447ede630e4caf32"

# Base URL for Zillow
ZILLOW_BASE_URL = "https://www.zillow.com/"


# Function to scrape Zillow using ScraperAPI
def scrape_zillow_html(city="tampa", state="fl"):
    city = city.strip().lower()
    state = state.strip().lower()

    # Construct the URL
    current_url = f"{ZILLOW_BASE_URL}{city}-{state}/rentals/"
    payload = {"api_key": api_key, "url": current_url}

    try:
        # Request the page through ScraperAPI
        response = requests.get(
            "https://api.scraperapi.com/", params=payload, timeout=60
        )

        if response.status_code == 200:
            print(f"Scraping from URL: {current_url}")  # Feedback
            content = response.text

            # Save HTML content to a file
            with open("tampa_rentals.html", "w", encoding="utf-8") as file:
                file.write(content)

            print("HTML content saved to 'tampa_rentals.html'")
        else:
            print(
                f"Error: Unable to scrape the URL {current_url} with status code {response.status_code}"
            )

    except Exception as e:
        print(f"Error (URL: {current_url}): {e}")


def main():
    scrape_zillow_html()


if __name__ == "__main__":
    main()
