"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Building,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  Clock
} from "lucide-react";
import { useCNJIntegration } from "@/hooks/useCNJIntegration";
import { toast } from "sonner";

interface CNJStats {
  total_processos: number;
  processos_sincronizados: number;
  processos_pendentes: number;
  ultima_sincronizacao: string;
  taxa_sucesso: number;
}

export function CNJStatsCard() {
  const [stats, setStats] = useState<CNJStats | null>(null);
  const [loading, setLoading] = useState(false);
  const { sincronizarProcesso } = useCNJIntegration();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/company/processes/cnj/stats', {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Erro ao buscar estatísticas CNJ:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAll = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/company/processes/cnj/sync-all', {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        toast.success("Sincronização em massa iniciada!");
        // Recarregar estatísticas após alguns segundos
        setTimeout(fetchStats, 3000);
      } else {
        toast.error("Erro ao iniciar sincronização em massa");
      }
    } catch (error) {
      console.error("Erro ao sincronizar todos os processos:", error);
      toast.error("Erro ao sincronizar processos");
    } finally {
      setLoading(false);
    }
  };

  if (!stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building className="w-5 h-5" />
            Integração CNJ
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Clock className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Building className="w-5 h-5" />
            Integração CNJ
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSyncAll}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Sincronizar Todos
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Estatísticas Gerais */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {stats.total_processos}
            </div>
            <div className="text-sm text-gray-600">Total de Processos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {stats.processos_sincronizados}
            </div>
            <div className="text-sm text-gray-600">Sincronizados</div>
          </div>
        </div>

        {/* Taxa de Sucesso */}
        <div className="text-center">
          <div className="text-3xl font-bold text-purple-600">
            {stats.taxa_sucesso}%
          </div>
          <div className="text-sm text-gray-600">Taxa de Sucesso</div>
        </div>

        {/* Status dos Processos */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm">Processos Sincronizados</span>
            </div>
            <Badge variant="default" className="text-xs">
              {stats.processos_sincronizados}
            </Badge>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
              <span className="text-sm">Processos Pendentes</span>
            </div>
            <Badge variant="secondary" className="text-xs">
              {stats.processos_pendentes}
            </Badge>
          </div>
        </div>

        {/* Última Sincronização */}
        {stats.ultima_sincronizacao && (
          <div className="text-center pt-2 border-t">
            <div className="text-xs text-gray-500">
              Última sincronização: {new Date(stats.ultima_sincronizacao).toLocaleString('pt-BR')}
            </div>
          </div>
        )}

        {/* Indicador de Tendência */}
        <div className="flex items-center justify-center gap-2 text-sm text-green-600">
          <TrendingUp className="w-4 h-4" />
          <span>Sincronização automática ativa</span>
        </div>
      </CardContent>
    </Card>
  );
}
