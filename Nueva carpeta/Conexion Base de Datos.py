import mysql.connector

def conectar():
    """
    Establece una conexión con la base de datos MySQL.

    Conecta a la base de datos `employees` utilizando las credenciales y parámetros de conexión especificados.
    Devuelve un objeto de conexión a la base de datos si tiene éxito, de lo contrario devuelve `None`.

    Returns:
        mydb (mysql.connector.connection.MySQLConnection): Objeto de conexión a la base de datos.
        None: Si ocurre un error durante la conexión.
    """
    try:
        mydb = mysql.connector.connect(
            host="18.188.124.77",
            user="studentsucundi",
            passwd="mami_prende_la_radi0",
            port="3306",
            database="employees"
        )
        return mydb
    except mysql.connector.Error as error:
        print("Error al conectar con la base de datos", error)
        return None

# Establece la conexión a la base de datos
mydb = conectar()

def crear_empleado(emp_no, birth_date, first_name, last_name, gender, hire_date, email):
    """
    Crea un nuevo registro de empleado en la tabla `employees`.

    Inserta un nuevo empleado con los datos especificados.

    Args:
        emp_no (int): Número de empleado.
        birth_date (str): Fecha de cumpleaños del empleado.
        first_name (str): Nombre del empleado.
        last_name (str): Apellido del empleado.
        gender (str): Género del empleado.
        hire_date (str): Fecha de contratación del empleado.
        email (str): Correo electrónico del empleado.

    Returns:
        None
    """
    if mydb is not None:
        try:
            cursor = mydb.cursor()
            cursor.execute(
                "INSERT INTO employees (emp_no, birth_date, first_name, last_name, gender, hire_date, email) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                (emp_no, birth_date, first_name, last_name, gender, hire_date, email)
            )
            mydb.commit()
            print(f"El empleado {first_name} {last_name} fue creado con éxito.")
        except mysql.connector.Error as error:
            print("Error al crear el empleado", error)
        finally:
            cursor.close()

def leer_empleado():
    """
    Lee y muestra todos los registros de empleados en la tabla `employees`.

    Recupera y muestra todos los registros de la tabla `employees`.

    Returns:
        None
    """
    if mydb:
        try:
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM employees limit 10")
            empleados = cursor.fetchall()
            for empleado in empleados:
                print(empleado)
        except mysql.connector.Error as error:
            print("Error al leer los empleados", error)
        finally:
            cursor.close()

def actualizar_empleado(emp_no, nombre=None, apellido=None):
    """
    Actualiza la información de un empleado existente en la tabla `employees`.

    Permite actualizar el nombre, apellido, trabajo y salario de un empleado especificado por su ID.

    Args:
        emp_no (int): ID del empleado a actualizar.
        nombre (str, opcional): Nuevo nombre del empleado.
        apellido (str, opcional): Nuevo apellido del empleado.

    Returns:
        None
    """
    if mydb is not None:
        try:
            cursor = mydb.cursor()
            sql = "UPDATE employees SET "
            valores = []

            if nombre:
                sql += "nombre = %s, "
                valores.append(nombre)
            if apellido:
                sql += "apellido = %s, "
                valores.append(apellido)

            # Remover la última coma y espacio
            sql = sql.rstrip(", ")
            sql += " WHERE num_Empleado = %s"
            valores.append(emp_no)

            cursor.execute(sql, tuple(valores))
            mydb.commit()
            print(f"Empleado con ID {emp_no} actualizado exitosamente.")
        except mysql.connector.Error as error:
            print("Error al actualizar el empleado:", error)
        finally:
            cursor.close()
def eliminar_Empleado(emp_no):
    """
    Elimina un empleado de la tabla `employees`.

    Elimina un empleado de la tabla `employees` utilizando el ID especificado.

    Args:
        id_empleado (int): ID del empleado a eliminar.

    Returns:
        None
    """
    if mydb is not None:
        try:
            cursor = mydb.cursor()
            cursor.execute("DELETE FROM employees WHERE emp_no = %s", (emp_no,))
            mydb.commit()
            print(f"Empleado con ID {emp_no} eliminado exitosamente.")
        except mysql.connector.Error as error:
            print("Error al eliminar el empleado:", error)
        finally:
            cursor.close()
# Ejemplo de uso de las funciones con datos predefinidos
def main():
    # Modificar la tabla
    eliminar_Empleado(1002)

    # Crear un empleado
    crear_empleado(1002, "1990-05-15", "Juan", "Pérez", "M", "2024-08-01", "juan.perez@example.com")
    crear_empleado(1003, "1990-05-15", "Jose", "Garzon", "M", "2024-08-01", "Jose.garzon@example.com")
    crear_empleado(1004, "1990-05-15", "Maria", "Perez", "F", "2024-08-01", "mariaperez@example.com")
    crear_empleado(1005, "1990-05-15", "Luis", "Perez", "M", "2024-08-01", "luisperez@example.com")


    # Leer empleados
    leer_empleado()

    # Actualizar un empleado
    actualizar_empleado(1005, nombre="Juan Carlos", salario=55000.00)

if __name__ == "__main__":
    main()
