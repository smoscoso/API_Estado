import requests
import json
import time
from pymongo import MongoClient, InsertOne
from ConfiMongoDB import config

# API y token
API_Key = "4bb45c88c6e74b59becb509eb365be5b"  # Clave de API para la validación de correos (Abstract API)
Github_Token = "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"  # Token de acceso para la API de GitHub

# Conexión a la base de datos MongoDB alojada en MongoDB Atlas
client = MongoClient(config["URI"])
db = client[config["DATABASE"]]  # Base de datos 'Check_Emails'
collection = db[config["COLLECTION"]]    # Colección 'emails' para almacenar la información validada

class CheckEmail:
    def __init__(self):
        """
        Constructor de la clase CheckEmail que inicializa las listas que se utilizarán para almacenar
        correos electrónicos, phishing, nombres de usuarios, repositorios, y los documentos que se
        insertarán en MongoDB.
        """
        self.listEmail = []  # Lista para almacenar los correos obtenidos de la API del estado
        self.listEmailPhishing = []  # Lista para almacenar correos sospechosos de phishing
        self.usernames_found = []  # Lista para almacenar los nombres de usuarios encontrados en GitHub
        self.repositories = []  # Lista para almacenar los enlaces a los repositorios de GitHub
        self.email_documents = []  # Lista para almacenar los documentos de correos que se insertarán en MongoDB

    def requestDataFromAPI(self):
        """
        Este método consume una API gubernamental para obtener una lista de correos electrónicos
        y los almacena en la lista `self.listEmail`. En este ejemplo, se limitan a 3 correos electrónicos
        para evitar un exceso de solicitudes.
        """
        try:
            # Solicitud GET a la API del estado para obtener correos electrónicos
            responseAPIEmails = requests.get("https://www.datos.gov.co/resource/jtnk-dmga.json")
            dataJson = responseAPIEmails.json()  # Conversión de la respuesta a formato JSON
            
            # Limitar el procesamiento a los primeros 50 correos electrónicos
            for email in dataJson[:50]:
                self.listEmail.append(email['email_address'])  # Añadir cada correo a la lista listEmail
        except requests.exceptions.RequestException as e:
            # Captura y muestra cualquier error que ocurra al consumir la API
            print(f"Error al consumir la API del estado: {e}")

    def validateEmail(self):
        """
        Este método valida cada correo electrónico de la lista `self.listEmail` utilizando la API de Abstract.
        Verifica si los correos son válidos y si son propensos a phishing. Luego almacena la información
        en un documento que será insertado en MongoDB.
        """
        for email in self.listEmail:
            try:
                # Solicitud GET para validar el correo electrónico usando la API de Abstract
                print(f"Validando correo {email}...")
                responseEmail = requests.get(f"https://emailvalidation.abstractapi.com/v1/?api_key={API_Key}&email={email}")
                
                # Si la solicitud es exitosa (código de respuesta 200)
                if responseEmail.status_code == 200:
                    dataEmailsJson = responseEmail.json()  # Convertir la respuesta en JSON
                    deliverability = dataEmailsJson.get('deliverability', 'UNKNOWN')  # Verificar si es entregable
                    
                    # Solo se almacenan los correos con estado DELIVERABLE
                    if deliverability == 'DELIVERABLE':
                        status = 'Valid'  # Estado del correo es válido
                        
                        # Verificar si el correo es de tipo phishing
                        is_phishing = dataEmailsJson.get('is_disposable_email', False) or dataEmailsJson.get('is_role_email', False)
                        
                        if is_phishing:
                            # Si el correo es considerado phishing, se añade a la lista de phishing
                            self.listEmailPhishing.append(email)
                            print(f"Correo phishing encontrado: {email}")
                        
                        # Crear el documento de correo que se almacenará en MongoDB
                        email_document = {
                            'email': email,
                            'validation': {
                                'status': status,
                                'validation_data': dataEmailsJson.get('deliverability', {})  # Datos de validación
                            },
                            'github_search': {
                                'usernames_found': [],
                                'repositories': [],
                                'profile_link': '',  # Inicialización del enlace del perfil de GitHub
                                'status': 'Pending'  # Estado de la búsqueda de GitHub (Pendiente)
                            }
                        }
                        # Añadir el documento a la lista de documentos que se insertarán en MongoDB
                        self.email_documents.append(email_document)
                    else:
                        print(f"Correo {email} no es DELIVERABLE, no se guardará.")  # No se almacena si no es entregable
                else:
                    print(f"Error en la validación del correo {email}: {responseEmail.status_code}")  # Error en la solicitud
            except requests.exceptions.RequestException as e:
                print(f"Error en la solicitud de validación del correo {email}: {e}")  # Error en la solicitud de validación
            except Exception as e:
                print(f"Error procesando {email}: {e}")  # Cualquier otro error que ocurra
            
            # Pausa de 5 segundos entre cada solicitud para evitar exceder los límites de la API
            time.sleep(5)

        # Si se han validado correos, se insertan en MongoDB en una sola operación
        if self.email_documents:
            collection.bulk_write([InsertOne(doc) for doc in self.email_documents])

    def extractUsername(self, email):
        """
        Método para extraer el nombre de usuario de un correo electrónico (la parte antes de '@').
        """
        return email.split('@')[0]  # Separa el correo y devuelve el texto antes del símbolo '@'
    
    def searchInGithub(self):
        """
        Este método busca si los correos en `self.listEmailPhishing` están asociados a cuentas de GitHub.
        Primero intenta buscar usando el nombre de usuario (parte antes de '@'). Si no encuentra nada,
        realiza la búsqueda directamente por el correo electrónico. Finalmente, actualiza los registros en MongoDB.
        """
        profile_link = ''  # Variable para almacenar el enlace al perfil de GitHub (si se encuentra)
        for email in self.listEmailPhishing:
            try:
                username = self.extractUsername(email)  # Extraer el nombre de usuario del correo
                
                # Encabezados para la solicitud a la API de GitHub
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {Github_Token}",  # Token de autenticación
                    "X-GitHub-Api-Version": "2022-11-28"
                }

                # Buscar por nombre de usuario en GitHub
                responseUser = requests.get(f"https://api.github.com/search/users?q={username}+in:login", headers=headers)
                dataUserJson = responseUser.json()
                
                # Si se encuentra al menos un usuario
                if dataUserJson.get('total_count', 0) > 0:
                    self.usernames_found.append(username)  # Añadir el nombre de usuario encontrado
                    
                    # Obtener el login del primer usuario encontrado y construir el enlace del perfil
                    user_login = dataUserJson['items'][0]['login']
                    profile_link = f"https://github.com/{user_login}"
                    
                    # Obtener los repositorios del usuario
                    responseRepos = requests.get(f"https://api.github.com/users/{user_login}/repos", headers=headers)
                    dataReposJson = responseRepos.json()

                    # Guardar los enlaces de los repositorios encontrados
                    for repo in dataReposJson:
                        self.repositories.append(repo['html_url'])

                # Si no se encuentra por nombre de usuario, buscar directamente por correo
                if not self.usernames_found:
                    responseEmail = requests.get(f"https://api.github.com/search/users?q={email}+in:email", headers=headers)
                    dataEmailJson = responseEmail.json()

                    # Si se encuentra un usuario asociado al correo
                    if dataEmailJson.get('total_count', 0) > 0:
                        self.usernames_found.append(email)  # Añadir el correo a la lista de encontrados

                        # Obtener el login del usuario encontrado y el enlace al perfil de GitHub
                        user_login = dataEmailJson['items'][0]['login']
                        profile_link = f"https://github.com/{user_login}"
                        
                        # Obtener los repositorios del usuario
                        responseRepos = requests.get(f"https://api.github.com/users/{user_login}/repos", headers=headers)
                        dataReposJson = responseRepos.json()

                        # Guardar los enlaces de los repositorios
                        for repo in dataReposJson:
                            self.repositories.append(repo['html_url'])

                # Actualizar el documento en MongoDB con los resultados de la búsqueda en GitHub
                collection.update_one(
                    {'email': email},
                    {
                        '$set': {
                            'github_search': {
                                'usernames_found': self.usernames_found,
                                'repositories': self.repositories,
                                'profile_link': profile_link,
                                'status': 'Found' if self.usernames_found else 'Not Found'
                            }
                        }
                    }
                )
                # Pausa de 5 segundos entre cada solicitud para evitar límites de la API
                time.sleep(5)
            except Exception as e:
                print(f"Error procesando {email}: {e}")  # Captura de cualquier error que ocurra durante la búsqueda

# Ejecución del flujo completo
prueba = CheckEmail()  # Crear una instancia de la clase CheckEmail
prueba.requestDataFromAPI()  # Obtener correos electrónicos desde la API del estado
prueba.validateEmail()  # Validar los correos obtenidos
prueba.searchInGithub()  # Buscar si los correos están asociados a cuentas de GitHub