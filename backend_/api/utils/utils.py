from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pass(password:str) -> str:
    """
    Hashes the provided password using the configured CryptContext.

    Parameters:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(non_hashed_pass, hashed_pass):
    """
    Verifies if the non-hashed password matches the provided hashed password using the configured CryptContext.

    Parameters:
        non_hashed_pass (str): The non-hashed password to be verified.
        hashed_pass (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(non_hashed_pass, hashed_pass)


def is_strong_password(password: str) -> bool:
    """
    Checks if the provided password is strong.

    The password is considered strong if it contains at least one digit and one special character.

    Parameters:
        password (str): The password to be checked.

    Returns:
        bool: True if the password is strong, False otherwise.
    """
    return any(char.isdigit() for char in password) and any(char.isascii() and not char.isalnum() for char in password)