import json
import base64
import getpass
import sys
import argparse
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey, InvalidTag

def decrypt_json_with_password(encrypted_json_path: str, password: str) -> str:
    """
    Decrypts a JSON file using a password.

    Args:
        encrypted_json_path (str): Path to the encrypted JSON file.
        password (str): The password to use for decryption.

    Returns:
        str: The decrypted JSON string.

    Raises:
        FileNotFoundError: If the encrypted file does not exist.
        InvalidTag: If the password is incorrect or the data is corrupt.
        Exception: For other potential errors.
    """
    try:
        # 1. Read the encrypted data from the JSON file
        with open(encrypted_json_path, 'r') as f:
            data = json.load(f)
            # Decode the components from Base64
            salt = base64.b64decode(data['salt'])
            nonce = base64.b64decode(data['nonce'])
            tag = base64.b64decode(data['tag'])
            ciphertext = base64.b64decode(data['ciphertext'])

        # 2. Derive the key from the password and salt
        # This must use the exact same parameters as encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 key
            salt=salt,
            iterations=480000, # Recommended minimum
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # 3. Decrypt the data using AES-GCM
        aesgcm = AESGCM(key)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext + tag, None)

        # 4. Decode the decrypted bytes into a string
        return decrypted_data.decode('utf-8')

    except FileNotFoundError:
        print(f"❌ Error: File not found at '{encrypted_json_path}'")
        raise
    except InvalidTag:
        # This exception is crucial as it indicates a failed authentication,
        # which almost always means the password was wrong.
        print("❌ Decryption Failed: Incorrect password or corrupted data.")
        raise
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        raise

# --- Example Usage ---
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Decrypt an encrypted JSON file using a password.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python decrypt.py encrypted_File
  python decrypt.py /path/to/encrypted_file.json
  python decrypt.py -f myfile.txt
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Path to the encrypted JSON file'
    )
    
    parser.add_argument(
        '-f', '--file',
        dest='file_arg',
        help='Path to the encrypted JSON file (alternative)'
    )
    
    args = parser.parse_args()
    
    # Determine which file argument was used
    encrypted_file = args.file or args.file_arg
    
    # If no file provided, show help and exit
    if not encrypted_file:
        parser.print_help()
        sys.exit(1)
    
    print(f"🔐 Attempting to decrypt '{encrypted_file}'...")
    
    try:
        # Securely prompt for the password without showing it on screen
        user_password = getpass.getpass("Enter password: ")
        
        if not user_password:
            print("Password cannot be empty.")
            sys.exit(1)
        else:
            decrypted_json_string = decrypt_json_with_password(encrypted_file, user_password)
            
            print("\n✅ Decryption Successful!")
            
            # Pretty-print the decrypted JSON
            decrypted_content = json.loads(decrypted_json_string)
            print("📜 Decrypted Content:")
            print(json.dumps(decrypted_content, indent=4))

    except Exception:
        print("\nCould not complete the decryption process.")
        sys.exit(1)