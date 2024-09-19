from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure

# Conectar a MongoDB
uri = "mongodb+srv://smoscoso:Sergio_M10S@cluster0.v6amn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Verificar la conexión
try:
    # Realizar un ping para confirmar la conexión
    client.admin.command('ping')
    print("Conexión exitosa a MongoDB.")
except ConnectionFailure as e:
    print(f"Error al conectar a MongoDB: {e}")
    exit(1)

# Seleccionar la base de datos y la colección
db = client['Prueba_Mongo']
collection = db['Coleccion_Prueba']

def crear_usuario():
    nombre = input("Ingrese el nombre del usuario: ")
    edad = int(input("Ingrese la edad: "))
    ocupacion = input("Ingrese la ocupación: ")
    telefono = input("Ingrese el telefono: ")
    nuevo_documento = {
        "nombre": nombre,
        "edad": edad,
        "ocupacion": ocupacion,
        "telefono": telefono
    }
    resultado_insertar = collection.insert_one(nuevo_documento)
    print(f"Usuario '{nombre}' creado con ID: {resultado_insertar.inserted_id}")

def leer_usuarios():
    print("Usuarios registrados:")
    documentos = collection.find()
    for doc in documentos:
        print(doc)

def leer_usuario():
    nombre = input("Ingrese el nombre del usuario que desea buscar: ")
    filtro = {"nombre": nombre}
    documento = collection.find_one(filtro)
    
    if documento:
        print(f"Usuario encontrado: {documento}")
    else:
        print(f"No se encontró un usuario con el nombre '{nombre}'.")

def actualizar_usuario():
    nombre = input("Ingrese el nombre del usuario que desea actualizar: ")
    nuevo_nombre = input("Ingrese el nuevo nombre (dejar en blanco para no cambiar): ")
    nueva_edad = input("Ingrese la nueva edad (dejar en blanco para no cambiar): ")
    nueva_ocupacion = input("Ingrese la nueva ocupación (dejar en blanco para no cambiar): ")
    nuevo_Telefono= input("Ingrese el nuevo telefono (dejar en blanco para no cambiar): ")
    
    filtro = {"nombre": nombre}
    cambios = {}
    
    if nuevo_nombre:
        cambios["nombre"] = nuevo_nombre
    if nueva_edad:
        cambios["edad"] = int(nueva_edad)
    if nueva_ocupacion:
        cambios["ocupacion"] = nueva_ocupacion
    if nuevo_Telefono:
        cambios["telefono"] = nuevo_Telefono

    if cambios:
        nueva_informacion = {"$set": cambios}
        resultado_actualizar = collection.update_one(filtro, nueva_informacion)
        if resultado_actualizar.modified_count > 0:
            print(f"Usuario '{nombre}' actualizado.")
        else:
            print(f"No se realizaron cambios en el usuario '{nombre}'.")
    else:
        print("No se realizaron cambios.")

def eliminar_usuario():
    nombre = input("Ingrese el nombre del usuario que desea eliminar: ")
    filtro = {"nombre": nombre}
    resultado_eliminar = collection.delete_one(filtro)
    
    if resultado_eliminar.deleted_count > 0:
        print(f"Usuario '{nombre}' eliminado.")
    else:
        print(f"No se encontró un usuario con el nombre '{nombre}'.")

def menu():
    print("Seleccione una operación:")
    print("1. Crear usuario")
    print("2. Leer todos los usuarios")
    print("3. Leer un usuario específico")
    print("4. Actualizar usuario")
    print("5. Eliminar usuario")
    print("6. Salir")
    return input("Ingrese el número de la operación que desea realizar: ")

while True:
    opcion = menu()
    
    if opcion == '1':
        crear_usuario()
    elif opcion == '2':
        leer_usuarios()
    elif opcion == '3':
        leer_usuario()
    elif opcion == '4':
        actualizar_usuario()
    elif opcion == '5':
        eliminar_usuario()
    elif opcion == '6':
        print("Saliendo del programa...")
        break
    else:
        print("Opción no válida, intente de nuevo.")
