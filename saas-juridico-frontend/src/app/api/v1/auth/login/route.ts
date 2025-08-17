import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('🔐 API Login: Iniciando requisição');
    
    const body = await request.json();
    console.log('🔐 API Login: Dados recebidos:', { email: body.email, tenant_slug: body.tenant_slug });
    
    // Teste simples - retornar sucesso
    return NextResponse.json({
      access_token: "test-token",
      token_type: "bearer",
      expires_in: 1800,
      user: {
        id: "test-user-id",
        name: "Test User",
        email: body.email,
        is_super_admin: false
      },
      tenant: {
        id: "test-tenant-id",
        name: "Test Tenant",
        slug: body.tenant_slug
      }
    });
    
  } catch (error) {
    console.error('🔐 API Login: Erro no proxy de login:', error);
    return NextResponse.json(
      { detail: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}
