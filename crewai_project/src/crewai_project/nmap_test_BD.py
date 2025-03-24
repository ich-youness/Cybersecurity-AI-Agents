import psycopg2
import subprocess

DB_CONFIG = {
    "dbname": "recon_data",
    "user": "postgres",
    "password": "bibi",
    "host": "localhost",
    "port": 5432
    

}

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        print(DB_CONFIG)
        conn = psycopg2.connect(**DB_CONFIG)
        # conn = psycopg2.connect(
        #     dbname = "recon_data",
        #     user= "postgres",
        #     password= "bibi",
        #     host= "localhost",
        #     port= 5432
        # )
        
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
    

def my_tool(target: str, options: str):
  """
  Nmap scanner tool that executes an Nmap scan on a given target.
  """
  conn = get_db_connection()
  cursor = conn.cursor()
  
  # Check if the result already exists in the database
  cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target, "nmap"))
  existing_result = cursor.fetchone()
  
  if existing_result:
        print("here is the result from from the DB: ", existing_result)
        conn.close()
        return f"Cached result: {existing_result[0]}"


    
  try:
    result = subprocess.run(
      ["nmap"] + options.split() + [target], 
      capture_output=True,
      text=True  
    )
    with open("nmap_report.txt","w") as file:
         file.write(result.stdout)
    
    # Save the result to the database
    print("we inserted")
    cursor.execute(
            "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
            (target, "nmap", result.stdout)
    )
    conn.commit()
    conn.close()
    return result.stdout + " =====> "+ options
  except Exception as e:
    conn.close()
    return f"=> Error handling the Nmap command {str(e)}"
  
my_tool("linkedin.com", "-Pn")

# conn = psycopg2.connect("dbname=recon_data user=postgres password=bibi host=localhost port=5432".encode('utf-8'))
# conn = psycopg2.connect("dbname=test user=postgres")
# print(conn)
# import psycopg2

# # Connect to your postgres DB
# conn = psycopg2.connect("dbname=recon_data user=postgres host=localhost port=5432 password=bibi")

# # Open a cursor to perform database operations
# cur = conn.cursor()

# # Execute a query
# cur.execute("SELECT * FROM scan_results")

# # Retrieve query results
# records = cur.fetchall()
# print(records)

