#!/usr/bin/env python3
"""
Script para verificar se o hash da senha está correto
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from core.database import SessionLocal
from core.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

def verify_password_hash():
    """Verifica se o hash da senha está correto"""
    db = SessionLocal()
    
    try:
        print("🔍 Verificando hash da senha...")
        
        # Buscar o usuário owner
        user = db.query(User).filter(User.email == "maria-1755302373@escritorioteste.com").first()
        
        if not user:
            print("❌ Usuário não encontrado")
            return
        
        print(f"   Usuário: {user.name} ({user.email})")
        print(f"   Hash da senha: {user.password_hash}")
        print(f"   Tamanho do hash: {len(user.password_hash)}")
        
        # Testar verificação da senha com werkzeug
        test_password = "123456"
        is_valid = check_password_hash(user.password_hash, test_password)
        
        print(f"   Senha '123456' é válida (werkzeug): {is_valid}")
        
        if is_valid:
            print("✅ Hash da senha está correto!")
        else:
            print("❌ Hash da senha está incorreto!")
            
            # Tentar gerar um novo hash com werkzeug
            new_hash = generate_password_hash(test_password)
            print(f"   Novo hash gerado (werkzeug): {new_hash}")
            
            # Atualizar o hash no banco
            user.password_hash = new_hash
            db.commit()
            print("✅ Hash da senha atualizado no banco!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_password_hash()
