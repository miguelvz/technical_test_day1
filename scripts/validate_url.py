import re
from functools import cache
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from googletrans import Translator

IGNORE_CHARS = ["\n", "\t", " ", None]
TRANSLATION_DEPTH = 3
translator = Translator(raise_exception=True)


def get_html_document(url):

    response = requests.get(url)

    return response.text


def tag_visible(element):
    if element.parent.name in [
        "style",
        "script",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def format_urls(urls: str) -> List[str]:
    return [s.strip() for s in urls.splitlines()]


def detect_language(list_of_txt: List[str]) -> List:
    is_translated = translator.detect(list_of_txt)
    return [lang.confidence for lang in is_translated if lang.lang == "hi"]



@cache
def validate_translation(url: str) -> bool:
    html_document = get_html_document(url=url)
    soup = BeautifulSoup(html_document, "html.parser")

    texts = soup.findAll(string=True)
    visible_texts = list(filter(tag_visible, texts))
    visible_texts = list(filter(lambda txt: txt not in IGNORE_CHARS, visible_texts))
    len_visible_text = len(visible_texts)
    is_translated = detect_language(list_of_txt=visible_texts)

    if len(is_translated) / len_visible_text >= 0.8:
        return True
    return False


def validate_urls(urls: str):
    url_list = format_urls(urls=urls)
    print(f"URL LIST: {url_list}")
    url_validation = []
    for url in url_list:
        validation = True
        html_document = get_html_document(url=url)
        soup = BeautifulSoup(html_document, "html.parser")
        links = soup.select("a")
        is_valid = validate_translation(url=url)
        validation = validation and is_valid
        if not validation:
            url_validation.append((url, validation))
            return url_validation
        for idx, link in enumerate(links):
            if (link.get("href") is not None) and (".html" in link.get("href")):
                print(f"URL: {url}/{link.get('href')}, INDEX: {idx}")
                is_valid_sub = validate_translation(url=f'{url}/{link.get("href")}')
                validation = validation and is_valid_sub
                if not validation:
                    url_validation.append((url, validation))
                    return url_validation
            if idx == (TRANSLATION_DEPTH - 1):
                break
        url_validation.append((url, validation))
    return url_validation



def main():
    # validate_urls()
    url_test = (
        "https://graceful-sunburst-78f35d.netlify.app/www.classcentral.com/index.html"
    )
    #print(validate_translation(url=url_test)[1])
    print(validate_urls(urls="https://graceful-sunburst-78f35d.netlify.app/www.classcentral.com/ \n https://ammardab3an99.github.io/"))
    


if __name__ == "__main__":
    main()
