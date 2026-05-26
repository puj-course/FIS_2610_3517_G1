import hashlib
salt = b'some_salt'
password = "Admin123"
pwd_salt = password + salt.decode("utf-8")
print(hashlib.sha256(pwd_salt.encode()).hexdigest())