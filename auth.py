"""
AUTENTICAÇÃO - WebStruct Analyzer
Gerencia login, registro e hash de senhas
"""

import bcrypt
import os


def hash_senha(senha):
    """Gera hash da senha usando bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode("utf-8"), salt).decode("utf-8")


def verificar_senha(senha, hash_salvo):
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(senha.encode("utf-8"), hash_salvo.encode("utf-8"))
