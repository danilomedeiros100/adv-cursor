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
import { useAuth, usePermissions } from '@/hooks/useAuth';
import { Users, Plus, Search, Filter, UserPlus, Edit, Trash2, Eye } from 'lucide-react';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  position: string;
  is_active: boolean;
  oab_number?: string;
  oab_state?: string;
  phone?: string;
  created_at: string;
}

interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  role_counts: {
    admin: number;
    lawyer: number;
    assistant: number;
    secretary: number;
    receptionist: number;
    user: number;
  };
  lawyers_with_oab: number;
}

export default function UsersPage() {
  const { user, tenant } = useAuth();
  const { hasPermission } = usePermissions();
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [departments, setDepartments] = useState<string[]>([]);

  // Estados para criação de usuário
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    password: '',
    role: 'user',
    department: '',
    position: '',
    phone: '',
    oab_number: '',
    oab_state: '',
  });

  useEffect(() => {
    fetchUsers();
    fetchStats();
    fetchDepartments();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/company/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        // Verificar se data.users existe, senão usar data diretamente
        setUsers(data.users || data || []);
      } else {
        console.error('Erro ao carregar usuários');
        setUsers([]);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/company/users/stats/summary', {
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

  const fetchDepartments = async () => {
    try {
      const response = await fetch('/api/v1/company/users/departments/list', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setDepartments(data.departments || []);
      }
    } catch (error) {
      console.error('Erro ao carregar departamentos:', error);
    }
  };

  const createUser = async () => {
    // Validação básica
    if (!newUser.name || !newUser.email || !newUser.password) {
      alert('Por favor, preencha nome, email e senha');
      return;
    }

    if (newUser.role === 'lawyer' && (!newUser.oab_number || !newUser.oab_state)) {
      alert('Para advogados, é necessário informar número e estado da OAB');
      return;
    }

    try {
      const response = await fetch('/api/v1/company/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(newUser),
      });

      if (response.ok) {
        const createdUser = await response.json();
        
        // Adicionar o novo usuário à lista local
        setUsers(prevUsers => [...(prevUsers || []), createdUser]);
        
        setShowCreateDialog(false);
        setNewUser({
          name: '',
          email: '',
          password: '',
          role: 'user',
          department: '',
          position: '',
          phone: '',
          oab_number: '',
          oab_state: '',
        });
        
        // Atualizar estatísticas
        fetchStats();
        alert('Usuário criado com sucesso!');
      } else {
        const error = await response.json();
        alert(`Erro ao criar usuário: ${error.error || error.detail || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
      alert('Erro ao criar usuário');
    }
  };

  const viewUser = async (user: User) => {
    try {
      const response = await fetch(`/api/v1/company/users?id=${user.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        setSelectedUser(userData);
        setShowViewDialog(true);
      } else {
        console.error('Erro ao carregar detalhes do usuário');
        alert('Erro ao carregar detalhes do usuário');
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
      alert('Erro ao carregar detalhes do usuário');
    }
  };

  const editUser = (user: User) => {
    setEditingUser({ ...user });
    setShowEditDialog(true);
  };

  const updateUser = async () => {
    if (!editingUser) return;

    // Validação básica
    if (!editingUser.name || !editingUser.email) {
      alert('Por favor, preencha nome e email');
      return;
    }

    if (editingUser.role === 'lawyer' && (!editingUser.oab_number || !editingUser.oab_state)) {
      alert('Para advogados, é necessário informar número e estado da OAB');
      return;
    }

    try {
      const response = await fetch('/api/v1/company/users', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(editingUser),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        
        // Atualizar o usuário na lista local
        setUsers(prevUsers => 
          (prevUsers || []).map(user => 
            user.id === updatedUser.id ? updatedUser : user
          )
        );
        
        setShowEditDialog(false);
        setEditingUser(null);
        
        // Atualizar estatísticas
        fetchStats();
        alert('Usuário atualizado com sucesso!');
      } else {
        const error = await response.json();
        alert(`Erro ao atualizar usuário: ${error.error || error.detail || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
      alert('Erro ao atualizar usuário');
    }
  };

  const deleteUser = async () => {
    if (!selectedUser) return;

    if (!confirm(`Tem certeza que deseja excluir o usuário "${selectedUser.name}"?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/company/users?id=${selectedUser.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        // Remover o usuário da lista local
        setUsers(prevUsers => 
          (prevUsers || []).filter(user => user.id !== selectedUser.id)
        );
        
        setShowDeleteDialog(false);
        setSelectedUser(null);
        
        // Atualizar estatísticas
        fetchStats();
        alert('Usuário excluído com sucesso!');
      } else {
        const error = await response.json();
        alert(`Erro ao excluir usuário: ${error.error || error.detail || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
      alert('Erro ao excluir usuário');
    }
  };

  const filteredUsers = (users || []).filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (user.oab_number && user.oab_number.includes(searchTerm));
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesDepartment = departmentFilter === 'all' || user.department === departmentFilter;
    
    return matchesSearch && matchesRole && matchesDepartment;
  });

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'lawyer': return 'bg-blue-100 text-blue-800';
      case 'assistant': return 'bg-green-100 text-green-800';
      case 'secretary': return 'bg-purple-100 text-purple-800';
      case 'receptionist': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleDisplayName = (role: string) => {
    switch (role) {
      case 'admin': return 'Administrador';
      case 'lawyer': return 'Advogado';
      case 'assistant': return 'Assistente';
      case 'secretary': return 'Secretário';
      case 'receptionist': return 'Recepcionista';
      case 'user': return 'Usuário';
      default: return role;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Carregando usuários...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Usuários</h1>
          <p className="text-muted-foreground">
            Gerencie os usuários da sua empresa
          </p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="h-4 w-4 mr-2" />
              Novo Usuário
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Criar Novo Usuário</DialogTitle>
              <DialogDescription>
                Preencha os dados do novo usuário
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nome</Label>
                  <Input
                    id="name"
                    value={newUser.name}
                    onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                    placeholder="Nome completo"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                    placeholder="email@empresa.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Senha</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newUser.password}
                    onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                    placeholder="Senha"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Função</Label>
                  <Select value={newUser.role} onValueChange={(value) => setNewUser({...newUser, role: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Administrador</SelectItem>
                      <SelectItem value="lawyer">Advogado</SelectItem>
                      <SelectItem value="assistant">Assistente</SelectItem>
                      <SelectItem value="secretary">Secretário</SelectItem>
                      <SelectItem value="receptionist">Recepcionista</SelectItem>
                      <SelectItem value="user">Usuário</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="department">Departamento</Label>
                  <Select value={newUser.department} onValueChange={(value) => setNewUser({...newUser, department: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um departamento" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.length > 0 ? (
                        departments.map((dept, index) => (
                          <SelectItem key={`dept-create-${index}`} value={dept}>{dept}</SelectItem>
                        ))
                      ) : (
                        <SelectItem value="" disabled>Carregando departamentos...</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="position">Cargo</Label>
                  <Input
                    id="position"
                    value={newUser.position}
                    onChange={(e) => setNewUser({...newUser, position: e.target.value})}
                    placeholder="Cargo"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Telefone</Label>
                <Input
                  id="phone"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({...newUser, phone: e.target.value})}
                  placeholder="(11) 99999-9999"
                />
              </div>
              {newUser.role === 'lawyer' && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="oab_number">Número OAB</Label>
                    <Input
                      id="oab_number"
                      value={newUser.oab_number}
                      onChange={(e) => setNewUser({...newUser, oab_number: e.target.value})}
                      placeholder="123456"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="oab_state">Estado OAB</Label>
                    <Input
                      id="oab_state"
                      value={newUser.oab_state}
                      onChange={(e) => setNewUser({...newUser, oab_state: e.target.value})}
                      placeholder="SP"
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={createUser}>
                Criar Usuário
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_users}</div>
              <p className="text-xs text-muted-foreground">
                {stats.active_users} ativos, {stats.inactive_users} inativos
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Advogados</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.role_counts.lawyer}</div>
              <p className="text-xs text-muted-foreground">
                {stats.lawyers_with_oab} com OAB
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Assistentes</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.role_counts.assistant}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Administradores</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.role_counts.admin}</div>
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
                  placeholder="Nome, email ou OAB..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="role-filter">Função</Label>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as funções" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas as funções</SelectItem>
                  <SelectItem value="admin">Administrador</SelectItem>
                  <SelectItem value="lawyer">Advogado</SelectItem>
                  <SelectItem value="assistant">Assistente</SelectItem>
                  <SelectItem value="secretary">Secretário</SelectItem>
                  <SelectItem value="receptionist">Recepcionista</SelectItem>
                  <SelectItem value="user">Usuário</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="department-filter">Departamento</Label>
              <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os departamentos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os departamentos</SelectItem>
                  {departments.map((dept, index) => (
                    <SelectItem key={`dept-filter-${index}`} value={dept}>{dept}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Usuários</CardTitle>
          <CardDescription>
            {filteredUsers.length} usuário(s) encontrado(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredUsers.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <Users className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-medium">{user.name}</h3>
                      <Badge className={getRoleBadgeColor(user.role)}>
                        {getRoleDisplayName(user.role)}
                      </Badge>
                      {!user.is_active && (
                        <Badge variant="secondary">Inativo</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      {user.department && <span>{user.department}</span>}
                      {user.position && <span>{user.position}</span>}
                      {user.oab_number && (
                        <span>OAB: {user.oab_number}/{user.oab_state}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => viewUser(user)}
                    title="Visualizar detalhes"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => editUser(user)}
                    title="Editar usuário"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  {/* Botão de delete - só aparece se tiver permissão */}
                  {(hasPermission('users.delete') || hasPermission('users.manage')) && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-red-600"
                      onClick={() => {
                        setSelectedUser(user);
                        setShowDeleteDialog(true);
                      }}
                      title="Excluir usuário"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
            {filteredUsers.length === 0 && (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium">Nenhum usuário encontrado</h3>
                <p className="text-muted-foreground">
                  Tente ajustar os filtros ou criar um novo usuário
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
            <DialogTitle>Detalhes do Usuário</DialogTitle>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Nome</Label>
                  <p className="text-sm text-muted-foreground">{selectedUser.name}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Email</Label>
                  <p className="text-sm text-muted-foreground">{selectedUser.email}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Função</Label>
                  <Badge className={getRoleBadgeColor(selectedUser.role)}>
                    {getRoleDisplayName(selectedUser.role)}
                  </Badge>
                </div>
                <div>
                  <Label className="text-sm font-medium">Status</Label>
                  <Badge variant={selectedUser.is_active ? "default" : "secondary"}>
                    {selectedUser.is_active ? "Ativo" : "Inativo"}
                  </Badge>
                </div>
              </div>
              {selectedUser.department && (
                <div>
                  <Label className="text-sm font-medium">Departamento</Label>
                  <p className="text-sm text-muted-foreground">{selectedUser.department}</p>
                </div>
              )}
              {selectedUser.position && (
                <div>
                  <Label className="text-sm font-medium">Cargo</Label>
                  <p className="text-sm text-muted-foreground">{selectedUser.position}</p>
                </div>
              )}
              {selectedUser.phone && (
                <div>
                  <Label className="text-sm font-medium">Telefone</Label>
                  <p className="text-sm text-muted-foreground">{selectedUser.phone}</p>
                </div>
              )}
              {selectedUser.oab_number && (
                <div>
                  <Label className="text-sm font-medium">OAB</Label>
                  <p className="text-sm text-muted-foreground">{selectedUser.oab_number}/{selectedUser.oab_state}</p>
                </div>
              )}
              <div>
                <Label className="text-sm font-medium">Data de Criação</Label>
                <p className="text-sm text-muted-foreground">
                  {new Date(selectedUser.created_at).toLocaleDateString('pt-BR')}
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
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Editar Usuário</DialogTitle>
          </DialogHeader>
          {editingUser && (
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-name">Nome</Label>
                  <Input
                    id="edit-name"
                    value={editingUser.name}
                    onChange={(e) => setEditingUser({...editingUser, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-email">Email</Label>
                  <Input
                    id="edit-email"
                    type="email"
                    value={editingUser.email}
                    onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-role">Função</Label>
                  <Select value={editingUser.role} onValueChange={(value) => setEditingUser({...editingUser, role: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Administrador</SelectItem>
                      <SelectItem value="lawyer">Advogado</SelectItem>
                      <SelectItem value="assistant">Assistente</SelectItem>
                      <SelectItem value="secretary">Secretário</SelectItem>
                      <SelectItem value="receptionist">Recepcionista</SelectItem>
                      <SelectItem value="user">Usuário</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-department">Departamento</Label>
                  <Select value={editingUser.department} onValueChange={(value) => setEditingUser({...editingUser, department: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um departamento" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((dept, index) => (
                        <SelectItem key={`dept-edit-${index}`} value={dept}>{dept}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-position">Cargo</Label>
                <Input
                  id="edit-position"
                  value={editingUser.position}
                  onChange={(e) => setEditingUser({...editingUser, position: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-phone">Telefone</Label>
                <Input
                  id="edit-phone"
                  value={editingUser.phone || ''}
                  onChange={(e) => setEditingUser({...editingUser, phone: e.target.value})}
                />
              </div>
              {editingUser.role === 'lawyer' && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="edit-oab-number">Número OAB</Label>
                    <Input
                      id="edit-oab-number"
                      value={editingUser.oab_number || ''}
                      onChange={(e) => setEditingUser({...editingUser, oab_number: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-oab-state">Estado OAB</Label>
                    <Input
                      id="edit-oab-state"
                      value={editingUser.oab_state || ''}
                      onChange={(e) => setEditingUser({...editingUser, oab_state: e.target.value})}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={updateUser}>
              Salvar Alterações
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog de Confirmação de Exclusão */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Confirmar Exclusão</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja excluir o usuário "{selectedUser?.name}"? Esta ação não pode ser desfeita.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={deleteUser}>
              Excluir
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
