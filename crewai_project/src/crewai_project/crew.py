from typing import Text
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, CodeInterpreterTool
import subprocess
from crewai.tools import tool
from litellm import completion
import os
import requests
import time
from zapv2 import ZAPv2
import psycopg2

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
    

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target, "owasp_zap"))
    existing_result = cursor.fetchone()

    if existing_result:
        conn.close()
        return f"Cached result: {existing_result[0]}"

    zap = ZAPv2(apikey='tfu8u1o4834lnnt8ase8opk0rq', proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})

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
    return f"Scan completed. Report saved to {report_path}"

# scraper = ScrapeWebsiteTool()
# interp_nmap = CodeInterpreterTool()
# gemini_llm = {
#       "model": "gemini/gemini-1.5-flash",
#       "api_key": "AIzaSyCc_oV5dIHV_DL-5e-uC48Rym9T5kUn13k",
# }
# @tool("telegram_result_sender")

# Learn more about YAML configuration files here:
# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
agents_config = 'config/agents.yaml'
tasks_config = 'config/tasks.yaml'

@tool("nmap scanner")
def nmap_tool(target: str, options: str):
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
        with open("nmap_report.txt","w") as file:
         file.write(existing_result.stdout)
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
@CrewBase
class CrewaiProject():
    """CrewaiProject crew"""



    # agents_config = 'config/agents.yaml'
    # tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            tools=[nmap_tool, owasp_zap],
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

