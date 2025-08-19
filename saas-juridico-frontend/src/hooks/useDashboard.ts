import { useState, useEffect } from 'react';
import { toast } from 'sonner';

interface DashboardStats {
  totalProcesses: number;
  activeProcesses: number;
  urgentDeadlines: number;
  pendingTasks: number;
  completionRate: number;
  totalClients: number;
  monthlyRevenue: number;
}

interface ProcessDeadline {
  id: string;
  title: string;
  due_date: string;
  process_id: string;
  process_subject: string;
  days_left: number;
  status: 'pending' | 'overdue' | 'completed';
}

interface RecentActivity {
  id: string;
  type: 'process_created' | 'deadline_added' | 'document_uploaded' | 'client_added';
  title: string;
  description: string;
  timestamp: string;
  process_id?: string;
}

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalProcesses: 0,
    activeProcesses: 0,
    urgentDeadlines: 0,
    pendingTasks: 0,
    completionRate: 0,
    totalClients: 0,
    monthlyRevenue: 0
  });
  
  const [urgentDeadlines, setUrgentDeadlines] = useState<ProcessDeadline[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        // Se não há token, não tentar carregar dados
        setLoading(false);
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };

      // Carregar estatísticas do dashboard
      const statsResponse = await fetch('/api/v1/company/dashboard/stats', { headers });
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.dashboard);
      }

      // Carregar prazos urgentes
      const deadlinesResponse = await fetch('/api/v1/company/dashboard/urgent-deadlines', { headers });
      if (deadlinesResponse.ok) {
        const deadlinesData = await deadlinesResponse.json();
        setUrgentDeadlines(deadlinesData);
      }

      // Carregar atividades recentes
      const activitiesResponse = await fetch('/api/v1/company/dashboard/recent-activities', { headers });
      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json();
        setRecentActivities(activitiesData);
      }

    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
      setError(error instanceof Error ? error.message : 'Erro desconhecido');
      toast.error('Erro ao carregar dados do dashboard');
    } finally {
      setLoading(false);
    }
  };

  const refreshDashboard = async () => {
    await loadDashboardData();
    toast.success('Dashboard atualizado!');
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return {
    stats,
    urgentDeadlines,
    recentActivities,
    loading,
    error,
    refreshDashboard,
    loadDashboardData
  };
}
