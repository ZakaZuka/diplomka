import random
import string
from eth_account.messages import encode_defunct
from web3 import Web3

def generate_nonce(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def verify_signature(address, signature, nonce):
    w3 = Web3()
    message = encode_defunct(text=nonce)
    try:
        recovered_address = w3.eth.account.recover_message(message, signature=signature)
        return recovered_address.lower() == address.lower()
    except Exception:
        return False
