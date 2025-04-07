from zapv2 import ZAPv2
import psycopg2
import time

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


def owasp_zap(target: str):
    """
    OWASP ZAP scanner tool that scans a website for vulnerabilities.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the result already exists in the database
    cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s", (target, "owasp_zap"))
    existing_result = cursor.fetchone()

    if existing_result:
        conn.close()
        return f"Cached result: {existing_result[0]}"

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
    return f"Scan completed. Report saved to {report_path}"


owasp_zap("https://myismail.net")