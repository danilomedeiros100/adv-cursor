-- Criar banco de dados
CREATE DATABASE saas_juridico;

-- Conectar ao banco
\c saas_juridico;

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
