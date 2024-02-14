import sqlite3
from cryptography.fernet import Fernet
import random
import string

class PasswordManager:
    def __init__(self, db_file, key_file):
        self.db_file = db_file
        self.key = self.load_key(key_file)
        self.conn = sqlite3.connect(self.db_file)
        self.cur = self.conn.cursor()
        self.create_table()

    def load_key(self, key_file):
        try:
            with open(key_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS passwords
                            (id INTEGER PRIMARY KEY,
                             website TEXT NOT NULL,
                             username TEXT NOT NULL,
                             password TEXT NOT NULL)''')
        self.conn.commit()

    def encrypt_password(self, password):
        cipher_suite = Fernet(self.key)
        return cipher_suite.encrypt(password.encode())

    def decrypt_password(self, encrypted_password):
        cipher_suite = Fernet(self.key)
        return cipher_suite.decrypt(encrypted_password).decode()

    def add_password(self, website, username, password):
        encrypted_password = self.encrypt_password(password)
        self.cur.execute('''INSERT INTO passwords (website, username, password)
                             VALUES (?, ?, ?)''', (website, username, encrypted_password))
        self.conn.commit()

    def get_password(self, website):
        self.cur.execute('''SELECT password FROM passwords WHERE website = ?''', (website,))
        row = self.cur.fetchone()
        if row:
            return self.decrypt_password(row[0])
        else:
            return None

    def get_website_list(self):
        self.cur.execute('''SELECT DISTINCT website FROM passwords''')
        websites = [row[0] for row in self.cur.fetchall()]
        return websites

    def generate_password(self):
        length=int(input("enter the length of password:"))
        if length>=8:
            characters = string.ascii_letters + string.digits + string.punctuation
            return ''.join(random.choice(characters) for _ in range(length))
        else:
            print("The legth of password should be greater than 8......")
            return 0

if __name__ == '__main__':
    db_file = 'passwords.db'
    key_file = 'key.key'
    password_manager = PasswordManager(db_file, key_file)
    
    while True:
        print("1. Add Password")
        print("2. Show List of Saved Websites")
        print("3. Show Password for Website")
        print("4. Generate Password")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            website = input("\nPlease enter the website address: ")
            username = input("Please enter the user name: ")
            password = input("Please enter the password: ")
            if len(password) >= 8:
                if website in password_manager.get_website_list():
                    print(f"Updating password for {website}...")
                else:
                    print(f"Adding new website: {website}")

                password_manager.add_password(website, username, password)
                print("Password added successfully.")
            else:
                print("Password should be at least 8 characters long.")

        elif choice == '2':
            websites = password_manager.get_website_list()
            print("List of Saved Websites:")
            for idx, website in enumerate(websites, 1):
                print(f"{idx}. {website}")


        elif choice == '3':
            website = input("Enter the website to get the password of: ")
            password = password_manager.get_password(website)
            if password:
                print(f"Password for {website}: {password}")
            else:
                print("No password found for the specified website.")
                
        elif choice == '4':
                password = password_manager.generate_password()
                if password!=0:
                    print(f"Generated Password: {password}")
                    a=input("Do you want to save this password to the website?(y|n):")
                    if a=='y':
                    
                        website = input("Please enter the website address: ")
                        username = input("Please enter the user name: ")

                        if website in password_manager.get_website_list():
                            print(f"Updating password for {website}...")
                        else:
                            print(f"Adding new website: {website}")
                        password_manager.add_password(website, username, password)
                        print("Password added successfully.")
                    else:
                        print("Not saving......")

        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select a valid option.")
