import secrets
import hashlib 
import os 

## create random salt of given size
def generate_rand_salt(size: int):
    return secrets.token_hex(size)

# salt is user specific 
# pepper is global
# using sha 256 algorithm
def hash_password(password: str, salt: bytes):
    # get pepper from os.environ
    pepper = os.environ["PASSWORD_PEPPER"].encode()
    hash_result = hashlib.sha256()
    hash_result.update(password.encode())
    hash_result.update(pepper)
    hash_result.update(salt.encode())
    return hash_result.hexdigest()


def check_password_match(inputPassword: str, passwordHash: str, salt: str):
    inputHash = hash_password(inputPassword, salt)
    if(inputHash == passwordHash):
        return True 
    else:
        return False