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

    // Buscar todos os processos para verificar prazos
    const processesResponse = await fetch(`${BACKEND_URL}/api/v1/company/processes`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    if (!processesResponse.ok) {
      throw new Error(`Erro ao buscar processos: ${processesResponse.status}`);
    }

    const processes = await processesResponse.json();
    
    // Buscar prazos de cada processo
    const urgentDeadlines = [];
    
    for (const process of processes.slice(0, 10)) { // Limitar a 10 processos para performance
      try {
        const deadlinesResponse = await fetch(`${BACKEND_URL}/api/v1/company/processes/${process.id}/deadlines`, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
          },
        });

        if (deadlinesResponse.ok) {
          const deadlines = await deadlinesResponse.json();
          
          // Filtrar prazos urgentes (próximos 7 dias ou atrasados)
          const urgent = deadlines.filter((deadline: any) => {
            const dueDate = new Date(deadline.due_date);
            const today = new Date();
            const daysDiff = Math.ceil((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
            
            return daysDiff <= 7 && deadline.status !== 'completed';
          });

          urgent.forEach((deadline: any) => {
            const dueDate = new Date(deadline.due_date);
            const today = new Date();
            const daysDiff = Math.ceil((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
            
            urgentDeadlines.push({
              id: deadline.id,
              title: deadline.title,
              due_date: deadline.due_date,
              process_id: process.id,
              process_subject: process.subject,
              days_left: daysDiff,
              status: daysDiff < 0 ? 'overdue' : 'pending'
            });
          });
        }
      } catch (error) {
        console.error(`Erro ao buscar prazos do processo ${process.id}:`, error);
      }
    }

    // Ordenar por urgência (primeiro atrasados, depois por dias restantes)
    urgentDeadlines.sort((a, b) => {
      if (a.status === 'overdue' && b.status !== 'overdue') return -1;
      if (b.status === 'overdue' && a.status !== 'overdue') return 1;
      return a.days_left - b.days_left;
    });

    return NextResponse.json(urgentDeadlines.slice(0, 10)); // Retornar apenas os 10 mais urgentes
  } catch (error) {
    console.error('Erro ao buscar prazos urgentes:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
}
