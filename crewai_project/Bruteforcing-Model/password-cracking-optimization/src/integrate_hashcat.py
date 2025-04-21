import subprocess
import os

def integrate_with_hashcat(passwords_file, hashcat_path):
    if not os.path.exists(passwords_file):
        raise FileNotFoundError(f"The specified passwords file does not exist: {passwords_file}")

    if not os.path.exists(hashcat_path):
        raise FileNotFoundError(f"The specified Hashcat path does not exist: {hashcat_path}")

    command = [hashcat_path, '-a', '0', '-m', '0', passwords_file, 'hashes.txt']
    
    try:
        subprocess.run(command, check=True)
        print("Integration with Hashcat completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Hashcat: {e}")

if __name__ == "__main__":
    passwords_file = '../data/processed/passwords.csv'  # Adjust the path as necessary
    hashcat_path = '/path/to/hashcat'  # Update this to the actual path of Hashcat
    integrate_with_hashcat(passwords_file, hashcat_path)