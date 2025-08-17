'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { useSpecialties, type Specialty, type CreateSpecialtyData } from '@/hooks/useSpecialties';
import { usePermissions } from '@/hooks/useAuth';
import { 
  Scale, Plus, Search, Filter, Edit, Trash2, Eye, 
  Palette, Hash, Calendar, Award, BookOpen
} from 'lucide-react';

interface SpecialtyStats {
  total_specialties: number;
  active_specialties: number;
  inactive_specialties: number;
  specialties_with_oab_requirement: number;
  specialties_with_experience_requirement: number;
}

export default function SpecialtiesPage() {
  const { specialties, loading, createSpecialty, updateSpecialty, deleteSpecialty, activateSpecialty, filterSpecialties, fetchSpecialties } = useSpecialties();
  // const { hasPermission } = usePermissions(); // Temporariamente removido para permitir acesso total
  const [stats, setStats] = useState<SpecialtyStats | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [oabFilter, setOabFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedSpecialty, setSelectedSpecialty] = useState<Specialty | null>(null);
  const [editingSpecialty, setEditingSpecialty] = useState<Specialty | null>(null);

  // Estados para criação de especialidade
  const [newSpecialty, setNewSpecialty] = useState<CreateSpecialtyData>({
    name: '',
    description: '',
    code: '',
    color: '#3B82F6',
    icon: '',
    display_order: '0',
    requires_oab: false,
    min_experience_years: '',
  });

  // Carregar estatísticas
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/company/specialties/stats/summary', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleCreateSpecialty = async () => {
    console.log('Iniciando handleCreateSpecialty');
    console.log('Dados da nova especialidade:', newSpecialty);
    
    // Validação básica
    if (!newSpecialty.name.trim()) {
      alert('Por favor, preencha o nome da especialidade');
      return;
    }

    console.log('Chamando createSpecialty...');
    const result = await createSpecialty(newSpecialty);
    console.log('Resultado da criação:', result);
    
    if (result) {
      setShowCreateDialog(false);
      setNewSpecialty({
        name: '',
        description: '',
        code: '',
        color: '#3B82F6',
        icon: '',
        display_order: '0',
        requires_oab: false,
        min_experience_years: '',
      });
      
      // Atualizar lista
      await fetchSpecialties();
    }
  };



  const handleUpdateSpecialty = async () => {
    if (!editingSpecialty) return;

    // Validação básica
    if (!editingSpecialty.name.trim()) {
      alert('Por favor, preencha o nome da especialidade');
      return;
    }

    const result = await updateSpecialty(editingSpecialty.id, editingSpecialty);
    if (result) {
      setShowEditDialog(false);
      setEditingSpecialty(null);
      
      // Atualizar estatísticas
      fetchStats();
    }
  };

  const handleDeleteSpecialty = async () => {
    if (!selectedSpecialty) return;

    if (!confirm(`Tem certeza que deseja desativar a especialidade "${selectedSpecialty.name}"?\n\nA especialidade será marcada como inativa mas permanecerá no sistema.`)) {
      return;
    }

    const result = await deleteSpecialty(selectedSpecialty.id);
    if (result) {
      setShowDeleteDialog(false);
      setSelectedSpecialty(null);
      
      // Atualizar estatísticas
      fetchStats();
      alert('Especialidade desativada com sucesso!');
    }
  };

  const handleActivateSpecialty = async (specialty: Specialty) => {
    if (!confirm(`Tem certeza que deseja reativar a especialidade "${specialty.name}"?`)) {
      return;
    }

    const result = await activateSpecialty(specialty.id);
    if (result) {
      // Atualizar estatísticas
      fetchStats();
      alert('Especialidade reativada com sucesso!');
    }
  };

  const viewSpecialty = (specialty: Specialty) => {
    setSelectedSpecialty(specialty);
    setShowViewDialog(true);
  };

  const editSpecialty = (specialty: Specialty) => {
    setEditingSpecialty({ ...specialty });
    setShowEditDialog(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Carregando especialidades...</p>
        </div>
      </div>
    );
  }

  const filteredSpecialties = filterSpecialties(searchTerm).filter(specialty => {
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && specialty.is_active) ||
                         (statusFilter === 'inactive' && !specialty.is_active);
    
    const matchesOab = oabFilter === 'all' || 
                      (oabFilter === 'requires' && specialty.requires_oab) ||
                      (oabFilter === 'not_requires' && !specialty.requires_oab);
    
    return matchesStatus && matchesOab;
  });

  const getStatusBadgeColor = (isActive: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  const getOabBadgeColor = (requiresOab: boolean) => {
    return requiresOab ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Carregando especialidades...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Especialidades</h1>
          <p className="text-muted-foreground">
            Gerencie as especialidades do direito da sua empresa
          </p>
        </div>
        {/* Botão criar - acesso total temporariamente */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button onClick={() => console.log('Botão Nova Especialidade clicado')}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Especialidade
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Criar Nova Especialidade</DialogTitle>
              <DialogDescription>
                Preencha os dados da nova especialidade
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome da Especialidade *</Label>
                <Input
                  id="name"
                  value={newSpecialty.name}
                  onChange={(e) => setNewSpecialty({...newSpecialty, name: e.target.value})}
                  placeholder="Ex: Direito Civil"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Descrição</Label>
                <Textarea
                  id="description"
                  value={newSpecialty.description}
                  onChange={(e) => setNewSpecialty({...newSpecialty, description: e.target.value})}
                  placeholder="Descrição da especialidade..."
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="code">Código</Label>
                  <Input
                    id="code"
                    value={newSpecialty.code}
                    onChange={(e) => setNewSpecialty({...newSpecialty, code: e.target.value})}
                    placeholder="Ex: CIV"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="display_order">Ordem de Exibição</Label>
                  <Input
                    id="display_order"
                    type="number"
                    value={newSpecialty.display_order}
                    onChange={(e) => setNewSpecialty({...newSpecialty, display_order: e.target.value})}
                    placeholder="0"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="color">Cor</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      id="color"
                      type="color"
                      value={newSpecialty.color}
                      onChange={(e) => setNewSpecialty({...newSpecialty, color: e.target.value})}
                      className="w-16 h-10"
                    />
                    <Input
                      value={newSpecialty.color}
                      onChange={(e) => setNewSpecialty({...newSpecialty, color: e.target.value})}
                      placeholder="#3B82F6"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="icon">Ícone</Label>
                  <Input
                    id="icon"
                    value={newSpecialty.icon}
                    onChange={(e) => setNewSpecialty({...newSpecialty, icon: e.target.value})}
                    placeholder="Ex: scale"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="min_experience">Anos Mínimos de Experiência</Label>
                <Input
                  id="min_experience"
                  value={newSpecialty.min_experience_years}
                  onChange={(e) => setNewSpecialty({...newSpecialty, min_experience_years: e.target.value})}
                  placeholder="Ex: 3"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="requires_oab"
                  checked={newSpecialty.requires_oab}
                  onCheckedChange={(checked) => setNewSpecialty({...newSpecialty, requires_oab: checked})}
                />
                <Label htmlFor="requires_oab">Requer OAB</Label>
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={() => {
                console.log('Botão Criar Especialidade clicado');
                handleCreateSpecialty();
              }}>
                Criar Especialidade
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total</CardTitle>
              <Scale className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_specialties}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Ativas</CardTitle>
              <Award className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_specialties}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Inativas</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.inactive_specialties}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Requerem OAB</CardTitle>
              <Hash className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.specialties_with_oab_requirement}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Com Experiência</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.specialties_with_experience_requirement}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Buscar</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Nome, descrição ou código..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status-filter">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os status</SelectItem>
                  <SelectItem value="active">Ativas</SelectItem>
                  <SelectItem value="inactive">Inativas</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="oab-filter">Requer OAB</Label>
              <Select value={oabFilter} onValueChange={setOabFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="requires">Requerem OAB</SelectItem>
                  <SelectItem value="not_requires">Não requerem OAB</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Specialties List */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Especialidades</CardTitle>
          <CardDescription>
            {filteredSpecialties.length} especialidade(s) encontrada(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredSpecialties.map((specialty) => (
              <div key={specialty.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: specialty.color || '#3B82F6' }}
                  >
                    <Scale className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium">{specialty.name}</h3>
                      <Badge className={getStatusBadgeColor(specialty.is_active)}>
                        {specialty.is_active ? "Ativa" : "Inativa"}
                      </Badge>
                      <Badge className={getOabBadgeColor(specialty.requires_oab)}>
                        {specialty.requires_oab ? "Requer OAB" : "Não requer OAB"}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {specialty.description || "Sem descrição"}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      {specialty.code && <span>Código: {specialty.code}</span>}
                      {specialty.min_experience_years && (
                        <span>Exp: {specialty.min_experience_years} anos</span>
                      )}
                      <span>Ordem: {specialty.display_order}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => viewSpecialty(specialty)}
                    title="Visualizar detalhes"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  {/* Botão de editar - acesso total temporariamente */}
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => editSpecialty(specialty)}
                    title="Editar especialidade"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  {/* Botão de reativar - só aparece para especialidades inativas */}
                  {!specialty.is_active && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-green-600"
                      onClick={() => handleActivateSpecialty(specialty)}
                      title="Reativar especialidade"
                    >
                      <Award className="h-4 w-4" />
                    </Button>
                  )}
                  {/* Botão de delete - acesso total temporariamente */}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-red-600"
                    onClick={() => {
                      setSelectedSpecialty(specialty);
                      setShowDeleteDialog(true);
                    }}
                    title="Desativar especialidade"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
            {filteredSpecialties.length === 0 && (
              <div className="text-center py-8">
                <Scale className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium">Nenhuma especialidade encontrada</h3>
                <p className="text-muted-foreground">
                  Tente ajustar os filtros ou criar uma nova especialidade
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Dialog de Visualização */}
      <Dialog open={showViewDialog} onOpenChange={setShowViewDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Detalhes da Especialidade</DialogTitle>
          </DialogHeader>
          {selectedSpecialty && (
            <div className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Nome</Label>
                <p className="text-sm text-muted-foreground">{selectedSpecialty.name}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Descrição</Label>
                <p className="text-sm text-muted-foreground">
                  {selectedSpecialty.description || "Sem descrição"}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Código</Label>
                  <p className="text-sm text-muted-foreground">
                    {selectedSpecialty.code || "Não informado"}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Ordem</Label>
                  <p className="text-sm text-muted-foreground">{selectedSpecialty.display_order}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Status</Label>
                  <Badge className={getStatusBadgeColor(selectedSpecialty.is_active)}>
                    {selectedSpecialty.is_active ? "Ativa" : "Inativa"}
                  </Badge>
                </div>
                <div>
                  <Label className="text-sm font-medium">Requer OAB</Label>
                  <Badge className={getOabBadgeColor(selectedSpecialty.requires_oab)}>
                    {selectedSpecialty.requires_oab ? "Sim" : "Não"}
                  </Badge>
                </div>
              </div>
              {selectedSpecialty.min_experience_years && (
                <div>
                  <Label className="text-sm font-medium">Anos Mínimos de Experiência</Label>
                  <p className="text-sm text-muted-foreground">{selectedSpecialty.min_experience_years} anos</p>
                </div>
              )}
              {selectedSpecialty.color && (
                <div>
                  <Label className="text-sm font-medium">Cor</Label>
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-6 h-6 rounded border"
                      style={{ backgroundColor: selectedSpecialty.color }}
                    />
                    <span className="text-sm text-muted-foreground">{selectedSpecialty.color}</span>
                  </div>
                </div>
              )}
              <div>
                <Label className="text-sm font-medium">Data de Criação</Label>
                <p className="text-sm text-muted-foreground">
                  {new Date(selectedSpecialty.created_at).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>
          )}
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setShowViewDialog(false)}>
              Fechar
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog de Edição */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Editar Especialidade</DialogTitle>
          </DialogHeader>
          {editingSpecialty && (
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Nome da Especialidade *</Label>
                <Input
                  id="edit-name"
                  value={editingSpecialty.name}
                  onChange={(e) => setEditingSpecialty({...editingSpecialty, name: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Descrição</Label>
                <Textarea
                  id="edit-description"
                  value={editingSpecialty.description || ''}
                  onChange={(e) => setEditingSpecialty({...editingSpecialty, description: e.target.value})}
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-code">Código</Label>
                  <Input
                    id="edit-code"
                    value={editingSpecialty.code || ''}
                    onChange={(e) => setEditingSpecialty({...editingSpecialty, code: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-display-order">Ordem de Exibição</Label>
                  <Input
                    id="edit-display-order"
                    type="number"
                    value={editingSpecialty.display_order}
                    onChange={(e) => setEditingSpecialty({...editingSpecialty, display_order: e.target.value})}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-color">Cor</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      id="edit-color"
                      type="color"
                      value={editingSpecialty.color || '#3B82F6'}
                      onChange={(e) => setEditingSpecialty({...editingSpecialty, color: e.target.value})}
                      className="w-16 h-10"
                    />
                    <Input
                      value={editingSpecialty.color || '#3B82F6'}
                      onChange={(e) => setEditingSpecialty({...editingSpecialty, color: e.target.value})}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-icon">Ícone</Label>
                  <Input
                    id="edit-icon"
                    value={editingSpecialty.icon || ''}
                    onChange={(e) => setEditingSpecialty({...editingSpecialty, icon: e.target.value})}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-experience">Anos Mínimos de Experiência</Label>
                <Input
                  id="edit-experience"
                  value={editingSpecialty.min_experience_years || ''}
                  onChange={(e) => setEditingSpecialty({...editingSpecialty, min_experience_years: e.target.value})}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="edit-requires-oab"
                  checked={editingSpecialty.requires_oab}
                  onCheckedChange={(checked) => setEditingSpecialty({...editingSpecialty, requires_oab: checked})}
                />
                <Label htmlFor="edit-requires-oab">Requer OAB</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="edit-is-active"
                  checked={editingSpecialty.is_active}
                  onCheckedChange={(checked) => setEditingSpecialty({...editingSpecialty, is_active: checked})}
                />
                <Label htmlFor="edit-is-active">Ativa</Label>
              </div>
            </div>
          )}
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpdateSpecialty}>
              Salvar Alterações
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog de Confirmação de Desativação */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Confirmar Desativação</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja desativar a especialidade "{selectedSpecialty?.name}"? 
              A especialidade será marcada como inativa mas permanecerá no sistema e poderá ser reativada posteriormente.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteSpecialty}>
              Desativar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
