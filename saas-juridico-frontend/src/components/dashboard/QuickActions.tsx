import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Plus,
  FileText,
  Calendar,
  Upload,
  Users,
  Settings,
  Search,
  Zap
} from "lucide-react";

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  action: () => void;
}

interface QuickActionsProps {
  onAction?: (actionId: string) => void;
}

export function QuickActions({ onAction }: QuickActionsProps) {
  const actions: QuickAction[] = [
    {
      id: 'new-process',
      title: 'Novo Processo',
      description: 'Criar novo processo jurídico',
      icon: <Plus className="h-6 w-6" />,
      color: 'blue',
      action: () => onAction?.('new-process')
    },
    {
      id: 'new-petition',
      title: 'Nova Petição',
      description: 'Criar nova petição',
      icon: <FileText className="h-6 w-6" />,
      color: 'green',
      action: () => onAction?.('new-petition')
    },
    {
      id: 'new-deadline',
      title: 'Novo Prazo',
      description: 'Adicionar novo prazo',
      icon: <Calendar className="h-6 w-6" />,
      color: 'orange',
      action: () => onAction?.('new-deadline')
    },
    {
      id: 'upload-document',
      title: 'Upload Doc',
      description: 'Fazer upload de documento',
      icon: <Upload className="h-6 w-6" />,
      color: 'purple',
      action: () => onAction?.('upload-document')
    },
    {
      id: 'new-client',
      title: 'Novo Cliente',
      description: 'Cadastrar novo cliente',
      icon: <Users className="h-6 w-6" />,
      color: 'indigo',
      action: () => onAction?.('new-client')
    },
    {
      id: 'search-process',
      title: 'Buscar Processo',
      description: 'Pesquisar processos',
      icon: <Search className="h-6 w-6" />,
      color: 'teal',
      action: () => onAction?.('search-process')
    },
    {
      id: 'settings',
      title: 'Configurações',
      description: 'Ajustar configurações',
      icon: <Settings className="h-6 w-6" />,
      color: 'gray',
      action: () => onAction?.('settings')
    },
    {
      id: 'quick-actions',
      title: 'Ações Rápidas',
      description: 'Menu de ações rápidas',
      icon: <Zap className="h-6 w-6" />,
      color: 'yellow',
      action: () => onAction?.('quick-actions')
    }
  ];

  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: 'border-blue-200 hover:bg-blue-50 hover:border-blue-300 text-blue-700',
      green: 'border-green-200 hover:bg-green-50 hover:border-green-300 text-green-700',
      orange: 'border-orange-200 hover:bg-orange-50 hover:border-orange-300 text-orange-700',
      purple: 'border-purple-200 hover:bg-purple-50 hover:border-purple-300 text-purple-700',
      indigo: 'border-indigo-200 hover:bg-indigo-50 hover:border-indigo-300 text-indigo-700',
      teal: 'border-teal-200 hover:bg-teal-50 hover:border-teal-300 text-teal-700',
      gray: 'border-gray-200 hover:bg-gray-50 hover:border-gray-300 text-gray-700',
      yellow: 'border-yellow-200 hover:bg-yellow-50 hover:border-yellow-300 text-yellow-700'
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.gray;
  };

  const getIconBgColor = (color: string) => {
    const colorMap = {
      blue: 'bg-blue-500/10',
      green: 'bg-green-500/10',
      orange: 'bg-orange-500/10',
      purple: 'bg-purple-500/10',
      indigo: 'bg-indigo-500/10',
      teal: 'bg-teal-500/10',
      gray: 'bg-gray-500/10',
      yellow: 'bg-yellow-500/10'
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.gray;
  };

  const getIconColor = (color: string) => {
    const colorMap = {
      blue: 'text-blue-600',
      green: 'text-green-600',
      orange: 'text-orange-600',
      purple: 'text-purple-600',
      indigo: 'text-indigo-600',
      teal: 'text-teal-600',
      gray: 'text-gray-600',
      yellow: 'text-yellow-600'
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.gray;
  };

  return (
    <Card className="card-modern bg-white/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-xl font-semibold flex items-center">
          <Zap className="h-5 w-5 mr-2 text-blue-600" />
          Ações Rápidas
          <span className="ml-auto text-sm text-muted-foreground">
            {actions.length} ações disponíveis
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {actions.map((action) => (
            <Button 
              key={action.id}
              variant="outline" 
              className={`h-24 flex-col button-modern transition-all duration-200 ${getColorClasses(action.color)}`}
              onClick={action.action}
            >
              <div className={`p-2 rounded-lg mb-2 ${getIconBgColor(action.color)}`}>
                <div className={getIconColor(action.color)}>
                  {action.icon}
                </div>
              </div>
              <span className="text-sm font-medium">{action.title}</span>
              <span className="text-xs text-muted-foreground mt-1 text-center">
                {action.description}
              </span>
            </Button>
          ))}
        </div>
        
        {/* Seção de ações mais usadas */}
        <div className="mt-6 pt-6 border-t border-border/50">
          <h4 className="text-sm font-medium text-muted-foreground mb-3">Ações Mais Usadas</h4>
          <div className="flex flex-wrap gap-2">
            {actions.slice(0, 4).map((action) => (
              <Button
                key={`quick-${action.id}`}
                size="sm"
                variant="ghost"
                className={`text-xs ${getColorClasses(action.color)}`}
                onClick={action.action}
              >
                <div className={`p-1 rounded mr-1 ${getIconBgColor(action.color)}`}>
                  <div className={`w-3 h-3 ${getIconColor(action.color)}`}>
                    {action.icon}
                  </div>
                </div>
                {action.title}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
