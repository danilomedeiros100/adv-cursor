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

    // Buscar processos recentes
    const processesResponse = await fetch(`${BACKEND_URL}/api/v1/company/processes?limit=5`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    // Buscar clientes recentes
    const clientsResponse = await fetch(`${BACKEND_URL}/api/v1/company/clients?limit=5`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    const activities = [];

    // Processar processos recentes
    if (processesResponse.ok) {
      const processes = await processesResponse.json();
      processes.forEach((process: any) => {
        activities.push({
          id: `process_${process.id}`,
          type: 'process_created',
          title: 'Novo processo criado',
          description: `${process.subject} - ${process.client?.name || 'Cliente não informado'}`,
          timestamp: process.created_at,
          process_id: process.id
        });
      });
    }

    // Processar clientes recentes
    if (clientsResponse.ok) {
      const clients = await clientsResponse.json();
      clients.forEach((client: any) => {
        activities.push({
          id: `client_${client.id}`,
          type: 'client_added',
          title: 'Novo cliente cadastrado',
          description: `${client.name} - ${client.specialty?.name || 'Sem especialidade'}`,
          timestamp: client.created_at
        });
      });
    }

    // Buscar timeline de alguns processos para atividades mais recentes
    if (processesResponse.ok) {
      const processes = await processesResponse.json();
      
      for (const process of processes.slice(0, 3)) {
        try {
          const timelineResponse = await fetch(`${BACKEND_URL}/api/v1/company/processes/${process.id}/timeline?limit=3`, {
            headers: {
              'Authorization': authHeader,
              'Content-Type': 'application/json',
            },
          });

          if (timelineResponse.ok) {
            const timeline = await timelineResponse.json();
            timeline.forEach((event: any) => {
              activities.push({
                id: `timeline_${event.id}`,
                type: getActivityType(event.type),
                title: getActivityTitle(event.type),
                description: `${event.description} - ${process.subject}`,
                timestamp: event.occurred_at || event.created_at,
                process_id: process.id
              });
            });
          }
        } catch (error) {
          console.error(`Erro ao buscar timeline do processo ${process.id}:`, error);
        }
      }
    }

    // Ordenar por timestamp (mais recentes primeiro)
    activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    return NextResponse.json(activities.slice(0, 10)); // Retornar apenas as 10 atividades mais recentes
  } catch (error) {
    console.error('Erro ao buscar atividades recentes:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}

function getActivityType(eventType: string): string {
  switch (eventType) {
    case 'petition':
      return 'document_uploaded';
    case 'decision':
      return 'process_updated';
    case 'hearing':
      return 'deadline_added';
    case 'deadline':
      return 'deadline_added';
    case 'document':
      return 'document_uploaded';
    case 'note':
      return 'process_updated';
    default:
      return 'process_updated';
  }
}

function getActivityTitle(eventType: string): string {
  switch (eventType) {
    case 'petition':
      return 'Petição enviada';
    case 'decision':
      return 'Decisão publicada';
    case 'hearing':
      return 'Audiência marcada';
    case 'deadline':
      return 'Prazo adicionado';
    case 'document':
      return 'Documento enviado';
    case 'note':
      return 'Anotação adicionada';
    default:
      return 'Atividade registrada';
  }
}
