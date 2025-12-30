/**
 * Navigation component with route links.
 */

import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Layers,
  GitBranch,
  Wrench,
  FileText,
  Settings,
  type LucideIcon,
} from 'lucide-react';
import { ROUTES } from '../../constants';

// Icon mapping for type-safe icon lookup
const iconMap: Record<string, LucideIcon> = {
  LayoutDashboard,
  Layers,
  GitBranch,
  Wrench,
  FileText,
  Settings,
};

// Navigation items with centralized route constants
const navItems = [
  { path: ROUTES.DASHBOARD, label: 'Dashboard', iconName: 'LayoutDashboard' },
  { path: ROUTES.BATCHES, label: 'Batches', iconName: 'Layers' },
  { path: ROUTES.SEQUENCES, label: 'Sequences', iconName: 'GitBranch' },
  { path: ROUTES.MANUAL, label: 'Manual', iconName: 'Wrench' },
  { path: ROUTES.LOGS, label: 'Logs', iconName: 'FileText' },
  { path: ROUTES.SETTINGS, label: 'Settings', iconName: 'Settings' },
] as const;

export function Navigation() {
  return (
    <nav className="flex gap-1 px-4 py-2 bg-zinc-800 border-b border-zinc-700">
      {navItems.map(({ path, label, iconName }) => {
        const Icon = iconMap[iconName];
        return (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-500/20 text-brand-400'
                  : 'text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200'
              }`
            }
          >
            {Icon && <Icon className="w-4 h-4" />}
            {label}
          </NavLink>
        );
      })}
    </nav>
  );
}
