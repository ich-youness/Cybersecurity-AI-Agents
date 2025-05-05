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
from pymetasploit3.msfrpc import MsfRpcClient
import whois
from jinja2 import Environment, FileSystemLoader
import pdfkit

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



# data = {
#     "client_name": "ACME Corp",
#     "report_date": "2025-04-28",
#     "executive_summary": "This is a high-level summary of findings...",
#     "nmap_results": "Nmap found 3 open ports: 22, 80, 443...",
#     "zap_results": "Several XSS vulnerabilities were found...",
#     "sqlmap_results": "No SQL injection vulnerabilities found.",
#     "conclusion": "Immediate actions recommended on web server configuration."
# }



@tool("generate report")
def generate_report():
    """
    generate a pentest report in PDF format using Jinja2 and pdfkit.
    """

    with open(r"D:\Stage_PFE\CrewAI\crewai_project\data.json", "r") as dt:

        data = dt.read()
    template_dir = 'D:/Stage_PFE/CrewAI/crewai_project/src/crewai_project/'
    template_file = 'pentest_report_template.html'

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    html_out = template.render(data)

    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    options = {
        'enable-local-file-access': None
    }

    pdfkit.from_string(html_out, 'pentest_report.pdf', configuration=config, options=options)

# Exemple de données
# data = {
#     "client_name": "ACME Corp",
#     "report_date": "2025-04-28",
#     "executive_summary": "Résumé rapide...",
#     "nmap_results": "Ports ouverts : 22, 80, 443",
#     "zap_results": "Détection d'injections XSS.",
#     "sqlmap_results": "Aucune vulnérabilité SQL détectée.",
#     "conclusion": "Actions recommandées : patcher serveur web."
# }


# generate_report(data, 'pentest_report.pdf')

# @tool("owasp zap scanner")
# def zap_scanner_tool(path: str):
#     """
#     OWASP 
#     """
@tool("scrapy tool")
def scrapy_tool(target_url: str):
    """
    Scrapy tool to scrape a website and extract information using a Scrapy spider.
    The spider must accept 'target_url' as an argument.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target_url, "scrapy"))
    existing_result = cursor.fetchone()

    if existing_result:
        with open("scrapy_report.json", "w") as file:
            file.write(existing_result[0])
        conn.close()
        return f"Cached Scrapy results loaded correctly!"
    
    try:
        # Run the Scrapy spider
        subprocess.run(
            [
                "scrapy",
                "runspider",
                r"D:\Stage_PFE\CrewAI\crewai_project\src\crewai_project\scrapy_test.py",
                "-a", f"target_url={target_url}",
                "-o", "scrapy_report.json"
            ],
            capture_output=True,
            text=True
        )

        # Read the output from the generated JSON file
        with open("scrapy_report.json", "r") as file:
            result = file.read()

        print("Cache from file ::> ", result)

        if result:
            # Insert the result into the database
            cursor.execute(
                "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
                (target_url, "scrapy", result)
            )
            conn.commit()
            conn.close()
            return "Scraping completed. Output saved to scrapy_report.json and inserted into the database."
        else:
            conn.commit()
            conn.close()
            return "Scrapy failed: No output generated."

    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Unexpected error: {str(e)}"
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
    # print("Starting active scan...")
    # ascan_id = zap.ascan.scan(target)

    # Wait for the active scan to complete
    # while int(zap.ascan.status(ascan_id)) < 100:
    #     print(f"Active scan progress: {zap.ascan.status(ascan_id)}%")
    #     time.sleep(5)

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
        wordlist_path (str):  r"D:/dirbuster/wordlist.txt"
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
            # "-noGUI", # Force CLI mode (no GUI popup)
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
            print("dirbuster results: /n", result.stdout )
        
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
    options = "--crawl=2 "
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
    
@tool("sublist3r subdomain enumeration")
#capable of bruteforcing as well with -b, try adding it later!
def sublist3r_tool(target_domain: str):
    """
    Sublist3r tool for subdomain enumeration.

    Args:
        target_domain (str): The target domain to enumerate subdomains for.

    Returns:
        str: The result of the Sublist3r scan.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target_domain, "sublist3r"))
    existing_result = cursor.fetchone()

    if existing_result:
        print("Here is the result from the DB: ", existing_result)
        conn.close()
        with open("sublist3r_report.txt", "w") as file:
            file.write(existing_result[0])
        return f"Cached result: {existing_result[0]}"

    try:
        # Construct the Sublist3r command
        command = ["sublist3r", "-d", target_domain]

        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        # Save output to a file
        with open("sublist3r_report.txt", "w") as file:
            file.write(result.stdout)

        # Save the result to the database
        print("Inserting result into the database...")
        cursor.execute(
            "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
            (target_domain, "sublist3r", result.stdout)
        )
        conn.commit()
        conn.close()

        return "Sublist3r scan completed. Results saved to sublist3r_report.txt"

    except subprocess.CalledProcessError as e:
        return f"Sublist3r failed (exit code {e.returncode}): {e.stderr}"
    except FileNotFoundError:
        return "Error: Sublist3r not found. Ensure it is installed and in your PATH."
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    
@tool("whois lookup")
def whois_tool(target_domain: str):
    """
    WHOIS lookup tool to retrieve domain registration information.

    Args:
        target_domain (str): The target domain to perform a WHOIS lookup on.

    Returns:
        str: The WHOIS information for the target domain.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target_domain, "whois"))
    existing_result = cursor.fetchone()

    if existing_result:
        print("Here is the result from the DB: ", existing_result)
        conn.close()
        with open("whois_report.txt", "w") as file:
            file.write(existing_result[0])
        return f"Cached result: {existing_result[0]}"

    try:
        # Perform the WHOIS lookup
        print(f"Performing WHOIS lookup for {target_domain}...")
        whois_data = whois.whois(target_domain)

        # Save the WHOIS data to a file
        with open("whois_report.txt", "w") as file:
            file.write(str(whois_data))

        # Save the result to the database
        print("Inserting result into the database...")
        cursor.execute(
            "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
            (target_domain, "whois", str(whois_data))
        )
        conn.commit()
        conn.close()

        return f"WHOIS lookup completed. Results saved to whois_report.txt\n\n{whois_data}"

    except Exception as e:
        return f"Error performing WHOIS lookup: {str(e)}"

@tool("dnsrecon scanner")
def dnsrecon_tool(target_domain: str, options: str = ""):
    """
    DNSRecon tool for DNS enumeration.

    Args:
        target_domain (str): The target domain to enumerate DNS records for.
        options (str): Additional DNSRecon options (e.g., "-t brt").

    Returns:
        str: The result of the DNSRecon scan.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s AND dnsrecon_parameters = %s", 
                   (target_domain, "dnsrecon", options))
    existing_result = cursor.fetchone()

    if existing_result:
        print("Here is the result from the DB: ", existing_result)
        conn.close()
        with open("dnsrecon_report.txt", "w") as file:
            file.write(existing_result[0])
        return f"Cached result: {existing_result[0]}"

    try:
        # Construct the DNSRecon command
        command = ["dnsrecon", "-d", target_domain] + options.split()

        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        # Save output to a file
        with open("dnsrecon_report.txt", "w") as file:
            file.write(result.stdout)

        # Save the result to the database
        print("Inserting result into the database...")
        cursor.execute(
            "INSERT INTO scan_results (target, scan_type, result, dnsrecon_parameters) VALUES (%s, %s, %s, %s)",
            (target_domain, "dnsrecon", result.stdout, options)
        )
        conn.commit()
        conn.close()

        return "DNSRecon scan completed. Results saved to dnsrecon_report.txt"

    except subprocess.CalledProcessError as e:
        return f"DNSRecon failed (exit code {e.returncode}): {e.stderr}"
    except FileNotFoundError:
        return "Error: DNSRecon not found. Ensure it is installed and in your PATH."
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    

@tool("metasploit exploitation tool")
def metasploit_tool(target_ip: str, exploit: str, payload: str, options: dict):
    """
    Metasploit exploitation tool to exploit a target using a specified exploit and payload.

    Args:
        target_ip (str): The target IP address.
        exploit (str): The Metasploit exploit module to use (e.g., "exploit/windows/smb/ms17_010_eternalblue").
        payload (str): The Metasploit payload to use (e.g., "windows/meterpreter/reverse_tcp").
        options (dict): Additional options for the exploit (e.g., LHOST, LPORT).

    Returns:
        str: The result of the exploitation attempt.
    """
    try:
        # Connect to Metasploit RPC server
        client = MsfRpcClient(password='msfpassword', username='yns', port=55559, server='127.0.0.1', ssl=False)


        # Use the specified exploit
        exploit_module = client.modules.use('exploit', exploit)
        exploit_module['RHOSTS'] = target_ip

        # Set the payload
        payload_module = client.modules.use('payload', payload)
        for key, value in options.items():
            payload_module[key] = value

        # Execute the exploit
        print(f"Running exploit {exploit} against {target_ip}...")
        job_id = exploit_module.execute(payload=payload_module)

        # Wait for the exploit to complete
        while client.jobs.list:
            print("Exploit running...")
            time.sleep(5)

        # Check for sessions
        if client.sessions.list:
            session_id = list(client.sessions.list.keys())[0]
            session = client.sessions.session(session_id)
            return f"Exploit successful! Session ID: {session_id}\nSession Info: {session.info}"
            return f"Exploit successful! Session ID: {session_id}"

        else:
            return "Exploit failed. No session created."

    except Exception as e:
        return f"Error running Metasploit tool: {str(e)}"
  
@tool("wafw00f tool")
def wafw00f_tool(target:str):
    """
    wafw00f is a web app firewall detection tool
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target, "wafw00f"))
    existing_result = cursor.fetchone()
    if existing_result:
        print("Here is the result from the DB: ", existing_result)
        conn.close()
        with open("wafw00f_report.txt", "w") as file:
            file.write(existing_result[0])
        return f"Cached result: {existing_result[0]}"
    try:
        # Run wafw00f command
        result = subprocess.run(
            ["wafw00f", target],
            capture_output=True,
            text=True,
            check=True
        )

        # Save output to a file
        with open("wafw00f_report.txt", "w") as file:
            file.write(result.stdout)

        # Save the result to the database
        print("Inserting result into the database...")
        cursor.execute(
            "INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)",
            (target, "wafw00f", result.stdout)
        )
        conn.commit()
        conn.close()

        return "WAFW00F scan completed. Results saved to wafw00f_report.txt"
    
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
    print("Nmap results: ", result.stdout)
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
    def recon_agent(self) -> Agent:
        return Agent(
            tools=[nmap_tool,  dirbuster_tool, sublist3r_tool, whois_tool, dnsrecon_tool,wafw00f_tool,owasp_zap, sqlmap_tool, ssl_scanner,metasploit_tool , scrapy_tool ],
            config=self.agents_config['recon_agent'],
            verbose=True
        )

    # @agent
    # def recon(self)-> Agent:
    #     return Agent(
    #         tools=[nmap_tool,  dirbuster_tool, sublist3r_tool, whois_tool, dnsrecon_tool,wafw00f_tool],
    #         config=self.agents_config['recon'],
    #         verbose=True
    #     )
    # @agent
    # def vuln(self) -> Agent:
    #     return Agent(
    #         tools=[owasp_zap, sqlmap_tool, ssl_scanner,metasploit_tool , scrapy_tool],
    #         config=self.agents_config['vuln'],
    #         verbose=True
    #     )
    # @agent
    # def json_format(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['json_format'],
    #         verbose=True,
            
    #     )
    
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
            # tools=[generate_report],
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )
    @agent
    def html_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['html_agent'],
            verbose=True
        )
     

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
    # @task
    # def recon_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['recon_task'],
    #     )
    # @task
    # def vuln_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['vuln_task'],
    #     )
    @task
    def recon_task(self) -> Task:
        return Task(
            config=self.tasks_config['recon_task'],
            # output_file='combined_results.txt'
        )
    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.txt'
        )
    
    @task
    def html_task(self) -> Task:
        return Task(
            config=self.tasks_config['html_task'],
            output_file='report_html.html'
        )
    
    # @task
    # def json_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['json_task'],
    #         # output_file='data.json'
    #     )
    @task
    def telegram_task(self) -> Task:
        return Task(
            config=self.tasks_config['telegram_task'],
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
    #   chat_llm="gemini/gemini-1.5-flash",
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

