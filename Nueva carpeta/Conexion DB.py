
import mysql.connector
from mysql.connector import Error

def connect_to_db():
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

def fetch_high_salaries(con):
    try:
        cursor = con.cursor()
        sql_query = "SELECT * FROM salaries WHERE salary > 120000 LIMIT 5"
        cursor.execute(sql_query)
        results = cursor.fetchall()
        for row in results:
            print(f"Employee No: {row[0]}, Salary: {row[1]}")
    except Error as err:
        print(f"Error reading data: {err}")

def add_salary_record(conn, emp_id, salary_amt, start_date, end_date):
    try:
        cursor = conn.cursor()
        sql_query = "INSERT INTO salaries (emp_no, salary, from_date, to_date) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (emp_id, salary_amt, start_date, end_date))
        conn.commit()
        print(f"Salary record added for Employee ID: {emp_id}")
    except Error as err:
        print(f"Error inserting data: {err}")

def modify_salary_record(conn, emp_id, salary_amt, start_date, end_date):
    try:
        cursor = conn.cursor()
        sql_query = """
        UPDATE salaries 
        SET salary = %s, from_date = %s, to_date = %s
        WHERE emp_no = %s
        """
        cursor.execute(sql_query, (salary_amt, start_date, end_date, emp_id))
        conn.commit()
        print(f"Salary record updated for Employee ID: {emp_id}")
    except Error as err:
        print(f"Error updating data: {err}")

def remove_salary_record(conn, emp_id):
    try:
        cursor = conn.cursor()
        sql_query = "DELETE FROM salaries WHERE emp_no = %s"
        cursor.execute(sql_query, (emp_id,))
        conn.commit()
        print(f"Salary record deleted for Employee ID: {emp_id}")
    except Error as err:
        print(f"Error deleting data: {err}")

# Main function to execute the above operations
def main():
    connection = connect_to_db()

    if connection:
        # Removing a salary record
        print("Deleting a salary record...")
        remove_salary_record(connection, 123456)
        remove_salary_record(connection, 143457)
        remove_salary_record(connection, 183458)
        remove_salary_record(connection, 223459)

        # Inserting a new salary record
        print("Inserting a new salary record...")
        add_salary_record(connection, 123456, 125000, '1990-05-15', '1991-05-15')
        add_salary_record(connection, 143457, 130000, '1991-05-15', '1992-05-15')
        add_salary_record(connection, 183458, 135000, '1992-05-15', '1993-05-15')
        add_salary_record(connection, 223459, 140000, '1993-05-15', '1994-05-15')


        # Reading high salary records
        print("Fetching high salary records...")
        fetch_high_salaries(connection)

        # Updating an existing salary record
        print("Updating a salary record...")
        modify_salary_record(connection, 123456, 130000, '1990-05-15', '1991-05-15')
        modify_salary_record(connection, 123456, 130000, '1990-05-15', '1992-05-15')
        modify_salary_record(connection, 143457, 135000, '1991-05-15', '1992-05-15')

        connection.close()

if __name__ == "__main__":
    main()
