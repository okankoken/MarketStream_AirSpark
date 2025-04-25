#api_2.py
import requests

key = "cvtvni1r01qjg136l32gcvtvni1r01qjg136l330"
url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={key}"

r = requests.get(url)
print(r.status_code)
print(r.text)
