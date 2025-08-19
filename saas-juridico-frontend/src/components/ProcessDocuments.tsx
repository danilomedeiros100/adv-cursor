"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  Upload, 
  Download, 
  Eye, 
  Trash2, 
  Plus,
  Search,
  Filter
} from "lucide-react";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";

interface ProcessDocument {
  id: string;
  title: string;
  description?: string;
  file_url: string;
  file_size: number;
  mime_type: string;
  tags: string[];
  created_by: {
    id: string;
    name: string;
  };
  created_at: string;
  updated_at?: string;
  version: number;
  is_signed?: boolean;
}

interface ProcessDocumentsProps {
  processId: string;
}

export function ProcessDocuments({ processId }: ProcessDocumentsProps) {
  const [documents, setDocuments] = useState<ProcessDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadDocuments();
  }, [processId]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.log("Token não encontrado, não carregando documentos");
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/v1/company/processes/${processId}/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const documentsData = await response.json();
        setDocuments(documentsData);
      } else {
        throw new Error('Erro ao carregar documentos');
      }
    } catch (error) {
      console.error("Erro ao carregar documentos:", error);
      toast.error("Erro ao carregar documentos");
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <Loading message="Carregando documentos..." />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Documentos do Processo</h2>
          <p className="text-sm text-gray-600">
            Gerencie documentos e arquivos relacionados
          </p>
        </div>
        
        <Button>
          <Upload className="h-4 w-4 mr-2" />
          Upload Documento
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Buscar documentos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md"
          />
        </div>
        
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filtros
        </Button>
      </div>

      {/* Documents Grid */}
      <Card>
        <CardContent className="p-6">
          {filteredDocuments.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum documento encontrado
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm ? 'Nenhum documento corresponde à busca.' : 'Comece fazendo upload do primeiro documento.'}
              </p>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload Primeiro Documento
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredDocuments.map((document) => (
                <DocumentCard key={document.id} document={document} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface DocumentCardProps {
  document: ProcessDocument;
}

function DocumentCard({ document }: DocumentCardProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-medium text-gray-900 mb-1">{document.title}</h3>
          {document.description && (
            <p className="text-sm text-gray-600 mb-2">{document.description}</p>
          )}
        </div>
        
        <div className="flex space-x-1">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{formatFileSize(document.file_size)}</span>
          <span>v{document.version}</span>
        </div>
        
        {document.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {document.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
        
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Por: {document.created_by.name}</span>
          <span>{formatDate(document.created_at)}</span>
        </div>
        
        {document.is_signed && (
          <Badge variant="default" className="text-xs">
            Assinado
          </Badge>
        )}
      </div>
    </div>
  );
}
