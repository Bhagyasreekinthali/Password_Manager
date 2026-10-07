import random
import getpass
import subprocess
from cryptography.fernet import Fernet
try:
    with open("secret.key", "rb") as file:
        encryption_key = file.read()
except FileNotFoundError:
    encryption_key = Fernet.generate_key()
    with open("secret.key", "wb") as file:
        file.write(encryption_key)
cipher = Fernet(encryption_key)
def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()
def decrypt_password(password):
    return cipher.decrypt(password.encode()).decode()
master_password = "1234"
try:
    with open("master_password.txt", "r") as file:
        master_password = file.read().strip()
except FileNotFoundError:
    pass
accounts = []
needs_encryption = False

try:
    with open("accounts.txt", "r") as file:
        for line in file:
            website, username, password = line.strip().split("|")

            try:
                password = decrypt_password(password)
            except:
                needs_encryption = True

            accounts.append([website, username, password])

except FileNotFoundError:
    pass
if needs_encryption:
    with open("accounts.txt", "w") as file:
        for account in accounts:
            encrypted_password = encrypt_password(account[2])
            file.write(f"{account[0]}|{account[1]}|{encrypted_password}\n")
entered_password = getpass.getpass("Enter master password: ")
if entered_password != master_password:
    print("Incorrect master password!")
    exit()
while True:

    print("Password Manager")
    print("1. Add Account")
    print("2. View Accounts")
    print("3. Search Account")
    print("4. Update Account")
    print("5. Delete Account")
    print("6. Generate Password")
    print("7. Password Strength Checker")
    print("8. Exit")
    print("9. Change Master Password")

    choice = input("Enter your choice: ")
    print("you entered:", choice)

    if choice == "1":
        print("Add Account")
        website = input("Enter website: ")
        found = False
        for account in accounts:
            if account[0].lower() == website.lower():
                print("Account already exists!")
                found = True
                break
            if not found:
                username = input("Enter username: ")
                password = input("Enter password: ")
                accounts.append([website, username, password])
                with open("accounts.txt", "a") as file:
                    file.write(f"{website}|{username}|{encrypt_password(password)}\n")
                print("Account added successfully!")

    elif choice == "2":
        if not accounts:
            print("No accounts found!")
        else:
            account_number = int(input("Enter account number to view: "))
            if account_number < 1 or account_number > len(accounts):
                print("Invalid account number!")
                continue
            account = accounts[account_number - 1]
            
            print("--- Account", account_number, "---")
            print("Website:", account[0])
            print("Username:", account[1])
            show_password = input("Show password? (yes/no): ")
            if show_password.lower() == "yes":
                print("Password:", account[2])
                copy_password = input("Copy password? (yes/no): ")
                if copy_password.lower() == "yes":
                    subprocess.run(["clip"], input=account[2], text=True, check=True)
                    print("Password copied to clipboard!")
                    
            else:
                print("Password: *********")
                print("      ---------")
    
    elif choice == "3":
        website = input("Enter website to search: ")
        found = False
        for account in accounts:
            if account[0].lower() == website.lower():
                print("website:", account[0])
                print("Username:", account[1])
                print("Password: **********")
                found = True
                break
            if not found:
                print("Account not found!")
    elif choice == "4":
        website = input("Enter website to update: ")
        found = False
        for account in accounts:
            if account[0].lower() == website.lower():
                found = True
                username = input("Enter new username: ")
                password = input("Enter new password: ")
                account[1] = username
                account[2] = password
                with open("accounts.txt", "w") as file:
                    for account in accounts:
                        file.write(f"{account[0]}|{account[1]}|{encrypt_password(account[2])}\n")
                print("Account updated successfully!")
                break
            if not found:
                print("Account not found!")
    elif choice == "5":
        website = input("Enter website to delete: ")
        for account in accounts:
            if account[0].lower() == website.lower():
                confirm = input("Are you sure you want to delete this account? (yes/no): ")
            if confirm.lower() == "yes":
                accounts.remove(account)
                with open("accounts.txt", "w") as file:
                    for account in accounts:
                        file.write(f"{account[0]}|{account[1]}|{encrypt_password(account[2])}\n")
                print("Account deleted successfully!")
            else:
                print("Deletion cancelled!")
            break
    elif choice == "6":
        print("Generate Password")
        length = int(input("Enter password length (minimum 6): "))
        if length < 6:
            print("Password length must be atleast 6!: ")
            continue
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%!"
        password = ""
        for i in range(length):
            password += random.choice(characters)
        print("Generated password:", password)
        print("Password length:", len(password))
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "@#$%!" for char in password)
        strength = 0
        if len(password) >= 12:
            strength += 1
        if has_upper:
            strength += 1
        if has_lower:
            strength += 1
        if has_digit:
            strength += 1
        if has_special:
            strength += 1
        if strength >= 5:
            print("Password strength: Strong")
        elif strength >= 3:
            print("Password strength: Medium")
        else:
            print("Password strength: Weak")

    elif choice == "7":
        print("Password Strength Checker")
        password = getpass.getpass("Enter password to check: ")
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in "@#$%!" for char in password)
        strength = 0
        if len(password) >= 12:
            strength += 1
        if has_upper:
            strength += 1
        if has_lower:
            strength += 1
        if has_digit:
            strength += 1
        if has_special:
            strength += 1
        if strength >= 5:
            print("Password strength: Strong")
        elif strength >= 3:
            print("Password strength: Medium")
        else:
            print("Password strength: Weak")
        
    elif choice == "8":
        print("Goodbye!")
        break
    elif choice == "9":
        new_password = getpass.getpass("Enter new master password: ")
        confirm_password = getpass.getpass("Confirm new  master password: ")
        if new_password == confirm_password:
            master_password = new_password
            with open("master_password.txt", "w") as file:
                file.write(master_password)
            print("Master password changed successfully!")
        else:
            print("Passwords do not match!")
            
        
    

        

        