import React from 'react';
import { User as UserIcon, Key, ShieldCheck, Terminal, Server } from 'lucide-react';

interface SettingsPageProps {
  user: any;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ user }) => {
  return (
    <div className="space-y-8 font-mono">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide font-sans">
          Platform Settings & System Information
        </h1>
        <p className="text-sm text-slate-400 mt-1 font-sans">
          Manage user credentials, role permissions, JWT tokens, and platform runtime configurations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        {/* User Account Info */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-3 text-cyan-400 pb-3 border-b border-slate-800">
            <UserIcon className="w-5 h-5" />
            <h2 className="text-sm font-bold text-white">Active Analyst Profile</h2>
          </div>
          <div className="space-y-2 text-slate-300">
            <div>Email Address: <span className="text-white font-bold">{user?.email || 'admin@securesupply.ai'}</span></div>
            <div>Full Name: <span className="text-white font-bold">{user?.full_name || 'Security Administrator'}</span></div>
            <div>Assigned Role: <span className="text-cyan-400 font-bold uppercase">{user?.role || 'ADMIN'}</span></div>
            <div>Account Status: <span className="text-emerald-400 font-bold">ACTIVE</span></div>
          </div>
        </div>

        {/* System Architecture */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-3 text-cyan-400 pb-3 border-b border-slate-800">
            <Server className="w-5 h-5" />
            <h2 className="text-sm font-bold text-white">Platform System Runtime</h2>
          </div>
          <div className="space-y-2 text-slate-300">
            <div>Backend Engine: <span className="text-white font-bold">FastAPI / Python 3.14</span></div>
            <div>ML Model: <span className="text-white font-bold">RandomForestClassifier (scikit-learn)</span></div>
            <div>Database: <span className="text-white font-bold">PostgreSQL / SQLite</span></div>
            <div>SBOM Format: <span className="text-cyan-400 font-bold">CycloneDX 1.4 JSON</span></div>
          </div>
        </div>
      </div>
    </div>
  );
};
