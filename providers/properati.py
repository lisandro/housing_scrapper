import logging
import re

from bs4 import BeautifulSoup

from providers.base_provider import BaseProvider


class Properati(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data["base_url"] + source
        page = 0
        total_pages = 1

        def increment_page_number(url, increment_by=1):
            # Use regular expression to find the page number before the "?"

            page_number_match = re.search(r"/(\d+)\?", url)
            if page_number_match:
                current_page_number = int(page_number_match.group(1))
                new_page_number = current_page_number + increment_by
                new_url = re.sub(r"/\d+\?", f"/{new_page_number}?", url)
            else:
                # If no page number is found, assume it's the first page and append '/2'
                new_url = re.sub(r"(\.com\.ar/s/[^?]+)", r"\1/2", url)
            return new_url

        while True:
            # if page > total_pages:
            #     break

            logging.info("Requesting %s" % page_link)
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                logging.error(f"Invalid status code")
                break

            page_content = BeautifulSoup(page_response.content, "lxml")
            properties = page_content.find_all("article", class_="snippet")

            # if page == 1:
            #     nav_list = page_content.select('#page-wrapper > div.results-content > div.container.wide-listing > div.content > div.row.items-container > div.item-list.span6 > div > div.pagination.pagination-centered > ul > li')
            #     total_pages = len(nav_list) - 2

            if len(properties) == 0:
                logging.error("There are not properties")
                break

            for prop in properties:
                title_tag = prop.find("a", class_="title")
                price_tag = prop.find("div", class_="price")
                href = prop["data-url"]
                idanuncio = prop["data-idanuncio"]

                title = title_tag.text if title_tag else "No title"
                price = price_tag.text if price_tag else "No price"

                formatted_title = f"💰 {price} - 📍 {title}"

                yield {
                    "title": formatted_title,
                    "url": href,
                    "internal_id": idanuncio,
                    "provider": self.provider_name,
                }

            page += 1

            next_page_element = page_content.find(
                "div", {"data-test": "pagination-next", "id": "pagination-next"}
            )
            if next_page_element and next_page_element.get("data-islast") == "true":
                logging.info("Last page reached, stopping execution.")
                break

            page_link = increment_page_number(
                self.provider_data["base_url"] + source, page
            )
            logging.info("Next page%s" % page_link)
