from DBConnection import DBConnection
from DatabaseService import DatabaseService
import hashlib

import hashlib

def generate_variant_key(kwargs: dict = {}) -> str:
    """
    Generate a unique key to identify candidate alterations.
    
    Args:
        kwargs (dict): A dictionary of alterations.

    Returns:
        str: A unique SHA256 hash representing the alterations.
    """
    
    alterations = "&".join(f"{key}={value}" for key, value in sorted(kwargs.items()))
    return hashlib.sha256(alterations.encode()).hexdigest()

def store_or_fetch_variant_key(db: DBConnection, kwargs: dict) -> str:
    """
    Generate or retrieve a Variant_Key for the given alterations.

    Args:
        db (DBConnection): The database connection object.
        kwargs (dict): A dictionary of alterations.

    Returns:
        str: The existing or newly created Variant_Key.
    """
    alterations = "&".join(f"{key}={value}" for key, value in sorted(kwargs.items()))
    
    # Check if the alterations exist in the database
    variant_key = DatabaseService.get_alterations(db, alterations)
    if not variant_key:
        # Generate a new Variant_Key and save it to the database
        variant_key = generate_variant_key(kwargs)
        DatabaseService.save_alterations(db, variant_key, alterations)
    
    return variant_key