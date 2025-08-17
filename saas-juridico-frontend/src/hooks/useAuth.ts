import { useAuthStore } from '@/stores/authStore';

export function useAuth() {
  const {
    user,
    tenant,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    getToken,
    checkAuthStatus,
    clearError,
  } = useAuthStore();

  // Detectar tipo de usuário
  const isSuperAdmin = user?.is_super_admin === true;
  const isCompanyUser = !isSuperAdmin && isAuthenticated && user;
  const isClientUser = false; // TODO: implementar quando necessário

  return {
    user,
    tenant,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    token: getToken(),
    checkAuthStatus,
    clearError,
    isSuperAdmin,
    isCompanyUser,
    isClientUser,
    isInitialized: true, // Para compatibilidade
  };
}

// Hook para verificar permissões
export function usePermissions() {
  const { user, tenant } = useAuth();
  
  const hasPermission = (permission: string) => {
    if (!user || !tenant) return false;
    
    // Super admin tem todas as permissões
    if (user.is_super_admin) return true;
    
    // Verifica permissões do usuário no tenant
    const userPermissions = (tenant as any).permissions || {};
    return userPermissions[permission] === true;
  };

  const hasModuleAccess = (module: string) => {
    if (!user || !tenant) return false;
    
    // Super admin tem acesso a todos os módulos
    if (user.is_super_admin) return true;
    
    // Verifica acesso ao módulo
    const allowedModules = (tenant as any).allowed_modules || [];
    return allowedModules.includes(module) || allowedModules.includes('*');
  };

  return {
    hasPermission,
    hasModuleAccess,
  };
}

// Hook para verificar se pode gerenciar usuários
export function useCanManageUsers() {
  const { hasPermission } = usePermissions();
  return hasPermission('users.manage');
}

// Hook para verificar se pode gerenciar financeiro
export function useCanManageFinancial() {
  const { hasPermission } = usePermissions();
  return hasPermission('financial.manage');
}

// Hook para verificar se pode ver todos os processos
export function useCanViewAllProcesses() {
  const { hasPermission } = usePermissions();
  return hasPermission('processes.view_all');
}
