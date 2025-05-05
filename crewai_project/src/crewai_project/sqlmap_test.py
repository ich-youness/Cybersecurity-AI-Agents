import subprocess
def sqlmap_tool(target_url: str, options: str = ""):
    """
    SQLMap scanner tool that scans a website for SQL injection vulnerabilities.

    Args:
        target_url (str): The target URL to scan.
        options (str): Additional SQLMap options (e.g., "--batch --level=5").
    """
    # Ensure the target URL starts with http:// or https://
    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url
        print("Target URL modified to include http://", target_url)

    # conn = get_db_connection()
    # cursor = conn.cursor()

    # Check if the result already exists in the database
    # cursor.execute("SELECT result FROM scan_results WHERE target = %s AND scan_type = %s AND sqlmap_parameters = %s", 
    #                (target_url, "sqlmap", options))
    # existing_result = cursor.fetchone()

    # if existing_result:
    #     print("Here is the result from the DB: ", existing_result)
    #     conn.close()
    #     with open("sqlmap_report.txt", "w") as file:
    #         file.write(existing_result[0])
    #     return f"Cached result: {existing_result[0]}"

    try:
        # Construct the SQLMap command
        command = [
            "python",
            r"D:\sql-map\sqlmapproject-sqlmap-29825cd\sqlmap.py",
            "-u", target_url,
            "--batch"  # Non-interactive mode
        ] + options.split()

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
        # print("Inserting result into the database...")
        # cursor.execute(
        #     "INSERT INTO scan_results (target, scan_type, result, sqlmap_parameters) VALUES (%s, %s, %s, %s)",
        #     (target_url, "sqlmap", result.stdout, options)
        # )
        # conn.commit()
        # conn.close()

        return "SQLMap scan completed. Results saved to sqlmap_report.txt"

    except subprocess.CalledProcessError as e:
        return f"SQLMap failed (exit code {e.returncode}): {e.stderr}"
    except FileNotFoundError:
        return "Error: SQLMap not found. Ensure it is installed and in your PATH."
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    
# Example usage of sqlmap_tool
print(sqlmap_tool(
    target_url="https://2152ad01.ich-youness.pages.dev/",
    options="--crawl=2"
))