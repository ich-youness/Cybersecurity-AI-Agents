import subprocess

def integrate_with_john(password_file: str):
    """
    Integrates the generated password list with John the Ripper for password cracking.

    Args:
        password_file (str): Path to the file containing generated passwords.
    """
    try:
        # Run John the Ripper with the specified password file
        result = subprocess.run(['john', password_file], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("John the Ripper executed successfully.")
            print(result.stdout)
        else:
            print("Error executing John the Ripper:")
            print(result.stderr)
    except FileNotFoundError:
        print("John the Ripper not found. Please ensure it is installed and in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    # Example usage
    integrate_with_john('../data/processed/passwords.csv')