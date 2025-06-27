from typing import List, Optional
from bs4 import BeautifulSoup
import unicodedata
import re

def extract_attribute_from_selector(html_content: str, selector: str, attribute: str = "href") -> List[str]:
    urls = []
    try:
        soup = BeautifulSoup(html_content, "lxml")
        for element in soup.select(selector):
            url = element.get(attribute)
            if url:
                urls.append(url)
    except Exception as e:
        print(f"Fehler beim Extrahieren von Attributen mit Selektor '{selector}': {e}")

    return urls


def extract_text_from_selector(html_content: str, selector: str) -> Optional[str]:
    if not html_content:
        return None

    try:
        soup = BeautifulSoup(html_content, "lxml")
        target_element = soup.select_one(selector)
        if target_element:
            raw_text = target_element.get_text(separator="\n", strip=True)
            normalized_text = unicodedata.normalize("NFC", raw_text)
            cleaned_text = re.sub(r'\s+', ' ', normalized_text)
            cleaned_text = re.sub(r'[^\S\r\n]+', ' ', cleaned_text)
            return cleaned_text.strip()
    except Exception as e:
        print(f"Fehler beim Extrahieren von Text mit Selektor '{selector}': {e}")

    return None
