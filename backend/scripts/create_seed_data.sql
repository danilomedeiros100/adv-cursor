-- Script SQL para criar dados iniciais do SaaS Jurídico

-- 1. Criar Super Admin
INSERT INTO super_admins (id, name, email, password_hash, is_active, created_at) VALUES (
    gen_random_uuid(),
    'Super Administrador',
    'admin@saasjuridico.com',
    'pbkdf2:sha256:600000$admin123$hash_placeholder',
    true,
    NOW()
);

-- 2. Criar Tenant demo
INSERT INTO tenants (id, name, slug, email, phone, plan_type, plan_features, max_users, max_processes, is_active, is_suspended, settings, branding, created_at) VALUES (
    gen_random_uuid(),
    'Escritório Demo',
    'demo',
    'contato@escritoriodemo.com',
    '(11) 99999-9999',
    'premium',
    '{"max_users": 50, "max_processes": 1000, "modules": ["clients", "processes", "documents", "financial", "notifications"]}',
    50,
    1000,
    true,
    false,
    '{"timezone": "America/Sao_Paulo", "language": "pt_BR", "currency": "BRL"}',
    '{"logo_url": null, "primary_color": "#3B82F6", "company_name": "Escritório Demo"}',
    NOW()
);

-- 3. Criar usuário admin da empresa
INSERT INTO users (id, name, email, password_hash, phone, oab_number, oab_state, position, department, is_active, is_super_admin, email_verified, phone_verified, preferences, timezone, language, created_at) VALUES (
    gen_random_uuid(),
    'João Silva',
    'joao@escritoriodemo.com',
    'pbkdf2:sha256:600000$123456$hash_placeholder',
    '(11) 88888-8888',
    '123456',
    'SP',
    'Sócio',
    'Administrativo',
    true,
    false,
    true,
    true,
    '{"theme": "light", "notifications": {"email": true, "push": true, "sms": false}}',
    'America/Sao_Paulo',
    'pt_BR',
    NOW()
);

-- 4. Criar usuário advogado
INSERT INTO users (id, name, email, password_hash, phone, oab_number, oab_state, position, department, is_active, is_super_admin, email_verified, phone_verified, preferences, timezone, language, created_at) VALUES (
    gen_random_uuid(),
    'Maria Santos',
    'maria@escritoriodemo.com',
    'pbkdf2:sha256:600000$123456$hash_placeholder',
    '(11) 77777-7777',
    '654321',
    'SP',
    'Advogada',
    'Civil',
    true,
    false,
    true,
    true,
    '{"theme": "light", "notifications": {"email": true, "push": true, "sms": false}}',
    'America/Sao_Paulo',
    'pt_BR',
    NOW()
);

-- 5. Criar roles padrão
INSERT INTO roles (id, name, display_name, description, default_permissions, can_manage_users, can_manage_financial, can_view_all_processes, can_manage_specialties, is_active, created_at) VALUES 
(gen_random_uuid(), 'admin', 'Administrador', 'Administrador da empresa', '{"users.manage": true, "financial.manage": true, "processes.view_all": true, "specialties.manage": true}', true, true, true, true, true, NOW()),
(gen_random_uuid(), 'lawyer', 'Advogado', 'Advogado da empresa', '{"processes.create": true, "processes.read": true, "processes.update": true, "clients.create": true, "clients.read": true, "clients.update": true, "documents.create": true, "documents.read": true}', false, false, false, false, true, NOW()),
(gen_random_uuid(), 'assistant', 'Assistente', 'Assistente jurídico', '{"processes.read": true, "clients.read": true, "documents.read": true}', false, false, false, false, true, NOW());

-- 6. Associar usuários aos tenants (usando tenant_users)
-- Primeiro, vamos pegar os IDs dos usuários e tenant criados
DO $$
DECLARE
    admin_user_id UUID;
    lawyer_user_id UUID;
    demo_tenant_id UUID;
    admin_role_id UUID;
    lawyer_role_id UUID;
BEGIN
    -- Pegar IDs
    SELECT id INTO admin_user_id FROM users WHERE email = 'joao@escritoriodemo.com';
    SELECT id INTO lawyer_user_id FROM users WHERE email = 'maria@escritoriodemo.com';
    SELECT id INTO demo_tenant_id FROM tenants WHERE slug = 'demo';
    SELECT id INTO admin_role_id FROM roles WHERE name = 'admin';
    SELECT id INTO lawyer_role_id FROM roles WHERE name = 'lawyer';
    
    -- Associar admin ao tenant
    INSERT INTO tenant_users (id, tenant_id, user_id, role, permissions, department, position, is_active, is_primary_admin, created_at) VALUES (
        gen_random_uuid(),
        demo_tenant_id,
        admin_user_id,
        'admin',
        '{"users.manage": true, "financial.manage": true, "processes.view_all": true}',
        'Administrativo',
        'Sócio',
        true,
        true,
        NOW()
    );
    
    -- Associar advogada ao tenant
    INSERT INTO tenant_users (id, tenant_id, user_id, role, permissions, department, position, is_active, is_primary_admin, created_at) VALUES (
        gen_random_uuid(),
        demo_tenant_id,
        lawyer_user_id,
        'lawyer',
        '{"processes.create": true, "processes.read": true, "processes.update": true, "clients.create": true, "clients.read": true, "clients.update": true}',
        'Civil',
        'Advogada',
        true,
        false,
        NOW()
    );
END $$;

-- 7. Criar especialidades jurídicas
DO $$
DECLARE
    demo_tenant_id UUID;
    admin_user_id UUID;
BEGIN
    SELECT id INTO demo_tenant_id FROM tenants WHERE slug = 'demo';
    SELECT id INTO admin_user_id FROM users WHERE email = 'joao@escritoriodemo.com';
    
    INSERT INTO legal_specialties (id, tenant_id, name, code, description, is_active, requires_oab, created_by, created_at) VALUES 
    (gen_random_uuid(), demo_tenant_id, 'Direito Civil', 'CIVIL', 'Direito Civil e Contratual', true, true, admin_user_id, NOW()),
    (gen_random_uuid(), demo_tenant_id, 'Direito Trabalhista', 'TRABALHISTA', 'Direito do Trabalho', true, true, admin_user_id, NOW()),
    (gen_random_uuid(), demo_tenant_id, 'Direito Empresarial', 'EMPRESARIAL', 'Direito Empresarial e Societário', true, true, admin_user_id, NOW());
END $$;
