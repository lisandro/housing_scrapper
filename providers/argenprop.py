import logging
import re

from bs4 import BeautifulSoup

from providers.base_provider import BaseProvider


class Argenprop(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data["base_url"] + source
        page = 0
        regex = r".*--(\d+)"

        while True:
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, "lxml")
            properties = page_content.find_all("div", class_="listing__item")

            if len(properties) == 0:
                break

            for prop in properties:
                address_element = prop.find("p", class_="card__address")
                address = (
                    address_element.get_text().strip()
                    if address_element
                    else "Address not found"
                )
                title_element = prop.find("h2", class_="card__title")
                title = (
                    title_element.get_text().strip()
                    if title_element
                    else "No title found"
                )
                price_section = prop.find("p", class_="card__price")
                price = (
                    price_section.get_text().strip()
                    if price_section
                    else "No price found"
                )
                title = f"💰 {price} - 📍 {address} - 🌍 {title}"
                href = prop.find("a", class_="card")["href"]
                matches = re.search(regex, href)
                internal_id = matches.group(1)

                yield {
                    "title": title,
                    "url": self.provider_data["base_url"] + href,
                    "internal_id": internal_id,
                    "provider": self.provider_name,
                }

            next_page = page_content.find(
                "li",
                class_="pagination__page-next pagination__page pagination__page--disable",
            )
            if next_page is not None:
                break

            page += 1
            page_link = self.provider_data["base_url"] + source + f"&pagina-{page}"
