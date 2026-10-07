import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert, AlertTriangle, Layers, Ban, TrendingUp,
  ArrowUpRight, ShieldCheck, Activity
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  AreaChart, Area, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { dashboardService } from '../services/api';
import { ExecutiveSummary } from '../types';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const data = await dashboardService.getSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch dashboard summary', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  const severityData = summary ? [
    { name: 'Critical', value: summary.severity_breakdown.CRITICAL || 0, color: '#FF0055' },
    { name: 'High', value: summary.severity_breakdown.HIGH || 0, color: '#FF7700' },
    { name: 'Medium', value: summary.severity_breakdown.MEDIUM || 0, color: '#FFB800' },
    { name: 'Low', value: summary.severity_breakdown.LOW || 0, color: '#00FF66' },
  ] : [];

  const riskData = summary ? [
    { name: 'Critical', value: summary.risk_distribution.Critical || 0, color: '#FF0055' },
    { name: 'High', value: summary.risk_distribution.High || 0, color: '#FF7700' },
    { name: 'Medium', value: summary.risk_distribution.Medium || 0, color: '#FFB800' },
    { name: 'Low', value: summary.risk_distribution.Low || 0, color: '#00FF66' },
  ] : [];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">
            Executive Security posture
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time software supply chain risk, vulnerability intelligence, and attack detection summary.
          </p>
        </div>

        <Link
          to="/projects"
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2.5 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-lg shadow-cyan-500/20 w-fit"
        >
          <span>Run New Intake Scan</span>
          <ArrowUpRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Total Dependencies</span>
            <div className="p-2 bg-blue-950/60 border border-blue-800/60 rounded-xl text-blue-400">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 text-3xl font-bold font-mono text-white">
            {summary?.total_dependencies || 0}
          </div>
          <div className="mt-2 text-xs text-slate-400 flex items-center space-x-1">
            <span className="text-cyan-400 font-semibold">{summary?.total_projects || 0} Projects</span>
            <span>monitored in workspace</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Vulnerable Dependencies</span>
            <div className="p-2 bg-amber-950/60 border border-amber-800/60 rounded-xl text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 text-3xl font-bold font-mono text-amber-400">
            {summary?.vulnerable_dependencies || 0}
          </div>
          <div className="mt-2 text-xs text-slate-400">
            With known CVE or OSV advisories
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Critical Findings</span>
            <div className="p-2 bg-rose-950/60 border border-rose-800/60 rounded-xl text-rose-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 text-3xl font-bold font-mono text-rose-500">
            {summary?.critical_findings || 0}
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Immediate remediation required
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Blocked Dependencies</span>
            <div className="p-2 bg-purple-950/60 border border-purple-800/60 rounded-xl text-purple-400">
              <Ban className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 text-3xl font-bold font-mono text-purple-400">
            {summary?.blocked_dependencies || 0}
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Enforced by security policies
          </div>
        </div>
      </div>

      {/* Visualizations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Severity Breakdown Pie Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-white tracking-wide mb-4 flex items-center justify-between">
            <span>Vulnerability Severity Breakdown</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4 text-xs font-mono">
            {severityData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span className="text-slate-400">{item.name}:</span>
                <span className="text-white font-bold">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Level Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-white tracking-wide mb-4 flex items-center justify-between">
            <span>Project Risk Classification</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4 text-xs font-mono">
            {riskData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span className="text-slate-400">{item.name}:</span>
                <span className="text-white font-bold">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Scan History Trends */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-white tracking-wide mb-4 flex items-center justify-between">
            <span>Scan Risk Trend Timeline</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary?.scan_trends || []}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#00F0FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} />
                <Area type="monotone" dataKey="risk_score" stroke="#00F0FF" fillOpacity={1} fill="url(#colorRisk)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Scans Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Recent Security Scan Sessions</h2>
          <Link to="/projects" className="text-xs text-cyan-400 hover:text-cyan-300 font-mono">View All Projects &rarr;</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Scan ID</th>
                <th className="px-6 py-3.5">Risk Level</th>
                <th className="px-6 py-3.5">Risk Score</th>
                <th className="px-6 py-3.5">Dependencies</th>
                <th className="px-6 py-3.5">Vulnerable</th>
                <th className="px-6 py-3.5">Policy Action</th>
                <th className="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {summary?.recent_scans.map((scan) => (
                <tr key={scan.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-white">#{scan.id}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                      scan.risk_level === 'Critical' ? 'bg-rose-950 text-rose-400 border border-rose-80 backdrop-blur' :
                      scan.risk_level === 'High' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                      scan.risk_level === 'Medium' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                      'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}>
                      {scan.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-white font-bold">{scan.risk_score} / 100</td>
                  <td className="px-6 py-4 text-slate-300">{scan.total_dependencies}</td>
                  <td className="px-6 py-4 text-amber-400 font-bold">{scan.vulnerable_dependencies}</td>
                  <td className="px-6 py-4">
                    <span className={`font-bold ${
                      scan.policy_status === 'BLOCK' ? 'text-rose-400' : 'text-emerald-400'
                    }`}>
                      {scan.policy_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/scans/${scan.id}`}
                      className="text-cyan-400 hover:text-cyan-300 font-semibold inline-flex items-center space-x-1"
                    >
                      <span>Explore</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
