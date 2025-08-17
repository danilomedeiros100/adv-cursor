'use client';

import { useRouter } from 'next/navigation';
import { 
  Building2, 
  Users, 
  BarChart3, 
  Settings, 
  Shield, 
  Activity,
  Database,
  FileText
} from 'lucide-react';

interface NavigationItem {
  name: string;
  href: string;
  icon: any;
  current: boolean;
}

interface SuperAdminNavigationProps {
  onItemClick?: () => void;
}

export default function SuperAdminNavigation({ onItemClick }: SuperAdminNavigationProps) {
  const router = useRouter();

  const navigation: NavigationItem[] = [
    {
      name: 'Dashboard',
      href: '/superadmin/dashboard',
      icon: BarChart3,
      current: true
    },
    {
      name: 'Empresas',
      href: '/superadmin/tenants',
      icon: Building2,
      current: false
    },
    {
      name: 'Usuários',
      href: '/superadmin/users',
      icon: Users,
      current: false
    },
    {
      name: 'Analytics',
      href: '/superadmin/analytics',
      icon: Activity,
      current: false
    },
    {
      name: 'Sistema',
      href: '/superadmin/system',
      icon: Database,
      current: false
    },
    {
      name: 'Relatórios',
      href: '/superadmin/reports',
      icon: FileText,
      current: false
    },
    {
      name: 'Segurança',
      href: '/superadmin/security',
      icon: Shield,
      current: false
    },
    {
      name: 'Configurações',
      href: '/superadmin/settings',
      icon: Settings,
      current: false
    }
  ];

  const handleNavigation = (href: string) => {
    router.push(href);
    if (onItemClick) {
      onItemClick();
    }
  };

  return (
    <nav className="flex-1 space-y-1 px-2 py-4">
      {navigation.map((item) => (
        <button
          key={item.name}
          onClick={() => handleNavigation(item.href)}
          className={`group flex items-center w-full px-2 py-2 text-sm font-medium rounded-md ${
            item.current
              ? 'bg-purple-100 text-purple-900'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          }`}
        >
          <item.icon className="mr-3 h-5 w-5" />
          {item.name}
        </button>
      ))}
    </nav>
  );
}
