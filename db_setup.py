import psycopg2 #psycopg2 connector is imported after being installed on the PC.
from config import Config #Obtains the Config class from config.py, so database credentials can be accessed.

def connect_to_database(): #Establishes connection to database.
    conn = psycopg2.connect(
        host=Config.DB_HOST, #All necessary credentials from config are used here.
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    return conn #Conn is the actual connection, which is referenced when used.

def execute_sql_file(filename): #Method to execute SQL file after connection.
    conn = connect_to_database() #Uses method declared above.
    cur = conn.cursor() # Cursor is what is used to actually insert commands and execute.
    try:
        with open(filename, 'r') as f:#Python reading files syntax used here, with 'r' as read only.
            sql = f.read()
        cur.execute(sql)
        conn.commit() #Saves changes made to database.
        print("SQL script read successfully.")#Will print to console if successful.
    except Exception as e:
        print("Error reading SQL script:", e)#Will print error message to console if unsuccessful.
    finally:    
        cur.close() #Close cursor.
        conn.close()#Close connection.
