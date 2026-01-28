from playwright.sync_api import sync_playwright
from twilio.rest import Client
import os

URL = "https://initial-sale.skyairline.com/es/chile?origin=GRU&destination=CCP&departureDate=2026-03-01&flightType=OW&ADT=1"
FECHA_ID = "#carousel-2026-03-01"
PRECIO_SELECTOR = ".days-carousel__card__price"
ARCHIVO = "precio.txt"
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
from_phone = os.getenv("TWILIO_PHONE")
to_phone = os.getenv("MY_PHONE")

def leer_precio_anterior():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return int(f.read())
    return None

def guardar_precio(precio):
    with open(ARCHIVO, "w",encoding="utf-8") as f:
        f.write(str(precio))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_selector(FECHA_ID)

    elemento = page.query_selector(FECHA_ID)
    precio_texto = elemento.query_selector(PRECIO_SELECTOR).inner_text()

    precio = int(precio_texto.replace("CLP", "").replace(".", "").strip())

    precio_anterior = leer_precio_anterior()

    if precio_anterior:
        if precio < precio_anterior:
            print("🎉 Bajó el precio")
        elif precio > precio_anterior:
            print("😢 Subió el precio")
        else:
            print("😐 Sigue igual")
    else:
        print("Primera vez guardando precio")

    guardar_precio(precio)
    browser.close()