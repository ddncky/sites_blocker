from requests import get


URL = "https://stoic.tekloon.net/stoic-quote"

data = get(URL).json()
author = data["author"]
quote = data["quote"]
