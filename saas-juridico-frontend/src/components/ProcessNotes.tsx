"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  MessageSquare, 
  Plus, 
  Edit, 
  Trash2, 
  User,
  AtSign
} from "lucide-react";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";

interface ProcessNote {
  id: string;
  content: string;
  created_by: {
    id: string;
    name: string;
  };
  created_at: string;
  updated_at?: string;
  mentions?: string[]; // IDs de usuários mencionados
}

interface ProcessNotesProps {
  processId: string;
}

export function ProcessNotes({ processId }: ProcessNotesProps) {
  const [notes, setNotes] = useState<ProcessNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState("");

  useEffect(() => {
    loadNotes();
  }, [processId]);

  const loadNotes = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.log("Token não encontrado, não carregando anotações");
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/v1/company/processes/${processId}/notes`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const notesData = await response.json();
        setNotes(notesData);
      } else {
        throw new Error('Erro ao carregar anotações');
      }
    } catch (error) {
      console.error("Erro ao carregar anotações:", error);
      toast.error("Erro ao carregar anotações");
    } finally {
      setLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNoteContent.trim()) {
      toast.error("A anotação não pode estar vazia");
      return;
    }

    try {
      // TODO: Implementar adição via API
      const newNote: ProcessNote = {
        id: Date.now().toString(),
        content: newNoteContent,
        created_by: { id: '1', name: 'João Silva' }, // Mock - usar usuário atual
        created_at: new Date().toISOString()
      };

      setNotes([newNote, ...notes]);
      setNewNoteContent("");
      setIsAddingNote(false);
      toast.success("Anotação adicionada com sucesso!");
    } catch (error) {
      console.error("Erro ao adicionar anotação:", error);
      toast.error("Erro ao adicionar anotação");
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    if (!confirm("Tem certeza que deseja excluir esta anotação?")) {
      return;
    }

    try {
      // TODO: Implementar exclusão via API
      setNotes(notes.filter(note => note.id !== noteId));
      toast.success("Anotação excluída com sucesso!");
    } catch (error) {
      console.error("Erro ao excluir anotação:", error);
      toast.error("Erro ao excluir anotação");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <Loading message="Carregando anotações..." />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Anotações do Processo</h2>
          <p className="text-sm text-gray-600">
            Registre observações e informações importantes
          </p>
        </div>
        
        <Button onClick={() => setIsAddingNote(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nova Anotação
        </Button>
      </div>

      {/* Adicionar Nova Anotação */}
      {isAddingNote && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nova Anotação
                </label>
                <textarea
                  value={newNoteContent}
                  onChange={(e) => setNewNoteContent(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  rows={4}
                  placeholder="Digite sua anotação aqui..."
                  autoFocus
                />
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsAddingNote(false);
                    setNewNoteContent("");
                  }}
                >
                  Cancelar
                </Button>
                <Button onClick={handleAddNote}>
                  Adicionar Anotação
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lista de Anotações */}
      <div className="space-y-4">
        {notes.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhuma anotação registrada
              </h3>
              <p className="text-gray-600 mb-4">
                Comece adicionando a primeira anotação do processo.
              </p>
              <Button onClick={() => setIsAddingNote(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Primeira Anotação
              </Button>
            </CardContent>
          </Card>
        ) : (
          notes.map((note) => (
            <NoteItem
              key={note.id}
              note={note}
              onDelete={handleDeleteNote}
            />
          ))
        )}
      </div>
    </div>
  );
}

interface NoteItemProps {
  note: ProcessNote;
  onDelete: (noteId: string) => void;
}

function NoteItem({ note, onDelete }: NoteItemProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <User className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-900">
                {note.created_by.name}
              </span>
              <span className="text-xs text-gray-500">
                {formatDate(note.created_at)}
              </span>
              {note.updated_at && note.updated_at !== note.created_at && (
                <Badge variant="outline" className="text-xs">
                  Editado
                </Badge>
              )}
            </div>
            
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">
                {note.content}
              </p>
            </div>
            
            {note.mentions && note.mentions.length > 0 && (
              <div className="flex items-center space-x-1 mt-2">
                <AtSign className="h-3 w-3 text-gray-400" />
                <span className="text-xs text-gray-500">
                  Mencionados: {note.mentions.length} usuário(s)
                </span>
              </div>
            )}
          </div>
          
          <div className="flex space-x-1 ml-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(note.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
