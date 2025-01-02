import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_playcount(track_id):
    url = f"https://www.mystreamcount.com/track/{track_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            playcount_element = soup.find("span", {"class": "text-lg font-bold underline"})
            if playcount_element:
                playcount = playcount_element.text.replace(",", "").strip()
                return int(playcount)
        return None
    except Exception as e:
        print(f"Error fetching playcount: {e}")
        return None
