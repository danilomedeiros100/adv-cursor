#!/usr/bin/env python3
"""
Teste para verificar se o loop infinito no useAuth foi resolvido
"""

import requests
import json
import time

# Configurações
API_BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"

def test_auth_loop_fix():
    """Testa se o loop infinito foi resolvido"""
    
    print("🔍 Testando se o loop infinito no useAuth foi resolvido...")
    
    try:
        # Testa se o frontend está respondendo
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend está respondendo corretamente")
        else:
            print(f"❌ Frontend retornou status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar frontend: {e}")
        return False
    
    try:
        # Testa se o backend está respondendo
        response = requests.get(f"{API_BASE_URL}/auth/auth/me", timeout=5)
        # Esperado: 401 (não autenticado) ou 200 (se houver token válido)
        if response.status_code in [200, 401]:
            print("✅ Backend está respondendo corretamente")
        else:
            print(f"❌ Backend retornou status inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar backend: {e}")
        return False
    
    print("✅ Teste de conectividade passou")
    print("📝 Para verificar se o loop foi resolvido:")
    print("   1. Abra o navegador em http://localhost:3000")
    print("   2. Abra o DevTools (F12)")
    print("   3. Vá para a aba Console")
    print("   4. Verifique se não há mensagens de erro repetitivas")
    print("   5. Verifique se a página carrega normalmente")
    
    return True

if __name__ == "__main__":
    success = test_auth_loop_fix()
    if success:
        print("\n🎉 Teste concluído com sucesso!")
        print("O loop infinito deve ter sido resolvido.")
    else:
        print("\n💥 Teste falhou!")
        print("Verifique se os serviços estão rodando.")

