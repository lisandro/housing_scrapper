# import requests
import logging

from bs4 import BeautifulSoup

from providers.base_provider import BaseProvider


class Zonaprop(BaseProvider):

    def scrape_zonaprop_properties(self, base_url, page_content):
        processed_ids = []
        # Find property cards with the updated class name
        properties = page_content.find_all(
            "div", {"class": "postingCardLayout-module__posting-card-layout"}
        )

        results = []
        for prop in properties:
            # Extract the data-id attribute
            data_id = prop.get("data-id")
            if data_id in processed_ids:
                continue

            processed_ids.append(data_id)

            # Extract the URL
            data_to_posting = prop.get("data-to-posting")

            # Extract the title from the description field
            description = prop.find(
                "h3", {"class": "postingCard-module__posting-description"}
            )

            address_element = prop.find(
                "div", {"class": "postingLocations-module__location-address"}
            )

            address = (
                address_element.get_text().strip()
                if address_element
                else "Address not found"
            )

            # Extract the price
            price_element = prop.find("div", {"class": "postingPrices-module__price"})
            price = (
                price_element.get_text().strip() if price_element else "Price not found"
            )

            # Extract location
            location_element = prop.find(
                "h2", {"class": "postingLocations-module__location-text"}
            )
            location = (
                location_element.get_text().strip()
                if location_element
                else "Location not found"
            )

            # Extract features
            features_element = prop.find(
                "h3",
                {"class": "postingMainFeatures-module__posting-main-features-block"},
            )
            features = []
            if features_element:
                feature_spans = features_element.find_all("span")
                for span in feature_spans:
                    features.append(span.get_text().strip())

            title = f"💰 {price} - 📍 {address} - 🌍 {location}"

            property_data = {
                "title": title,
                "url": base_url + data_to_posting if data_to_posting else "",
                "internal_id": data_id,
                "provider": "zonaprop",
                "price": price,
                "location": location,
                "features": features,
            }

            results.append(property_data)

        return results

    def props_in_source(self, source):
        page_link = self.provider_data["base_url"] + source
        page = 1

        while True:
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, "lxml")
            baseUrlProvider = self.provider_data["base_url"]
            properties_data = self.scrape_zonaprop_properties(
                baseUrlProvider, page_content
            )

            for property_data in properties_data:
                yield property_data

            next_page = page_content.find("a", {"data-qa": "PAGING_NEXT"})
            if next_page is None:
                break
            page += 1
            page_link = self.provider_data["base_url"] + source.replace(
                ".html", f"-pagina-{page}.html"
            )
