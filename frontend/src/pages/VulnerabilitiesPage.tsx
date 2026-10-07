import React, { useEffect, useState } from 'react';
import { Search, Filter, AlertTriangle, ExternalLink, Shield } from 'lucide-react';
import { vulnerabilityService } from '../services/api';
import { Vulnerability } from '../types';

export const VulnerabilitiesPage: React.FC = () => {
  const [vulns, setVulns] = useState<Vulnerability[]>([]);
  const [severityFilter, setSeverityFilter] = useState('');
  const [searchCve, setSearchCve] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVulnerabilities();
  }, [severityFilter, searchCve]);

  const fetchVulnerabilities = async () => {
    setLoading(true);
    try {
      const data = await vulnerabilityService.listVulnerabilities(severityFilter, searchCve);
      setVulns(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-wide">
          Vulnerability Intelligence Database
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Integrated intelligence from National Vulnerability Database (NVD), OSV.dev, and GitHub Security Advisories.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchCve}
            onChange={(e) => setSearchCve(e.target.value)}
            placeholder="Search CVE ID or advisory title..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-slate-400">Severity Filter:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex justify-center p-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">CVE / Advisory ID</th>
                <th className="px-6 py-3.5">Package Target</th>
                <th className="px-6 py-3.5">Severity</th>
                <th className="px-6 py-3.5">CVSS v3 Score</th>
                <th className="px-6 py-3.5">Title & Summary</th>
                <th className="px-6 py-3.5">Remediation Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {vulns.map((v) => (
                <tr key={v.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-cyan-400">{v.cve_id || v.osv_id}</td>
                  <td className="px-6 py-4 text-white font-bold">{v.dependency_name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                      v.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                      v.severity === 'HIGH' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                      'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}>
                      {v.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold text-white">{v.cvss_score} / 10.0</td>
                  <td className="px-6 py-4 text-slate-300 max-w-md">{v.title}</td>
                  <td className="px-6 py-4 text-emerald-400 font-bold">{v.fixed_version || 'Upgrade Available'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
