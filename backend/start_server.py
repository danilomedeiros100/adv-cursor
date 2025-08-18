#!/usr/bin/env python3
"""
Script para iniciar o servidor de forma robusta
"""
import os
import sys
import subprocess
import time
import signal
import psutil

def kill_process_on_port(port):
    """Mata processos na porta especificada"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        print(f"Matando processo {proc.pid} na porta {port}")
                        proc.kill()
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"Erro ao matar processos: {e}")

def check_port_available(port):
    """Verifica se a porta está disponível"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def start_server(port=8000):
    """Inicia o servidor"""
    print(f"🚀 Iniciando servidor na porta {port}...")
    
    # Mata processos na porta
    kill_process_on_port(port)
    
    # Verifica se a porta está livre
    if not check_port_available(port):
        print(f"❌ Porta {port} ainda não está disponível")
        return False
    
    # Inicia o servidor
    try:
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", str(port),
            "--reload"
        ]
        
        print(f"Executando: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        # Aguarda um pouco para o servidor inicializar
        time.sleep(5)
        
        # Verifica se o processo ainda está rodando
        if process.poll() is None:
            print(f"✅ Servidor iniciado com sucesso na porta {port}")
            return True
        else:
            print(f"❌ Servidor falhou ao iniciar")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

if __name__ == "__main__":
    # Tenta portas diferentes se necessário
    ports = [8000, 8001, 8002]
    
    for port in ports:
        print(f"\n--- Tentando porta {port} ---")
        if start_server(port):
            print(f"🎉 Servidor rodando em http://localhost:{port}")
            print("Pressione Ctrl+C para parar")
            
            try:
                # Mantém o processo rodando
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Parando servidor...")
                break
        else:
            print(f"❌ Falha na porta {port}")
    
    print("❌ Não foi possível iniciar o servidor em nenhuma porta")
