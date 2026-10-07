import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderGit2,
  AlertTriangle,
  ShieldAlert,
  FileCheck2,
  FileText,
  Settings,
  Cpu
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
    { to: '/projects', label: 'Projects & Scans', icon: FolderGit2 },
    { to: '/vulnerabilities', label: 'Vulnerability Intel', icon: AlertTriangle },
    { to: '/policies', label: 'Policy Engine', icon: ShieldAlert },
    { to: '/reports', label: 'Reports & Export', icon: FileText },
    { to: '/settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between">
      <div className="space-y-6">
        <div>
          <div className="px-3 mb-2 text-[11px] font-mono tracking-wider text-slate-500 uppercase">
            Security Control Center
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-950/70 text-cyan-400 border border-cyan-800/60 shadow-sm shadow-cyan-900/40'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 space-y-2">
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-semibold">
            <Cpu className="w-4 h-4" />
            <span>Random Forest Risk AI</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Multi-factor supply chain attack risk engine trained on package heuristics and CVSS metrics.
          </p>
          <div className="flex items-center justify-between text-[10px] font-mono pt-1 text-slate-500 border-t border-slate-900">
            <span>Accuracy: 98.4%</span>
            <span className="text-emerald-400">OPERATIONAL</span>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800 text-center">
        <span className="text-[11px] font-mono text-slate-500">
          SecureSupply AI v1.0.0
        </span>
      </div>
    </aside>
  );
};
