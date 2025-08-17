'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useSuperAdminStore } from '@/stores/superAdminStore';
import { SuperAdminProtectedRoute } from '@/components/auth/SuperAdminProtectedRoute';
import SuperAdminNavigation from './SuperAdminNavigation';
import { 
  Shield, 
  LogOut,
  Menu,
  X,
  AlertTriangle
} from 'lucide-react';

interface SuperAdminLayoutProps {
  children: React.ReactNode;
}

export default function SuperAdminLayout({ children }: SuperAdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const router = useRouter();
  const { logout } = useSuperAdminStore();

  const handleLogout = () => {
    logout();
    router.push('/superadmin/login');
  };

  return (
    <SuperAdminProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Mobile sidebar */}
        <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
            <div className="flex h-16 items-center justify-between px-4">
              <div className="flex items-center">
                <Shield className="h-8 w-8 text-purple-600" />
                <span className="ml-2 text-lg font-semibold text-gray-900">Super Admin</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            <SuperAdminNavigation onItemClick={() => setSidebarOpen(false)} />
            <div className="border-t border-gray-200 p-4">
              <Button
                variant="ghost"
                className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut className="mr-3 h-5 w-5" />
                Sair
              </Button>
            </div>
          </div>
        </div>

        {/* Desktop sidebar */}
        <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
          <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
            <div className="flex h-16 items-center px-4">
              <div className="flex items-center">
                <Shield className="h-8 w-8 text-purple-600" />
                <span className="ml-2 text-lg font-semibold text-gray-900">Super Admin</span>
              </div>
            </div>
            <SuperAdminNavigation />
            <div className="border-t border-gray-200 p-4">
              <Button
                variant="ghost"
                className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut className="mr-3 h-5 w-5" />
                Sair
              </Button>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="lg:pl-64">
          {/* Top bar */}
          <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
            <Button
              variant="ghost"
              className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </Button>

            <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
              <div className="flex flex-1"></div>
              <div className="flex items-center gap-x-4 lg:gap-x-6">
                {/* Notifications */}
                <Button variant="ghost" size="sm">
                  <AlertTriangle className="h-5 w-5" />
                </Button>
                
                {/* Profile dropdown */}
                <div className="flex items-center gap-x-2">
                  <div className="h-8 w-8 rounded-full bg-purple-600 flex items-center justify-center">
                    <Shield className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-sm font-medium text-gray-900">Super Admin</span>
                </div>
              </div>
            </div>
          </div>

          {/* Page content */}
          <main className="py-6">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </SuperAdminProtectedRoute>
  );
}
