from typing import Text
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
# from crewai_tools import ScrapeWebsiteTool, CodeInterpreterTool
import subprocess
from crewai.tools import tool
from litellm import completion
import os
import requests
import time
from zapv2 import ZAPv2
import psycopg2

agents_config = 'config/agents.yaml'
tasks_config = 'config/tasks.yaml'

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
        # print(DB_CONFIG)
        conn = psycopg2.connect(**DB_CONFIG)
        
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
os.environ['GEMINI_API_KEY'] = "AIzaSyCc_oV5dIHV_DL-5e-uC48Rym9T5kUn13k"

ZAP_API_KEY= "vtfu8u1o4834lnnt8ase8opk0rq"
ZAP_BASE_URL = "http://localhost:8080"
BOT_TOKEN = '8094075847:AAFUuaPGiLveaJwqSEuHTRYGriW_AIUhMDs'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


@tool("telegram document sender")
def send_telegram_document( file_path: str):
    """
    Sends a document to a Telegram chat.
    """
    url = f'{BASE_URL}/sendDocument'
    chat_id = 6284042135
    caption = "Here is your scan report."
    try:
        with open(file_path, 'rb') as file:
            data = {'chat_id': chat_id, 'caption': caption} if caption else {'chat_id': chat_id}
            files = {'document': file}
            response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            return f"Document sent successfully to chat ID {chat_id}."
        else:
            return f"Failed to send document. Error: {response.text}"
    except Exception as e:
        return f"Error sending document: {str(e)}"
    

@tool("owasp zap vulnerability scanner")
def owasp_zap(target: str):
    """
    OWASP ZAP scanner tool that scans a website for vulnerabilities.
    """
    if not target.startswith("http://") and not target.startswith("https://"):
        target = "http://" + target
        print("new target for zap")
    

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target, "owasp_zap"))
    existing_result = cursor.fetchone()

    if existing_result:
        conn.close()
        with open("zap_report.html","w") as file:
            file.write(existing_result[0])
        return f"Cache Loaded"

    zap = ZAPv2(apikey='tfu8u1o4834lnnt8ase8opk0rq', proxies={'http': 'http://127.0.0.1:8081', 'https': 'http://127.0.0.1:8081'})

    # Start the spider scan
    scan_id = zap.spider.scan(target)

    # Wait for the spider to complete
    while int(zap.spider.status(scan_id)) < 100:
        print(f"Spider progress: {zap.spider.status(scan_id)}%")
        time.sleep(5)

    # Start the active scan
    print("Starting active scan...")
    ascan_id = zap.ascan.scan(target)

    # Wait for the active scan to complete
    while int(zap.ascan.status(ascan_id)) < 100:
        print(f"Active scan progress: {zap.ascan.status(ascan_id)}%")
        time.sleep(5)

    # Generate a report
    report = zap.core.htmlreport()
    report_path = "zap_report.html"
    with open(report_path, "w") as f:
        f.write(report)

     # Save the result to the database
    cursor.execute(
        "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
        (target, "owasp_zap", report)
    )
    conn.commit()
    conn.close()
    # Return the path to the report or a summary of the scan
    return f"Scan completed. Report saved to {report_path} "

@tool("Dirbuster scanner")
def dirbuster_tool(target_url: str, options: str):
    """
    Run DirBuster in headless mode (no GUI) with custom wordlist and threads.
    
    Args:
        target_url (str): Target URL (e.g., "http://example.com")
        wordlist_path (str):  r"D:\dirbuster\wordlist.txt"
        threads (int): Number of threads 10
    """
    # wordlist_path =r"D:\dirbuster\wordlist.txt"
    # Validate inputs
    if not target_url.startswith(("http://", "https://")):
            target_url =  "http://" + target_url
            print(" here is the target url: ", target_url)    # threads = 10

    if target_url.startswith("https://"):
        target_url = target_url.replace("https://", "http://")
        print(" here is the target url without https: ", target_url)    # threads = 10
    conn = get_db_connection()
    cursor = conn.cursor()
    
    

    

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target_url, "dirbuster"))
    existing_result = cursor.fetchone()
    
    if existing_result:
            print("here is the result from from the DB: ", existing_result)
            conn.close()
            with open("dirbuster_report.txt","w") as file:
                file.write(existing_result[0])
                return f"Cached DIrbuster results loaded correctly!"
    try:
        
        
        # Construct the command
        command = [
            "java", "-jar",
            r"D:\dirbuster\DirBuster.jar",  # Path to DirBuster.jar
            "-u", target_url,
            "-l", r"D:\dirbuster\wordlist.txt",
            "-t", str(10),
            "-noGUI", # Force CLI mode (no GUI popup)
            "-H",
            "-o", "dirbuster_report.txt",
            "-v", "True"

        ] + options.split()  # Add any additional options passed to the function
        
        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # Raise an error if the command fails
        )
        
        # Save output
        with open("dirbuster_report.txt", "w") as file:
            file.write(result.stdout)
        
        # Save the result to the database
        print("we inserted")
        cursor.execute(
                "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
                (target_url, "dirbuster", result.stdout)
        )
        conn.commit()
        conn.close()

        
        return "Scan completed. Results saved to dirbuster_report.txt"
    
    except subprocess.CalledProcessError as e:
        return f"DirBuster failed (exit code {e.returncode}): {e.stderr}"
    except FileNotFoundError:
        return "Error: Java or DirBuster.jar not found. Check paths."
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool("sqlmap scanner")
def sqlmap_tool(target_url: str, options: str):
    """
    SQLMap scanner tool that scans a website for SQL injection vulnerabilities.

    Args:
        target_url (str): The target URL to scan.
        options (str): Additional SQLMap options (e.g., "--batch --level=5").
    """
    # options = "--crawl=2 "
    # opt = options.split()
    options = " ".join(options.split())  # problem to fix: options are not handled correctly!!!
    print("here is the options: ", options)

    # Ensure the target URL starts with http:// or https://
    # if not target_url.startswith(("http://", "https://")):
    #     target_url = "http://" + target_url

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s AND sqlmap_parameters = %s", 
                   (target_url, "sqlmap", options))
    existing_result = cursor.fetchone()

    if existing_result:
        print("Here is the result from the DB: ", existing_result)
        conn.close()
        with open("sqlmap_report.txt", "w") as file:
            file.write(existing_result[0])
        return f"Cached result: {existing_result[0]}"

    try:
        
        command = [
           "python",
            r"D:\sql-map\sqlmapproject-sqlmap-29825cd\sqlmap.py",
            "-u", target_url,
            "--batch",  # Non-interactive mode
            "--crawl=2",
        ] 

        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # Raise an error if the command fails
        )

        # Save output
        with open("sqlmap_report.txt", "w") as file:
            file.write(result.stdout)

        # Save the result to the database
        print("Inserting result into the database...")
        cursor.execute(
            "INSERT INTO scan_results (target, scan_type, result, sqlmap_parameters) VALUES (%s, %s, %s, %s)",
            (target_url, "sqlmap", result.stdout, options)
        )
        conn.commit()
        conn.close()

        return "SQLMap scan completed. Results saved to sqlmap_report.txt \n\n SQLMap results:" + result.stdout

    except subprocess.CalledProcessError as e:
        return f"SQLMap failed (exit code {e.returncode}): {e.stderr}"
    except FileNotFoundError:
        return "Error: SQLMap not found. Ensure it is installed and in your PATH."
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    
@tool("ssl scanner")
def ssl_scanner(target_url: str):
    """
    SSL/TLS scanner tool to check the security of a website's SSL/TLS configuration.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s ", 
                   (target_url, "ssl_scan"))
    existing_result = cursor.fetchone()

    if existing_result:
        print("Here is the result from the DB: ", existing_result)
        conn.close()
        with open("ssl_report.txt", "w") as file:
            file.write(existing_result[0])
        return f"Cached result: {existing_result[0]}"

    try:
        command = [r"D:\SSL-Scanner\sslscan.exe", target_url]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        with open("ssl_report.txt", "w") as file:
            file.write(result.stdout)
        print("we inserted")
        cursor.execute(
                "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
                (target_url, "ssl_scan", result.stdout)
        )
        conn.commit()
        conn.close()
        return "SSL scan completed. Results saved to ssl_report.txt \n\n SSL results:" + result.stdout
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    

@tool("nmap scanner")
def nmap_tool(target: str, options: str):
  """
  Nmap scanner tool that executes an Nmap scan on a given target.
  """
  conn = get_db_connection()
  cursor = conn.cursor()
  
  
  opts = options.split()
  opts_str = " ".join(opts)

  # Check if the result already exists in the database
  cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s AND nmap_parameters = %s", (target, "nmap", opts_str))
  existing_result = cursor.fetchone()
  
  if existing_result:
        print("here is the result from from the DB: ", existing_result)
        conn.close()
        with open("nmap_report.txt","w") as file:
         file.write(existing_result[0])
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
            "INSERT INTO scan_results (target, scan_type, result, nmap_parameters) VALUES (%s, %s, %s, %s)",
            (target, "nmap", result.stdout, opts_str)
    )
    conn.commit()
    conn.close()
    return result.stdout + " =====> "+ options
  except Exception as e:
    conn.close()
    return f"=> Error handling the Nmap command {str(e)}"
@CrewBase
class CrewaiProject():
    """CrewaiProject crew"""



    # agents_config = 'config/agents.yaml'
    # tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            tools=[nmap_tool, owasp_zap, dirbuster_tool, sqlmap_tool, ssl_scanner],
            config=self.agents_config['researcher'],
            verbose=True
        )
    
    @agent
    def telegram_result_sender(self) -> Agent:
        return Agent(
            tools=[send_telegram_document],
            config=self.agents_config['telegram_result_sender'],
            verbose=True
        )
 
    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )
     

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def telegram_task(self) -> Task:
        return Task(
            config=self.tasks_config['telegram_task'],
        )
    
    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewaiProject crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge
    
        return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
      chat_llm="gemini/gemini-1.5-flash",
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

