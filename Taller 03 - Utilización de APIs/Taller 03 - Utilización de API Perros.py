from pymongo import MongoClient
from bson import ObjectId  # Para manejar el _id de MongoDB
import requests
import json

# Configuración de la base de datos MongoDB
client = MongoClient('mongodb+srv://smoscoso:Sergio_M10S@cluster0.v6amn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['dog_db']
collection = db['dogs']

# Función para crear un nuevo perro obteniendo datos de la API
def create_dog():
    """
    Obtiene un hecho sobre un perro desde una API y lo inserta en la base de datos.
    Si la petición a la API es exitosa, se crea un nuevo documento en la colección 'dogs'.
    """
    try:
        response = requests.get('http://dog-api.kinduff.com/api/facts')
        if response.status_code == 200:
            dog_fact = response.json()['facts'][0]
            dog = {'fact': dog_fact}
            collection.insert_one(dog)
            print('Perro creado con éxito:', dog)
        else:
            print('Error al obtener datos de la API')
    except Exception as e:
        print(f'Error al crear el perro: {e}')

# Función para leer todos los perros y mostrarlos en formato JSON
def get_dogs():
    """
    Lee todos los documentos en la colección 'dogs' y los muestra en formato JSON.
    El campo '_id' se incluye en el resultado para referencia.
    """
    try:
        dogs = list(collection.find({}, {'_id': 1, 'fact': 1}))
        print(json.dumps(dogs, indent=4, default=str))
    except Exception as e:
        print(f'Error al obtener los perros: {e}')

# Función para actualizar un perro por su ID
def update_dog(dog_id, new_fact):
    """
    Actualiza el hecho sobre un perro en la base de datos dado su ID.
    
    :param dog_id: ID del perro a actualizar (debe ser un ObjectId en formato de cadena).
    :param new_fact: El nuevo hecho sobre el perro que se actualizará.
    """
    try:
        dog_oid = ObjectId(dog_id)
        result = collection.update_one({'_id': dog_oid}, {'$set': {'fact': new_fact}})
        if result.matched_count:
            print('Perro actualizado con éxito')
        else:
            print('Perro no encontrado')
    except Exception as e:
        print(f'Error al actualizar el perro: {e}')

# Función para eliminar un perro por su ID
def delete_dog(dog_id):
    """
    Elimina un perro de la base de datos dado su ID.
    
    :param dog_id: ID del perro a eliminar (debe ser un ObjectId en formato de cadena).
    """
    try:
        dog_oid = ObjectId(dog_id)
        result = collection.delete_one({'_id': dog_oid})
        if result.deleted_count:
            print('Perro eliminado con éxito')
        else:
            print('Perro no encontrado')
    except Exception as e:
        print(f'Error al eliminar el perro: {e}')

# Menú interactivo
def menu():
    """
    Muestra un menú interactivo para que el usuario pueda elegir entre crear, leer, actualizar o eliminar perros.
    """
    while True:
        print("\nMenú:")
        print("1. Crear un nuevo perro")
        print("2. Leer todos los perros")
        print("3. Actualizar un perro")
        print("4. Eliminar un perro")
        print("5. Salir")
        choice = input("Elige una opción: ")

        if choice == '1':
            create_dog()
        elif choice == '2':
            get_dogs()
        elif choice == '3':
            dog_id = input("Introduce el ID del perro a actualizar: ")
            new_fact = input("Introduce el nuevo hecho sobre el perro: ")
            update_dog(dog_id, new_fact)
        elif choice == '4':
            dog_id = input("Introduce el ID del perro a eliminar: ")
            delete_dog(dog_id)
        elif choice == '5':
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == '__main__':
    menu()
