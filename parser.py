import concurrent.futures
import os.path
import urllib.parse
from dataclasses import dataclass
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from mizue.progress import ColorfulProgress
from pathvalidate import sanitize_filename


@dataclass
class ParsedImageData:
    filename_jpg: str
    filename_png: str
    url_jpg: str
    url_png: str


class Parser:
    def __init__(self):
        self._soup: BeautifulSoup | None = None
        self.parallel_parsing = 1
        self.prefer_png = True

    def parse(self, url: str, start_page: int = 1, end_page: int | None = None) -> list[ParsedImageData]:
        return self._parse_pages(url, start_page, end_page)

    @staticmethod
    def _get_png_link(page_url: str) -> str | None:
        soup = BeautifulSoup(requests.get(page_url).content, "html5lib")
        png_link = soup.find("a", id="png")
        return png_link["href"] if png_link is not None else None

    def _parse_page(self, page_url: str):
        page_soup = self._get_page_content(page_url)
        page_image_data = self._get_image_data(page_soup)
        return page_image_data

    def _parse_pages(self, page_url: str, start_page: int, end_page: int | None = None) -> list[ParsedImageData]:
        soup = self._get_page_content(page_url)
        if end_page is None:
            end_page = self._get_last_page(soup)
        page_base_url = str.format("{}?page=", page_url) if page_url.find("?tags") == -1 else str.format("{}&page=",
                                                                                                         page_url)
        total_pages = end_page - start_page + 1
        parsed_pages = 0
        progress = ColorfulProgress(0, total_pages, 0)
        progress.label = "Parsing pages: "
        progress.start()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_parsing) as executor:
            futures = [executor.submit(self._parse_page, str.format("{}{}", page_base_url, page_num)) for page_num in
                       range(start_page, end_page + 1)]
            image_data_list: list[ParsedImageData] = []
            for future in concurrent.futures.as_completed(futures):
                image_data_list += future.result()
                parsed_pages += 1
                progress.update_value(parsed_pages)
                progress.info_text = str.format("[Page: {}/{}]", parsed_pages, total_pages)
        progress.stop()
        return image_data_list

    def _get_image_data(self, page_soup: BeautifulSoup) -> list[ParsedImageData]:
        posts_list = page_soup.find('ul', id="post-list-posts")
        if posts_list is None:
            return []
        post_li_list = posts_list.find_all('li')
        post_a_list = [post_li.find('a', class_='directlink') for post_li in post_li_list]
        post_href_list = [post_li.find('a', class_='thumb') for post_li in post_li_list]
        quoted_image_links = [post_a['href'] for post_a in post_a_list if post_a is not None]
        image_links = [unquote(a["href"]) for a in post_a_list]
        image_data_list: list[ParsedImageData] = []
        for idx, link in enumerate(image_links):
            link_quoted = quoted_image_links[idx]
            link_unquoted = urllib.parse.unquote(link_quoted)
            link_unquoted = link_unquoted.replace("?", "_")
            parsed_url = urllib.parse.urlparse(link_unquoted, allow_fragments=False)
            parsed_url_path = parsed_url.path
            basename = os.path.basename(parsed_url_path)
            unquoted_basename = urllib.parse.unquote(basename)
            raw_filename = unquoted_basename
            filename = sanitize_filename(raw_filename)
            link_png = None
            if self.prefer_png:
                link_png = Parser._get_png_link(f"https://yande.re/{post_href_list[idx]['href']}")
            if not self.prefer_png or link_png is None:
                image_data = ParsedImageData(filename, "", link_quoted, "")
            else:
                filename_png = filename.replace(".jpg", ".png")
                image_data = ParsedImageData(filename, filename_png, link_quoted, link_png)
            image_data_list.append(image_data)
        return image_data_list

    @staticmethod
    def _get_last_page(soup: BeautifulSoup) -> int:
        pagination_div = soup.find('div', class_='pagination')
        if pagination_div is None:
            return 1
        page_links = pagination_div.find_all('a')
        if len(page_links) == 0:
            return 1
        last_page_link = page_links[-2].text
        return int(last_page_link)

    @staticmethod
    def _get_page_content(page_url: str) -> BeautifulSoup:
        session = requests.Session()
        response = session.get(page_url)
        soup = BeautifulSoup(response.text, 'html5lib')
        return soup
