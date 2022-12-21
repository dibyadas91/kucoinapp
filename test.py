import requests
import cryptocom

BASE = "http://127.0.0.1:5000/"

response = requests.get(BASE + "webhook")

