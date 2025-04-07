import subprocess

def ssl_scanner(target_url: str):
    """
    SSL/TLS scanner tool to check the security of a website's SSL/TLS configuration.
    """
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
        return "SSL scan completed. Results saved to ssl_report.txt"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

print(ssl_scanner("2152ad01.ich-youness.pages.dev"))