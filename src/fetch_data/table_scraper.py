# table_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_table_by_caption(url: str, caption_text: str) -> pd.DataFrame:
    
    """
    Finds the first table on a web page with a given <caption> text.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for table in soup.find_all('table'):
        caption = table.find('caption')
        if caption and caption_text.lower() in caption.get_text(strip=True).lower():
            return pd.read_html(str(table))[0]

    raise ValueError(f"Table with caption '{caption_text}' not found.")
