"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  DollarSign, 
  Plus, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  FileText
} from "lucide-react";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";

interface ProcessFinancial {
  id: string;
  type: 'fee' | 'expense' | 'payment' | 'refund';
  title: string;
  description?: string;
  amount: number; // Em centavos
  due_date?: string;
  paid_date?: string;
  status: 'pending' | 'paid' | 'overdue' | 'cancelled';
  category?: string;
  receipt_url?: string;
  created_by: {
    id: string;
    name: string;
  };
  created_at: string;
  updated_at?: string;
}

interface ProcessFinancialProps {
  processId: string;
}

export function ProcessFinancial({ processId }: ProcessFinancialProps) {
  const [financialRecords, setFinancialRecords] = useState<ProcessFinancial[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFinancialRecords();
  }, [processId]);

  const loadFinancialRecords = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.log("Token não encontrado, não carregando dados financeiros");
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/v1/company/processes/${processId}/financial`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const financialData = await response.json();
        setFinancialRecords(financialData);
      } else {
        throw new Error('Erro ao carregar dados financeiros');
      }
    } catch (error) {
      console.error("Erro ao carregar registros financeiros:", error);
      toast.error("Erro ao carregar registros financeiros");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value / 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'fee':
        return 'Honorários';
      case 'expense':
        return 'Despesa';
      case 'payment':
        return 'Pagamento';
      case 'refund':
        return 'Reembolso';
      default:
        return type;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pendente';
      case 'paid':
        return 'Pago';
      case 'overdue':
        return 'Atrasado';
      case 'cancelled':
        return 'Cancelado';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'secondary';
      case 'paid':
        return 'default';
      case 'overdue':
        return 'destructive';
      case 'cancelled':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  // Calcular totais
  const totalIncome = financialRecords
    .filter(r => r.type === 'fee' || r.type === 'payment')
    .reduce((sum, r) => sum + r.amount, 0);

  const totalExpenses = financialRecords
    .filter(r => r.type === 'expense')
    .reduce((sum, r) => sum + r.amount, 0);

  const balance = totalIncome - totalExpenses;

  if (loading) {
    return <Loading message="Carregando dados financeiros..." />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Financeiro do Processo</h2>
          <p className="text-sm text-gray-600">
            Controle de receitas, despesas e pagamentos
          </p>
        </div>
        
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Novo Lançamento
        </Button>
      </div>

      {/* Resumo Financeiro */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Receitas</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(totalIncome)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Despesas</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(totalExpenses)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Saldo</CardTitle>
            <DollarSign className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(balance)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Lançamentos */}
      <Card>
        <CardHeader>
          <CardTitle>Lançamentos</CardTitle>
        </CardHeader>
        <CardContent>
          {financialRecords.length === 0 ? (
            <div className="text-center py-8">
              <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum lançamento registrado
              </h3>
              <p className="text-gray-600 mb-4">
                Comece registrando o primeiro lançamento financeiro.
              </p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Primeiro Lançamento
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {financialRecords.map((record) => (
                <FinancialRecordItem key={record.id} record={record} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface FinancialRecordItemProps {
  record: ProcessFinancial;
}

function FinancialRecordItem({ record }: FinancialRecordItemProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value / 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'fee':
        return 'Honorários';
      case 'expense':
        return 'Despesa';
      case 'payment':
        return 'Pagamento';
      case 'refund':
        return 'Reembolso';
      default:
        return type;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pendente';
      case 'paid':
        return 'Pago';
      case 'overdue':
        return 'Atrasado';
      case 'cancelled':
        return 'Cancelado';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'secondary';
      case 'paid':
        return 'default';
      case 'overdue':
        return 'destructive';
      case 'cancelled':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  const isIncome = record.type === 'fee' || record.type === 'payment';

  return (
    <div className="flex items-center justify-between p-4 border rounded-lg">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-2">
          <Badge variant="outline" className="text-xs">
            {getTypeLabel(record.type)}
          </Badge>
          <Badge variant={getStatusColor(record.status)} className="text-xs">
            {getStatusLabel(record.status)}
          </Badge>
        </div>
        
        <h3 className="font-medium text-gray-900 mb-1">
          {record.title}
        </h3>
        
        {record.description && (
          <p className="text-sm text-gray-600 mb-2">
            {record.description}
          </p>
        )}
        
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <span>Por: {record.created_by.name}</span>
          <span>Criado: {formatDate(record.created_at)}</span>
          {record.due_date && (
            <span>Vencimento: {formatDate(record.due_date)}</span>
          )}
          {record.paid_date && (
            <span>Pago: {formatDate(record.paid_date)}</span>
          )}
        </div>
      </div>
      
      <div className="text-right">
        <div className={`text-lg font-bold ${isIncome ? 'text-green-600' : 'text-red-600'}`}>
          {isIncome ? '+' : '-'}{formatCurrency(record.amount)}
        </div>
      </div>
    </div>
  );
}
