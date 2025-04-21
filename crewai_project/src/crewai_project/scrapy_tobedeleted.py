
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

def scrapy_tool(target_url: str, options: str = ""):
    """
    Scrapy tool to scrape a website and extract information using a Scrapy spider.
    The spider must accept 'target_url' as an argument.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target_url,"scrapy"))
    existing_result = cursor.fetchone()

    if existing_result:
        with open("scrapy_report.json", "w") as file:
            file.write(existing_result[0])
        conn.close()
        return f"Cached Scrapy results loaded correctly!"
    
    try:
        subprocess.run(
            [
                "scrapy",
                "runspider",
                r"D:\Stage_PFE\CrewAI\crewai_project\src\crewai_project\scrapy_test.py",
                "-a", f"target_url={target_url}",
                "-a", f"options={options}",
                "-o", "scrapy_report.json"
            ],
            capture_output=True,
            text=True
        )
        with open("scrapy_report.json", "r") as file:
            result = file.read()
            print("result: ", result)
        if result not in None:
            cursor.execute("INSERT INTO scan_results (target, scan_type, result) VALUES (%s, %s, %s)", (target_url, "scrapy", result.stdout))
            conn.commit()
            conn.close()
            return "Scraping completed. Output saved to result.json"
        else:
            conn.commit()
            conn.close()
            return f"Scrapy failed:\n{result.stderr}"
    except Exception as e:
        conn.commit()
        conn.close()
        return f"Unexpected error: {str(e)}"
    
scrapy_tool("https://noureddinephysique.ma/contact/", "")
    