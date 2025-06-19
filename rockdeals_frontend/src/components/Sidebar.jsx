import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Package, 
  Users, 
  CreditCard,
  Receipt,
  Settings,
  MessageSquare,
  HelpCircle,
  Crown
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: FileText, label: 'Report', path: '/reports' },
    { icon: Package, label: 'Product', path: '/products' },
    { icon: Users, label: 'Consumer', path: '/customers' },
    { icon: CreditCard, label: 'POS', path: '/pos' },
  ];

  const financialItems = [
    { icon: CreditCard, label: 'Transactions', path: '/transactions' },
    { icon: Receipt, label: 'Invoices', path: '/invoices' },
  ];

  const toolsItems = [
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: MessageSquare, label: 'Feed back', path: '/feedback' },
    { icon: HelpCircle, label: 'Help', path: '/help' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="w-72 rockdeals-sidebar h-full flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rockdeals-gradient rounded-lg flex items-center justify-center">
            <Crown className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-sidebar-foreground">RockDeals</span>
        </div>
      </div>

      {/* Menu */}
      <div className="flex-1 p-4 space-y-6">
        {/* Main Menu */}
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            MENU
          </h3>
          <nav className="space-y-1">
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                }`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Financial */}
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Financial
          </h3>
          <nav className="space-y-1">
            {financialItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                }`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Tools */}
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Tools
          </h3>
          <nav className="space-y-1">
            {toolsItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                }`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Upgrade Pro */}
      <div className="p-4">
        <div className="bg-muted rounded-xl p-4 text-center">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center mx-auto mb-3">
            <Crown className="w-5 h-5 text-primary-foreground" />
          </div>
          <h4 className="font-semibold text-foreground mb-1">Upgrade pro</h4>
          <p className="text-xs text-muted-foreground mb-3">
            Discover benefits of upgraded account
          </p>
          <Button className="w-full rockdeals-gradient text-white font-medium">
            Upgrade $30
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

