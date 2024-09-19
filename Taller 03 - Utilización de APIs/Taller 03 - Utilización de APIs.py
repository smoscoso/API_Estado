import requests
import json

# Tu clave API de Prospeo
api_key = '4846977f3e4583e0cbe765069394ac68'
# El dominio que quieres consultar
domain = 'buenaventura.com.pe'

# URL de la API de Prospeo
url = 'https://api.prospeo.io/domain-search'

# Parámetros de la solicitud
payload = {
    'company': domain,
    'limit': 10,  # Número de correos electrónicos que deseas obtener
    'email_type': 'all',  # Tipo de correos electrónicos: 'all', 'generic', 'professional'
    'company_enrichment': False  # Si deseas obtener detalles de la empresa
}

# Encabezados de la solicitud
headers = {
    'Content-Type': 'application/json',
    'X-KEY': api_key
}

# Hacer la solicitud POST
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    data = response.json()
    if not data['error']:
        print(json.dumps(data['response'], indent=4))
    else:
        print(f"Error: {data['message']}")
else:
    print(f'Error: {response.status_code}')

