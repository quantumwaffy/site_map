import argparse
import asyncio
import re
from typing import Type
from urllib.parse import urljoin, urlparse

import aiohttp
import bs4
from aiohttp import ClientTimeout

from data_structures import Node


class BaseParser:
    _re_url: str = r"^(http:\/\/|https:\/\/|www\.)"
    _request_timeout: int = 5
    _data_class: "Type[Node]" = Node

    def __init__(self, url: str, max_depth: int, max_concurrency: int) -> None:
        assert re.match(self._re_url, url), "Provide correct URL"
        assert max_depth > 0, "The value of maximum depth must be greater than 0"
        self._main_node: Node = self._data_class(url=url)
        self._domain_url: str = f"{urlparse(url).netloc}/"
        self._domain: str = self._domain_url.replace("www.", "")
        self._max_depth: int = max_depth
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrency)
        self._passed_urls: set[str] = set()

    async def fetch_site_data(self, session: aiohttp.ClientSession, url: str) -> str:
        async with self._semaphore:
            async with session.get(url) as response:
                return await response.text()

    def _get_url(self, href: str | None) -> str | None:
        if re.match(self._re_url, href) and self._domain in href:
            return href
        if href.startswith("/"):
            return urljoin(self._domain_url, href.strip("/"))

    async def _populate_map(self, node: _data_class, level: int = 0) -> None:
        url: str = node.url

        if url in self._passed_urls:
            return

        self._passed_urls.add(url)

        async with aiohttp.ClientSession(timeout=ClientTimeout(self._request_timeout)) as session:
            try:
                html_data: str = await self.fetch_site_data(session, url)
            except Exception:
                return
            soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html_data, "html.parser")

            node.children = tuple(
                [
                    self._data_class(url=url)
                    for link in soup.find_all("a", href=True)
                    if (url := self._get_url(link.get("href")))
                ]
            )

            if level == self._max_depth - 1:
                return

            async with asyncio.TaskGroup() as tg:
                [tg.create_task(self._populate_map(child, level=level + 1)) for child in node.children]

    async def _show_data(self, node: _data_class, level: int = 0) -> None:
        print(f"{'>'*level} {node}")

        for child in node.children:
            await self._show_data(child, level=level + 1)

    async def parse(self) -> None:
        print(f"SOURCE URL: {self._main_node.url}")
        print(f"MAX DEPTH: {self._max_depth}")
        await self._populate_map(self._main_node)
        await self._show_data(self._main_node)


if __name__ == "__main__":
    arg_parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Site map builder")
    arg_parser.add_argument("-u", dest="url", type=str, required=True, help="Site URL to parse")
    arg_parser.add_argument("-d", dest="max_d", type=int, default=3, help="Max parsing depth")
    arg_parser.add_argument("-c", dest="max_c", type=int, default=100, help="Max concurrent requests count")
    args: argparse.Namespace = arg_parser.parse_args()
    site_parser: BaseParser = BaseParser(url=args.url, max_depth=args.max_d, max_concurrency=args.max_c)
    asyncio.run(site_parser.parse())
