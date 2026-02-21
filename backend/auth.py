# Subissue - Encriptar contraseñas
#import section 
import hashlib

def hash_password(password): #firma de la función

    salt        =   b'some_salt' #salt para agregar seguridad a la contraseña
    
    pwd_salt    =   password+salt.decode("utf-8")  

    digest      =   hashlib.sha256(pwd_salt.encode())

    return digest.hexdigest()


def verify_password_hash(password, reference_hash):

    return hash_password(password) == reference_hash
