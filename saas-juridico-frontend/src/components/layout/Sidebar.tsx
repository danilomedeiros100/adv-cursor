'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useAuth } from '@/hooks/useAuth';
import {
  LayoutDashboard,
  Users,
  FileText,
  FolderOpen,
  DollarSign,
  Settings,
  Building2,
  User,
  LogOut,
  Menu,
  X,
  Scale,
} from 'lucide-react';

interface SidebarProps {
  className?: string;
}

const navigationItems = {
  superadmin: [
    { name: 'Dashboard', href: '/superadmin/dashboard', icon: LayoutDashboard },
    { name: 'Empresas', href: '/superadmin/tenants', icon: Building2 },
    { name: 'Analytics', href: '/superadmin/analytics', icon: FileText },
    { name: 'Configurações', href: '/superadmin/settings', icon: Settings },
  ],
  company: [
    { name: 'Dashboard', href: '/company/dashboard', icon: LayoutDashboard },
    { name: 'Usuários', href: '/company/users', icon: Users, permission: 'users.manage' },
    { name: 'Clientes', href: '/company/clients', icon: Users, permission: 'clients.read' },
    { name: 'Processos', href: '/company/processes', icon: FolderOpen, permission: 'processes.read' },
    { name: 'Especialidades', href: '/company/specialties', icon: Scale, permission: 'specialties.manage' },
    { name: 'Documentos', href: '/company/documents', icon: FileText, permission: 'documents.manage' },
    { name: 'Financeiro', href: '/company/financial', icon: DollarSign, permission: 'financial.manage' },
    { name: 'Configurações', href: '/company/settings', icon: Settings },
  ],
  client: [
    { name: 'Dashboard', href: '/client/dashboard', icon: LayoutDashboard },
    { name: 'Processos', href: '/client/processes', icon: FolderOpen },
    { name: 'Documentos', href: '/client/documents', icon: FileText },
    { name: 'Perfil', href: '/client/profile', icon: User },
  ],
};

export function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { user, tenant, logout, isSuperAdmin, isClientUser } = useAuth();

  // Log para debug
  useEffect(() => {
    console.log('🔍 Sidebar Debug:', {
      user: user?.name,
      tenant: tenant?.name,
      isSuperAdmin,
      isClientUser,
      // Removido tenantPermissions e tenantRole pois não existem no tipo Tenant
    });
  }, [user, tenant, isSuperAdmin, isClientUser]);

  // Determina o tipo de navegação baseado no usuário
  let navType: 'superadmin' | 'company' | 'client' = 'company';
  if (isSuperAdmin) navType = 'superadmin';
  else if (isClientUser) navType = 'client';

  // Filtra itens baseado nas permissões para usuários de empresa
  let navigation = navigationItems[navType];
  if (navType === 'company') {
    // Por enquanto, mostra todos os itens para usuários de empresa
    // As permissões serão verificadas no backend
    navigation = navigationItems.company;
  }

  console.log('Navigation items:', navigation.map(item => item.name));

  return (
    <div className={cn('flex flex-col h-full bg-background border-r', className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-2">
          <Building2 className="h-6 w-6 text-primary" />
          {!isCollapsed && (
            <span className="font-semibold text-lg">SaaS Jurídico</span>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="h-8 w-8 p-0"
        >
          {isCollapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn(
                  'w-full justify-start',
                  isActive && 'bg-secondary text-secondary-foreground'
                )}
              >
                <item.icon className="h-4 w-4 mr-2" />
                {!isCollapsed && item.name}
              </Button>
            </Link>
          );
        })}
      </nav>

      {/* User Info */}
      {!isCollapsed && (
        <>
          <Separator className="mx-4" />
          <div className="p-4">
            <div className="flex items-center space-x-2 mb-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">{user?.name}</span>
            </div>
            {tenant && (
              <div className="flex items-center space-x-2 mb-4">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">{tenant.name}</span>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                console.log('🔴 Logout clicado');
                logout();
              }}
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sair
            </Button>
          </div>
        </>
      )}

      {/* Logout button when collapsed */}
      {isCollapsed && (
        <>
          <Separator className="mx-4" />
          <div className="p-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                console.log('🔴 Logout clicado (colapsado)');
                logout();
              }}
              className="w-full justify-center text-red-600 hover:text-red-700 hover:bg-red-50"
              title="Sair"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
