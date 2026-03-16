from cryptography.fernet import Fernet

if __name__ == "__main__":
    print(f"\n{Fernet.generate_key()}")
