from werkzeug.security import generate_password_hash

password = input("Neues Passwort: ")
print(generate_password_hash(password))
