#!/usr/bin/env python3
"""
Script de diagnóstico para verificar o status do sistema
"""
import os
import sys
import subprocess
import time

def check_database():
    """Verifica conexão com banco de dados"""
    print("🔍 Verificando banco de dados...")
    try:
        from core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco OK")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def check_imports():
    """Verifica se todas as importações estão funcionando"""
    print("🔍 Verificando importações...")
    try:
        import main
        print("✅ Importação do main.py OK")
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def check_ports():
    """Verifica portas em uso"""
    print("🔍 Verificando portas...")
    import socket
    
    ports = [8000, 8001, 8002]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Porta {port} está em uso")
        else:
            print(f"✅ Porta {port} está livre")

def check_processes():
    """Verifica processos Python rodando"""
    print("🔍 Verificando processos...")
    try:
        import psutil
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'uvicorn' in cmdline or 'main:app' in cmdline:
                        python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print("⚠️  Processos Python encontrados:")
            for proc in python_processes:
                print(f"   PID {proc['pid']}: {' '.join(proc['cmdline'])}")
        else:
            print("✅ Nenhum processo Python rodando")
            
    except ImportError:
        print("⚠️  psutil não instalado, não é possível verificar processos")

def test_server_startup():
    """Testa se o servidor consegue iniciar"""
    print("🔍 Testando inicialização do servidor...")
    try:
        # Tenta importar e criar a aplicação
        from main import app
        print("✅ Aplicação criada com sucesso")
        
        # Testa se as rotas estão registradas
        routes = [route.path for route in app.routes]
        print(f"✅ {len(routes)} rotas registradas")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar aplicação: {e}")
        return False

def main():
    """Executa diagnóstico completo"""
    print("🔧 DIAGNÓSTICO DO SISTEMA")
    print("=" * 50)
    
    # Verificações
    db_ok = check_database()
    imports_ok = check_imports()
    test_server_startup()
    check_ports()
    check_processes()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO:")
    
    if db_ok and imports_ok:
        print("✅ Sistema básico OK")
        print("💡 Para iniciar o servidor, execute:")
        print("   python start_server.py")
    else:
        print("❌ Problemas detectados no sistema")
        print("💡 Verifique as configurações do banco de dados")

if __name__ == "__main__":
    main()
