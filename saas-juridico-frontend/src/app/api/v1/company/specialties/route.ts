import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    
    // Obter token de autenticação do header
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Token de autenticação necessário' },
        { status: 401 }
      );
    }
    
    // Se um ID foi fornecido, retorna a especialidade específica
    if (id) {
      console.log('Buscando especialidade com ID:', id);
      const response = await fetch(`${BACKEND_URL}/api/v1/company/specialties/${id}`, {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          return NextResponse.json(
            { error: 'Especialidade não encontrada' },
            { status: 404 }
          );
        }
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }
      
      const specialty = await response.json();
      console.log('Especialidade encontrada:', specialty.name);
      return NextResponse.json(specialty);
    }
    
    // Caso contrário, retorna todas as especialidades
    const response = await fetch(`${BACKEND_URL}/api/v1/company/specialties`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`);
    }
    
    const specialties = await response.json();
    return NextResponse.json(specialties);
  } catch (error) {
    console.error('Erro ao buscar especialidades:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Obter token de autenticação do header
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Token de autenticação necessário' },
        { status: 401 }
      );
    }
    
    const response = await fetch(`${BACKEND_URL}/api/v1/company/specialties`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Erro ao criar especialidade' },
        { status: response.status }
      );
    }
    
    const newSpecialty = await response.json();
    return NextResponse.json(newSpecialty, { status: 201 });
  } catch (error) {
    console.error('Erro ao criar especialidade:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, ...updateData } = body;
    
    console.log('Atualizando especialidade:', { id, updateData });
    
    // Obter token de autenticação do header
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Token de autenticação necessário' },
        { status: 401 }
      );
    }
    
    const response = await fetch(`${BACKEND_URL}/api/v1/company/specialties/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Especialidade não encontrada' },
          { status: 404 }
        );
      }
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Erro ao atualizar especialidade' },
        { status: response.status }
      );
    }
    
    const updatedSpecialty = await response.json();
    console.log('Especialidade atualizada com sucesso');
    return NextResponse.json(updatedSpecialty);
  } catch (error) {
    console.error('Erro ao atualizar especialidade:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    
    console.log('Excluindo especialidade com ID:', id);
    
    if (!id) {
      return NextResponse.json(
        { error: 'ID da especialidade é obrigatório' },
        { status: 400 }
      );
    }
    
    // Obter token de autenticação do header
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Token de autenticação necessário' },
        { status: 401 }
      );
    }
    
    const response = await fetch(`${BACKEND_URL}/api/v1/company/specialties/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Especialidade não encontrada' },
          { status: 404 }
        );
      }
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Erro ao excluir especialidade' },
        { status: response.status }
      );
    }
    
    const result = await response.json();
    console.log('Especialidade excluída com sucesso');
    return NextResponse.json(result);
  } catch (error) {
    console.error('Erro ao excluir especialidade:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}
