from aes import encrypt

password = input('Password: ')
print(encrypt(password).decode("utf-8"))
