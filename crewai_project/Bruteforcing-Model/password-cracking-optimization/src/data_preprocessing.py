import pandas as pd

def load_rockyou_data(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        passwords = file.readlines()
    return [password.strip() for password in passwords]

def clean_passwords(passwords):
    # Remove duplicates and filter out short passwords
    unique_passwords = set(passwords)
    cleaned_passwords = [pwd for pwd in unique_passwords if len(pwd) > 5]
    return cleaned_passwords

def save_processed_data(passwords, output_path):
    df = pd.DataFrame(passwords, columns=['password'])
    df.to_csv(output_path, index=False)

def preprocess_rockyou_data(raw_file_path, processed_file_path):
    passwords = load_rockyou_data(raw_file_path)
    cleaned_passwords = clean_passwords(passwords)
    save_processed_data(cleaned_passwords, processed_file_path)