import React, { useEffect, useState } from 'react';
import { FileText, Download, FileCode, Table } from 'lucide-react';
import { projectService, scanService, reportService } from '../services/api';
import { Project, ScanSession } from '../types';

export const ReportsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [scans, setScans] = useState<ScanSession[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const projList = await projectService.listProjects();
      setProjects(projList);
      if (projList.length > 0) {
        setSelectedProjectId(projList[0].id);
        const scanList = await scanService.getProjectScans(projList[0].id);
        setScans(scanList);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProject = async (projectId: number) => {
    setSelectedProjectId(projectId);
    try {
      const scanList = await scanService.getProjectScans(projectId);
      setScans(scanList);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide">
          Security Reporting & Audit Exports
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Export compliance-ready PDF reports, raw JSON scan summaries, and CSV dependency inventory sheets.
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex items-center space-x-4 font-mono text-xs">
        <span className="text-slate-400 font-bold">Select Project Scope:</span>
        <select
          value={selectedProjectId || ''}
          onChange={(e) => handleSelectProject(parseInt(e.target.value))}
          className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-cyan-500 font-bold"
        >
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name} ({p.project_type})</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center p-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Scan Session ID</th>
                <th className="px-6 py-3.5">Date Completed</th>
                <th className="px-6 py-3.5">Risk Level</th>
                <th className="px-6 py-3.5">Risk Score</th>
                <th className="px-6 py-3.5">Policy Action</th>
                <th className="px-6 py-3.5 text-right">Available Exports</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {scans.map((s) => (
                <tr key={s.id} className="hover:bg-slate-800/40">
                  <td className="px-6 py-4 font-bold text-white">#{s.id}</td>
                  <td className="px-6 py-4 text-slate-400">{new Date(s.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                      s.risk_level === 'Critical' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                      s.risk_level === 'High' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                      s.risk_level === 'Medium' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                      'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}>
                      {s.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold text-white">{s.risk_score} / 100</td>
                  <td className="px-6 py-4 font-bold text-cyan-400">{s.policy_status}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end space-x-2">
                      <a
                        href={reportService.getDownloadUrl(s.id)}
                        download
                        className="bg-slate-950 hover:bg-slate-800 text-cyan-400 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center space-x-1 transition-colors"
                        title="Download PDF"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        <span>PDF Report</span>
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
