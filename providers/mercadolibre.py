import logging
import re

from bs4 import BeautifulSoup

from providers.base_provider import BaseProvider


class Mercadolibre(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data["base_url"] + source + "_NoIndex_True"
        from_ = 1
        regex = r"(MLA-\d*)"

        while True:
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, "lxml")
            properties = page_content.find_all("li", class_="ui-search-layout__item")

            if len(properties) == 0:
                break

            for prop in properties:
                # Find the main link element
                link_element = prop.find(
                    "a", class_="poly-component__link"
                ) or prop.find("a", class_="poly-component__title")

                if not link_element:
                    continue

                href = link_element.get("href")

                # Extract internal ID using regex
                matches = re.search(r"MLA-(\d+)", href)
                internal_id = matches.group(1) if matches else None

                # Extract title
                title_element = prop.find("h3", class_="poly-component__title-wrapper")
                title = (
                    title_element.find("a").get_text().strip()
                    if title_element
                    else "No title found"
                )

                # Extract price
                price_element = prop.find("div", class_="poly-component__price")
                price = (
                    price_element.get_text().strip()
                    if price_element
                    else "No price found"
                )

                if price is not None:
                    title = title + " " + price

                yield {
                    "title": title,
                    "url": href,
                    "internal_id": internal_id,
                    "provider": self.provider_name,
                }

            from_ += 48
            # Find the position after "/mar-del-plata/"
            marker = "/mar-del-plata/"
            newLink = self.provider_data["base_url"] + source + f"_NoIndex_item"
            pos = page_link.find(marker) + len(marker)

            newUrl = newLink[:pos] + f"_Desde_{from_}_" + newLink[pos:]

            nextPage = page_content.find_all(
                "li", class_="andes-pagination__button andes-pagination__button--next"
            )

            if len(nextPage) == 0:
                break

            logging.info(f"Requesting {newUrl}")
            page_link = newUrl
