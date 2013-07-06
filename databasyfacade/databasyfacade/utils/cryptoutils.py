from flask import current_app
from pyDes import triple_des

__author__ = 'Marboni'

def encrypt(message):
    return triple_des(current_app.config['SECRET_KEY']).encrypt(message, padmode=2)

def decrypt(encrypted_message):
    return triple_des(current_app.config['SECRET_KEY']).decrypt(encrypted_message, padmode=2)
