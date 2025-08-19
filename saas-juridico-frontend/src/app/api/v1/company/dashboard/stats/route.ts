import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Token de autenticação necessário' },
        { status: 401 }
      );
    }

    // Buscar estatísticas de processos
    const processesResponse = await fetch(`${BACKEND_URL}/api/v1/company/processes/stats/summary`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    // Buscar estatísticas de clientes
    const clientsResponse = await fetch(`${BACKEND_URL}/api/v1/company/clients/stats/summary`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    // Buscar estatísticas de usuários
    const usersResponse = await fetch(`${BACKEND_URL}/api/v1/company/users/stats/summary`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    // Buscar estatísticas de especialidades
    const specialtiesResponse = await fetch(`${BACKEND_URL}/api/v1/company/specialties/stats/summary`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    // Processar respostas
    const processesStats = processesResponse.ok ? await processesResponse.json() : {};
    const clientsStats = clientsResponse.ok ? await clientsResponse.json() : {};
    const usersStats = usersResponse.ok ? await usersResponse.json() : {};
    const specialtiesStats = specialtiesResponse.ok ? await specialtiesResponse.json() : {};

    // Combinar estatísticas
    const combinedStats = {
      processes: processesStats,
      clients: clientsStats,
      users: usersStats,
      specialties: specialtiesStats,
      dashboard: {
        totalProcesses: processesStats.total_processes || 0,
        activeProcesses: processesStats.active_processes || 0,
        urgentDeadlines: processesStats.urgent_processes || 0,
        pendingTasks: 0, // Será calculado dinamicamente
        completionRate: processesStats.completion_rate || 0,
        totalClients: clientsStats.total_clients || 0,
        monthlyRevenue: 0, // Será implementado quando tivermos dados financeiros
      }
    };

    return NextResponse.json(combinedStats);
  } catch (error) {
    console.error('Erro ao buscar estatísticas do dashboard:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}
