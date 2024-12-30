import requests
from bs4 import BeautifulSoup
import json

def scrape_walmart_tvs(url):
    """
    Scrapes data from a Walmart TV product listing page and returns a list of dictionaries containing basic product information.

    Args:
        url: The URL of the Walmart TV product listing page.

    Returns:
        A list of dictionaries containing scraped product data, or None if scraping fails.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product containers on the page
        product_containers = soup.find_all('div', class_='gridview-item')

        # Extract data from each product container
        products = []
        for container in product_containers:
            try:
                title_element = container.find('a', class_='product-title-link')
                title = title_element.text.strip()

                # Extract price using regex or more robust methods (price format might change)
                price_element = container.find('span', class_='price')
                price_text = price_element.text.strip()
                # You can use regular expressions here to extract the numeric value from the price text

                # Information like rating and reviews might not be readily available on the listing page and might require following product links
                products.append({
                    'title': title,
                    'price': price_text,
                    'rating': None,  # Placeholder, can be populated if reviews page is followed
                    'reviews': None,  # Placeholder, can be populated if reviews page is followed
                })
            except AttributeError:
                # Skip products with missing data
                pass

        return products

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except AttributeError as e:
        print(f"Error parsing HTML: {e}")
        return None

if __name__ == "__main__":
    # Walmart TV listing page URL
    walmart_url = "https://www.walmart.com/shop/deals/electronics/tvs?seo=deals&seo=electronics&seo=tvs&page=1&affinityOverride=default"

    tv_data = scrape_walmart_tvs(walmart_url)

    if tv_data:
        # Print the list of dictionaries
        print(json.dumps(tv_data, indent=4))

        # Optionally, save the data to a file
        with open('walmart_tvs.json', 'w') as f:
            json.dump(tv_data, f, indent=4)