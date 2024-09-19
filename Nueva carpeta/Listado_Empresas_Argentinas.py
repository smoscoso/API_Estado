import requests
import time
from pymongo import MongoClient

# API Key de Hunter.io para buscar correos electrónicos.
API_KEY = '600c6715d6a15f77480503e6271889de12156eca'

# URI de conexión a la base de datos MongoDB en Atlas.
MONGO_URI = "mongodb+srv://smoscoso:Sergio_M10S@cluster0.v6amn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Conectar a la base de datos MongoDB y seleccionar la base de datos y colección.
client = MongoClient(MONGO_URI)  # Crear una instancia de cliente para MongoDB.
db = client['hunter_io_db']  # Seleccionar la base de datos 'hunter_io_db'.
collection = db['emails_empresas']  # Seleccionar la colección 'emails_empresas'.

# Lista de dominios de empresas argentinas para analizar.
dominios_empresas_argentinas = [
    "ypf.com", "techintgroup.com", "mercadolibre.com.ar", "clarin.com", "telecom.com.ar",
    "arcor.com.ar", "bancogalicia.com", "coca-colaandina.com", "cencosud.com", "aluar.com.ar",
    "santander.com.ar", "gruposupervielle.com", "ternium.com", "irsa.com.ar", "aa2000.com.ar",
    "macro.com.ar", "despegar.com.ar", "rappi.com.ar", "laanonima.com.ar", "aerolineas.com.ar",
    "losgrobo.com", "toyota.com.ar", "renault.com.ar", "volkswagen.com.ar", "pampaenergia.com",
    "naturgy.com.ar", "tgs.com.ar", "cablevision.com.ar", "newsan.com.ar", "bago.com.ar",
    "elea.com.ar", "edenor.com.ar", "edesur.com.ar", "metrogas.com.ar", "fravega.com",
    "garbarino.com", "bancociudad.com.ar", "carrefour.com.ar", "coto.com.ar", "swissmedical.com.ar",
    "galeno.com.ar", "bancopatagonia.com", "bancoprovincia.com.ar", "hipotecario.com.ar",
    "petrobras.com.ar", "shell.com.ar", "lacaja.com.ar", "sancorseguros.com.ar", "rus.com.ar",
    "gfg.com.ar"
]

def buscar_correos(dominio):
    """
    Busca correos electrónicos asociados a un dominio utilizando la API de Hunter.io.
    
    Args:
        dominio (str): El dominio de la empresa.
    
    Returns:
        list: Lista de correos electrónicos obtenidos del dominio.
    """
    # Construir la URL de solicitud para la API de Hunter.io.
    url = f"https://api.hunter.io/v2/domain-search?domain={dominio}&api_key={API_KEY}"
    
    try:
        # Realizar la solicitud GET a la API.
        response = requests.get(url)
        
        # Verificar que la solicitud fue exitosa.
        if response.status_code == 200:
            # Convertir la respuesta JSON en un diccionario de Python.
            data = response.json()
            # Extraer la lista de correos electrónicos del diccionario.
            emails = data.get('data', {}).get('emails', [])
            return emails
        else:
            # Imprimir un mensaje de error si la respuesta no es 200 OK.
            print(f"Error al buscar en el dominio {dominio}: {response.status_code}")
            return []
    except requests.RequestException as e:
        # Capturar y mostrar cualquier excepción que ocurra durante la solicitud.
        print(f"Error en la solicitud de correos para {dominio}: {e}")
        return []

def guardar_en_mongo(dominio, correos):
    """
    Guarda los correos electrónicos asociados a un dominio en la colección MongoDB en formato:
    {"dominio": dominio, "correos": [lista de correos]}
    
    Args:
        dominio (str): El dominio de la empresa.
        correos (list): Lista de correos electrónicos a guardar.
    """
    if correos:
        # Crear un documento con el dominio y la lista de correos electrónicos.
        documento = {
            "dominio": dominio,
            "correos": correos
        }
        # Insertar el documento en la colección de MongoDB.
        collection.insert_one(documento)
        print(f"Los correos del dominio {dominio} han sido guardados en MongoDB.")
    else:
        # Mostrar un mensaje si no se encontraron correos para el dominio.
        print(f"No se encontraron correos para el dominio {dominio}.")

# Buscar correos electrónicos para cada dominio y guardarlos en MongoDB.
for dominio in dominios_empresas_argentinas:
    # Buscar correos para el dominio actual.
    correos = buscar_correos(dominio)
    # Extraer solo el valor de cada correo electrónico en una lista.
    correos_lista = [correo['value'] for correo in correos] if correos else []
    
    # Guardar los correos asociados al dominio en MongoDB.
    guardar_en_mongo(dominio, correos_lista)
    
    # Mostrar un mensaje indicando el número de correos encontrados y guardados.
    if correos_lista:
        print(f"Se han encontrado y guardado {len(correos_lista)} correos para el dominio {dominio}.")
    else:
        print(f"No se encontraron correos para el dominio {dominio}.")
    
    # Pausa de 60 segundos entre cada solicitud para evitar límites de la API.
    time.sleep(60)

# Mensaje final indicando que el proceso ha terminado.
print("Todos los correos han sido buscados y almacenados en MongoDB.")
