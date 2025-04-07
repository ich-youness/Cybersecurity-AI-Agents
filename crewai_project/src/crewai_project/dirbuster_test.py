import subprocess

def dirbuster_tool(target_url: str, wordlist_path: str, threads: int = 10):
    """
    Run DirBuster in headless mode (no GUI) with custom wordlist and threads.
    
    Args:
        target_url (str): Target URL (e.g., "http://example.com")
        wordlist_path (str): Absolute path to wordlist (e.g., r"D:\dirbuster\wordlist.txt")
        threads (int): Number of threads (default: 10)
    """
    try:
        # Validate inputs
        if not target_url.startswith(("http://", "https://")):
            return "Error: Target URL must start with http:// or https://"
        
        # Construct the command
        command = [
            "java", "-jar",
            r"D:\dirbuster\DirBuster.jar",  # Path to DirBuster.jar
            "-u", target_url,
            "-l", wordlist_path,
            "-t", str(threads),
            "-noGUI", # Force CLI mode (no GUI popup)
            "-H",
            "-o", "dirbuster_report.txt",
            "-v", "True"

        ]
        
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
        
        return "Scan completed. Results saved to dirbuster_report.txt"
    
    except subprocess.CalledProcessError as e:
        return f"DirBuster failed (exit code {e.returncode}): {e.stderr}"
    except FileNotFoundError:
        return "Error: Java or DirBuster.jar not found. Check paths."
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Example usage with YOUR paths
print(dirbuster_tool(
    target_url="http://2152ad01.ich-youness.pages.dev",
    wordlist_path=r"D:\dirbuster\wordlist.txt",  # Raw string for Windows paths
    threads=20
))