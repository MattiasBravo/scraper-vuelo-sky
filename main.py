from playwright.sync_api import sync_playwright
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import time
import os
from dotenv import load_dotenv

load_dotenv()

URL = "https://initial-sale.skyairline.com/es/chile?origin=GRU&destination=CCP&departureDate=2026-03-01&flightType=OW&ADT=1"
FECHA_ID = "#carousel-2026-03-01"
PRECIO_SELECTOR = ".days-carousel__card__price"

ARCHIVO = "precio.txt"
SANDBOX_FILE = "sandbox_time.txt"
AVISO_FILE = "aviso_oferta.txt"

PRECIO_OBJETIVO = 150000 

account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
from_phone = os.getenv("TWILIO_PHONE")
to_phone = os.getenv("MY_PHONE")

if not all([account_sid, auth_token, from_phone, to_phone]):
    raise ValueError("Missing Twilio environment variables. Please check your .env file.")


def guardar_inicio_sandbox():
    with open(SANDBOX_FILE, "w") as f:
        f.write(str(time.time()))


def leer_inicio_sandbox():
    if os.path.exists(SANDBOX_FILE):
        with open(SANDBOX_FILE, "r") as f:
            return float(f.read())
    return None


def leer_precio_anterior():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return int(f.read())
    return None


def guardar_precio(precio):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(str(precio))


def ya_aviso_oferta():
    return os.path.exists(AVISO_FILE)


def guardar_aviso_oferta():
    with open(AVISO_FILE, "w") as f:
        f.write("avisado")


def enviar_whatsapp(mensaje):
    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=mensaje,
            from_=f"whatsapp:{from_phone}",
            to=f"whatsapp:{to_phone}"
        )
        print("✅ WhatsApp enviado correctamente")

    except TwilioRestException as e:
        print("⚠️ No se pudo enviar WhatsApp (posible sandbox vencido)")
        print("Detalle:", e)

    except Exception as e:
        print("❌ Error inesperado enviando WhatsApp:", e)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_selector(FECHA_ID)

    elemento = page.query_selector(FECHA_ID)
    precio_texto = elemento.query_selector(PRECIO_SELECTOR).inner_text()

    precio = int(precio_texto.replace("CLP", "").replace(".", "").strip())
    precio_formateado = f"{precio:,}".replace(",", ".")

    precio_anterior = leer_precio_anterior()

    # verificar sandbox
    inicio = leer_inicio_sandbox()
    if inicio:
        horas = (time.time() - inicio) / 3600
        if horas > 60:
            print("⚠️ Sandbox pronto a expirar (menos de 12 horas)")

    # Aviso inmediato si baja del precio objetivo
    if precio < PRECIO_OBJETIVO and not ya_aviso_oferta():
        enviar_whatsapp(
            f"🚨 OFERTA DETECTADA 🚨\n"
            f"✈️ Vuelo GRU → CCP\n"
            f"📅 01-03-2026\n"
            f"🎯 Bajó de 150.000 CLP\n"
            f"💰 Precio actual: {precio_formateado} CLP"
        )
        guardar_aviso_oferta()

    #Aviso normal cada 6 horas
    enviar_whatsapp(
        f"⏰ Estado del precio\n"
        f"✈️ Vuelo GRU → CCP\n"
        f"📅 01-03-2026\n"
        f"💰 Precio actual: {precio_formateado} CLP"
    )

    guardar_precio(precio)
    browser.close()