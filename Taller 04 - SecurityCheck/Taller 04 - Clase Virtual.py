from ConfigMongo import config
from pymongo.mongo_client import MongoClient
import requests
import time
import json

# Configuración de conexión a MongoDB Atlas utilizando el URI desde la configuración.
cliente = MongoClient(config["URI"])
base_datos = cliente[config["DATABASE"]]
coleccion = base_datos[config["COLLECTION"]]

class InvestigacionIp:
    """
    Clase que permite realizar investigaciones sobre dominios, obteniendo las IPs, regiones geográficas
    y correos electrónicos asociados. Luego almacena la información en MongoDB.
    """
    
    def __init__(self, dominio):
        """
        Inicializa la clase InvestigacionIp con un dominio.
        
        Args:
            dominio (str): El dominio que se va a investigar.
        """
        self.dominio = dominio
        self.listaIps = []
        self.listaEmails = []
        self.regionPorIp = {}

    def obtenerIpDesdeDominio(self):
        """
        Obtiene las IPs asociadas a un dominio mediante una solicitud a la API de DNS de 'networkcalc'.
        Las IPs se almacenan en la lista 'listaIps'.
        """
        try:
            respuesta_ip = requests.get(f"https://networkcalc.com/api/dns/lookup/{self.dominio}")
            time.sleep(5)  # Pausa para cumplir con los límites de la API.
            json_respuesta = respuesta_ip.json()

            # Verifica si hay registros 'A' en la respuesta.
            if json_respuesta.get("records") and "A" in json_respuesta["records"]:
                for ip in json_respuesta["records"]["A"]:
                    self.listaIps.append(ip["address"])
            else:
                print(f"No se encontraron registros A para el dominio {self.dominio}")
        
        except Exception as e:
            print(f"Error obteniendo IPs para el dominio {self.dominio}: {e}")

    def obtenerRegionDesdeIp(self):
        """
        Obtiene la región geográfica de cada IP en 'listaIps' utilizando la API de 'ipinfo.io'.
        Los resultados se almacenan en el diccionario 'regionPorIp'.
        """
        for ip in self.listaIps:
            try:
                respuesta_region = requests.get(f"https://ipinfo.io/{ip}?token=0bee2ba71a771e")
                time.sleep(5)  # Pausa entre solicitudes para evitar límites de la API.
                json_respuesta_region = respuesta_region.json()

                # Almacena la región (ciudad) asociada a la IP.
                ciudad = json_respuesta_region.get("city", "Ciudad desconocida")
                self.regionPorIp[ip] = ciudad
            
            except Exception as e:
                print(f"Error obteniendo región para la IP {ip}: {e}")

        print(self.regionPorIp)

    def obtenerEmailsDesdeDominio(self):
        """
        Obtiene correos electrónicos asociados a un dominio mediante la API de 'prospeo.io'.
        Los correos se almacenan en la lista 'listaEmails'.
        """
        try:
            respuesta_emails = requests.get(
                f"https://api.hunter.io/v2/domain-search?domain={self.dominio}&api_key=600c6715d6a15f77480503e6271889de12156eca"
            )
            time.sleep(10)  # Pausa para cumplir con los límites de la API.
            json_respuesta_emails = respuesta_emails.json()

            # Verifica si hay correos electrónicos en la respuesta.
            if json_respuesta_emails.get("data") and json_respuesta_emails["data"].get("emails"):
                for email in json_respuesta_emails["data"]["emails"]:
                    self.listaEmails.append(email["value"])
            else:
                print(f"No se encontraron correos electrónicos para el dominio {self.dominio}")
        
        except Exception as e:
            print(f"Error obteniendo correos para el dominio {self.dominio}: {e}")

    def guardarDatos(self):
        """
        Guarda la información recopilada (dominio, IPs, regiones, correos) en MongoDB.
        """
        try:
            plantilla_datos = {
                "Dominio": self.dominio,
                "ListaIps": self.listaIps,
                "RegionPorIp": self.regionPorIp,
                "ListaEmails": self.listaEmails
            }

            # Inserta los datos en la colección MongoDB.
            respuesta_guardado = coleccion.insert_one(plantilla_datos)
            print(f"Datos guardados con ID: {respuesta_guardado.inserted_id}")
        
        except Exception as e:
            print(f"Error al guardar los datos en MongoDB para el dominio {self.dominio}: {e}")

# Lista de dominios a investigar.
dominios_peru = [
    "credicorp.com", "southernperu.com", "buenaventura.com.pe", "alicorp.com.pe",
    "intercorp.com.pe", "granaymontero.com.pe", "backus.pe", "petroperu.com.pe",
    "yanacocha.com", "wong.com.pe", "inretail.pe", "grupo-gloria.com", "ferreycorp.com.pe",
    "rimac.com.pe", "lima-airport.com", "cencosud.pe", "telefonica.com.pe", "samarcanda.pe",
    "metrolima.pe", "vargasycia.com", "incakola.com.pe", "antamina.com", "scotiabank.pe",
    "laive.com.pe", "bcp.com.pe", "laboratoriosfarmaceuticos.com.pe", "gildemeister.com.pe",
    "barrick.com/misquichilca", "aesa.pe", "grupo-penta.com", "deyesa.com.pe", "bago.com.pe",
    "inversioneslarioca.com.pe", "ism.pe", "textildelvalle.com.pe", "cerveceriadelsur.com",
    "lindley.com.pe", "buenaventura.com.pe", "milpo.com", "productosparaiso.com.pe",
    "industriaspiana.com.pe", "santarosa.com.pe", "smith-nephew.com", "siderperu.com.pe",
    "google.com"
]

# Bucle para analizar cada dominio en la lista.
for dominio in dominios_peru:
    print(f"Analizando el dominio: {dominio}")
    try:
        investigacion = InvestigacionIp(dominio)
        investigacion.obtenerIpDesdeDominio()
        investigacion.obtenerRegionDesdeIp()
        investigacion.obtenerEmailsDesdeDominio()
        investigacion.guardarDatos()
    
    except Exception as e:
        print(f"Error al analizar el dominio {dominio}: {e}")
