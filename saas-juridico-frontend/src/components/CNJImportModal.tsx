"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { 
  Search, 
  Download, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Building,
  FileText,
  Users,
  Calendar
} from "lucide-react";
import { toast } from "sonner";
import { useCNJIntegration, type CNJValidationResult, type CNJData } from "@/hooks/useCNJIntegration";

interface CNJImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (processId: string) => void;
}



export function CNJImportModal({ isOpen, onClose, onImport }: CNJImportModalProps) {
  const [cnjNumber, setCnjNumber] = useState("");
  const [validationResult, setValidationResult] = useState<CNJValidationResult | null>(null);
  const [cnjData, setCnjData] = useState<CNJData | null>(null);
  const [step, setStep] = useState<"input" | "validation" | "preview" | "importing">("input");
  
  const { loading, validateCNJ: validateCNJHook, consultarProcesso: consultarProcessoHook, importarProcesso: importarProcessoHook } = useCNJIntegration();

  const validateCNJ = async () => {
    if (!cnjNumber.trim()) {
      toast.error("Digite um número CNJ válido");
      return;
    }

    const result = await validateCNJHook(cnjNumber);
    if (result) {
      setValidationResult(result);
      if (result.valid) {
        setStep("validation");
        toast.success("Número CNJ válido!");
      } else {
        toast.error(`Número CNJ inválido: ${result.error}`);
      }
    }
  };

  const consultarProcesso = async () => {
    const data = await consultarProcessoHook(cnjNumber);
    if (data) {
      setCnjData(data);
      setStep("preview");
      toast.success("Processo encontrado na API CNJ!");
    }
  };

  const importarProcesso = async () => {
    setStep("importing");
    
    const processId = await importarProcessoHook(cnjNumber);
    if (processId) {
      onImport(processId);
      onClose();
      resetModal();
    } else {
      setStep("preview");
    }
  };

  const resetModal = () => {
    setCnjNumber("");
    setValidationResult(null);
    setCnjData(null);
    setStep("input");
  };

  const handleClose = () => {
    resetModal();
    onClose();
  };

  const formatCNJ = (cnj: string) => {
    const clean = cnj.replace(/\D/g, '');
    if (clean.length >= 20) {
      return `${clean.slice(0, 7)}-${clean.slice(7, 9)}.${clean.slice(9, 13)}.${clean.slice(13, 14)}.${clean.slice(14, 16)}.${clean.slice(16, 20)}`;
    }
    return cnj;
  };

  const formatCurrency = (value: string) => {
    if (!value) return "Não informado";
    const num = parseFloat(value.replace(/[^\d,.-]/g, '').replace(',', '.'));
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(num);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "Não informado";
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  // Função utilitária para extrair valor de campo que pode ser string ou objeto
  const extractValue = (field: any): string => {
    if (typeof field === 'string') return field;
    if (typeof field === 'object' && field?.nome) return field.nome;
    if (typeof field === 'object' && field?.codigo) return field.codigo;
    return "Não informado";
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="w-5 h-5" />
            Importar Processo do CNJ
          </DialogTitle>
        </DialogHeader>

        {/* Step 1: Input do número CNJ */}
        {step === "input" && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Número do Processo (CNJ)
              </label>
              <div className="flex gap-2">
                <Input
                  placeholder="0000000-00.0000.0.00.0000"
                  value={cnjNumber}
                  onChange={(e) => setCnjNumber(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && validateCNJ()}
                />
                <Button 
                  onClick={validateCNJ} 
                  disabled={loading || !cnjNumber.trim()}
                >
                  {loading ? (
                    <Clock className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  Validar
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Digite o número do processo no formato CNJ (20 dígitos)
              </p>
            </div>
          </div>
        )}

        {/* Step 2: Validação */}
        {step === "validation" && validationResult && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Número CNJ Válido
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Tribunal</label>
                    <p className="text-sm text-gray-600">
                      {validationResult.tribunal?.nome}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Número Formatado</label>
                    <p className="text-sm text-gray-600 font-mono">
                      {validationResult.numero_formatado}
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <label className="font-medium">Sequencial</label>
                    <p className="text-gray-600">{validationResult.componentes?.sequencial}</p>
                  </div>
                  <div>
                    <label className="font-medium">Ano</label>
                    <p className="text-gray-600">{validationResult.componentes?.ano}</p>
                  </div>
                  <div>
                    <label className="font-medium">Vara</label>
                    <p className="text-gray-600">{validationResult.componentes?.vara}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep("input")}
                  >
                    Voltar
                  </Button>
                  <Button 
                    onClick={consultarProcesso}
                    disabled={loading}
                  >
                    {loading ? (
                      <Clock className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                    Consultar Processo
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 3: Preview dos dados */}
        {step === "preview" && cnjData && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Dados do Processo
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Informações básicas */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Assunto</label>
                    <p className="text-sm text-gray-600">
                      {extractValue(cnjData.assunto)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Classe Processual</label>
                    <p className="text-sm text-gray-600">
                      {extractValue(cnjData.classe_processual)}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium">Tribunal</label>
                    <p className="text-sm text-gray-600">
                      {extractValue(cnjData.tribunal)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Órgão Julgador</label>
                    <p className="text-sm text-gray-600">
                      {extractValue(cnjData.orgao_julgador)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Vara</label>
                    <p className="text-sm text-gray-600">
                      {extractValue(cnjData.vara)}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Data de Distribuição</label>
                    <p className="text-sm text-gray-600">
                      {formatDate(cnjData.data_distribuicao)}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Valor da Causa</label>
                    <p className="text-sm text-gray-600">
                      {formatCurrency(cnjData.valor_causa)}
                    </p>
                  </div>
                </div>

                {/* Partes */}
                {cnjData.partes && cnjData.partes.length > 0 && (
                  <div>
                    <label className="text-sm font-medium">Partes</label>
                    <div className="space-y-2 mt-2">
                      {cnjData.partes.slice(0, 5).map((parte, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                          <Users className="w-4 h-4 text-gray-500" />
                          <div>
                            <p className="text-sm font-medium">
                              {extractValue(parte.nome)}
                            </p>
                            <p className="text-xs text-gray-500">
                              {extractValue(parte.tipo)}
                            </p>
                          </div>
                        </div>
                      ))}
                      {cnjData.partes.length > 5 && (
                        <p className="text-xs text-gray-500">
                          +{cnjData.partes.length - 5} outras partes
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Andamentos */}
                {cnjData.andamentos && cnjData.andamentos.length > 0 && (
                  <div>
                    <label className="text-sm font-medium">Últimos Andamentos</label>
                    <div className="space-y-2 mt-2">
                      {cnjData.andamentos.slice(0, 3).map((andamento, index) => (
                        <div key={index} className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                          <Calendar className="w-4 h-4 text-gray-500 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium">
                              {extractValue(andamento.tipo)}
                            </p>
                            <p className="text-xs text-gray-600">
                              {extractValue(andamento.descricao)}
                            </p>
                            <p className="text-xs text-gray-500">
                              {formatDate(andamento.data)}
                            </p>
                          </div>
                        </div>
                      ))}
                      {cnjData.andamentos.length > 3 && (
                        <p className="text-xs text-gray-500">
                          +{cnjData.andamentos.length - 3} outros andamentos
                        </p>
                      )}
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep("validation")}
                  >
                    Voltar
                  </Button>
                  <Button 
                    onClick={importarProcesso}
                    disabled={loading}
                    className="flex-1"
                  >
                    {loading ? (
                      <Clock className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                    Importar Processo
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 4: Importando */}
        {step === "importing" && (
          <div className="space-y-4 text-center py-8">
            <Clock className="w-12 h-12 animate-spin mx-auto text-blue-600" />
            <h3 className="text-lg font-semibold">Importando Processo</h3>
            <p className="text-gray-600">
              Aguarde enquanto importamos os dados do processo da API CNJ...
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
