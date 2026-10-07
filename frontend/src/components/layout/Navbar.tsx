import React from 'react';
import { Shield, Bell, User as UserIcon, LogOut, Terminal } from 'lucide-react';
import { authService } from '../../services/api';

interface NavbarProps {
  user: any;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="bg-gradient-to-tr from-cyan-500 to-blue-600 p-2 rounded-lg shadow-lg shadow-cyan-500/20">
          <Shield className="w-5 h-5 text-slate-950 font-bold" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-wider text-white flex items-center gap-1.5">
            SECURE<span className="text-cyan-400">SUPPLY</span> AI
          </span>
          <span className="text-[10px] font-mono tracking-widest bg-cyan-950/80 text-cyan-400 px-1.5 py-0.5 rounded border border-cyan-800/50">
            ENTERPRISE PLATFORM
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono text-slate-400">
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span>ML Model: RF-1.0.0 (Active)</span>
        </div>

        <button className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyan-500 rounded-full animate-ping"></span>
        </button>

        <div className="h-6 w-[1px] bg-slate-800"></div>

        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400 font-bold text-sm">
            {user?.email?.[0].toUpperCase() || 'A'}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-200">{user?.full_name || 'Security Analyst'}</div>
            <div className="text-[10px] font-mono text-cyan-400 uppercase">{user?.role || 'DEVELOPER'}</div>
          </div>

          <button
            onClick={onLogout}
            title="Log out"
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors ml-2"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};
