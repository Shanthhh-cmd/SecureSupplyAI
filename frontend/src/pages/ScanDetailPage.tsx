import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ShieldAlert, AlertTriangle, Layers, Ban, CheckCircle,
  FileCode, Cpu, ShieldCheck, Download, ArrowLeft, Bug
} from 'lucide-react';
import { scanService, reportService } from '../services/api';
import { ScanDetail } from '../types';

export const ScanDetailPage: React.FC = () => {
  const { scanId } = useParams<{ scanId: string }>();
  const [scan, setScan] = useState<ScanDetail | null>(null);
  const [activeTab, setActiveTab] = useState<'deps' | 'vulns' | 'attacks' | 'risk' | 'policy' | 'recs' | 'sbom'>('deps');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (scanId) fetchScanDetail(parseInt(scanId));
  }, [scanId]);

  const fetchScanDetail = async (id: number) => {
    try {
      const data = await scanService.getScanDetail(id);
      setScan(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !scan) {
    return (
      <div className="flex justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <Link to="/projects" className="text-xs font-mono text-cyan-400 hover:underline flex items-center space-x-1 mb-2">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Projects</span>
        </Link>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-wide flex items-center space-x-3">
              <span>Security Scan Session #{scan.id}</span>
              <span className={`px-3 py-0.5 rounded-full text-xs font-mono font-bold uppercase ${
                scan.risk_level === 'Critical' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                scan.risk_level === 'High' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                scan.risk_level === 'Medium' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                'bg-emerald-950 text-emerald-400 border border-emerald-800'
              }`}>
                {scan.risk_level} Risk Level ({scan.risk_score}/100)
              </span>
            </h1>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Evaluated at: {new Date(scan.created_at).toLocaleString()} &bull; Policy Status: <span className="font-bold text-cyan-400">{scan.policy_status}</span>
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <a
              href={reportService.getDownloadUrl(scan.id)}
              download
              className="bg-slate-900 hover:bg-slate-800 text-white font-mono text-xs px-3.5 py-2.5 rounded-xl border border-slate-800 flex items-center space-x-2 transition-colors"
            >
              <Download className="w-4 h-4 text-cyan-400" />
              <span>Export PDF Report</span>
            </a>
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-slate-400 text-xs block">Dependencies</span>
          <span className="text-xl font-bold text-white">{scan.total_dependencies}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-slate-400 text-xs block">Vulnerabilities</span>
          <span className="text-xl font-bold text-amber-400">{scan.vulnerable_dependencies}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-slate-400 text-xs block">Attack Indicators</span>
          <span className="text-xl font-bold text-rose-400">{scan.attack_indicators_count}</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-slate-400 text-xs block">Suspicious Packages</span>
          <span className="text-xl font-bold text-purple-400">{scan.suspicious_dependencies}</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-800 flex space-x-4 overflow-x-auto text-xs font-mono">
        {[
          { key: 'deps', label: `Dependencies (${scan.dependencies.length})`, icon: Layers },
          { key: 'vulns', label: `Vulnerabilities (${scan.vulnerabilities.length})`, icon: Bug },
          { key: 'attacks', label: `Attack Indicators (${scan.attack_indicators.length})`, icon: ShieldAlert },
          { key: 'risk', label: 'ML Risk Analysis', icon: Cpu },
          { key: 'policy', label: 'Policy Decisions', icon: ShieldCheck },
          { key: 'recs', label: `Recommendations (${scan.recommendations.length})`, icon: AlertTriangle },
          { key: 'sbom', label: 'CycloneDX SBOM', icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`pb-3 px-2 border-b-2 font-semibold flex items-center space-x-2 whitespace-nowrap transition-colors ${
                activeTab === tab.key
                  ? 'border-cyan-400 text-cyan-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      {/* 1. Dependencies */}
      {activeTab === 'deps' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Name</th>
                <th className="px-6 py-3.5">Version</th>
                <th className="px-6 py-3.5">Ecosystem</th>
                <th className="px-6 py-3.5">Type</th>
                <th className="px-6 py-3.5">License</th>
                <th className="px-6 py-3.5">Suspicion Score</th>
                <th className="px-6 py-3.5">Triggers</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {scan.dependencies.map((d) => (
                <tr key={d.id} className="hover:bg-slate-800/40">
                  <td className="px-6 py-4 font-bold text-white">{d.name}</td>
                  <td className="px-6 py-4 text-cyan-400">{d.version}</td>
                  <td className="px-6 py-4 text-slate-400">{d.ecosystem}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${d.is_direct ? 'bg-cyan-950 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>
                      {d.is_direct ? 'Direct' : 'Transitive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-400">{d.license || 'UNKNOWN'}</td>
                  <td className="px-6 py-4">
                    <span className={`font-bold ${d.suspicion_score > 40 ? 'text-rose-400' : 'text-slate-300'}`}>
                      {d.suspicion_score} / 100
                    </span>
                  </td>
                  <td className="px-6 py-4 text-[11px]">
                    {d.suspicious_reasons.length > 0 ? (
                      <span className="text-amber-400">{d.suspicious_reasons.join(', ')}</span>
                    ) : (
                      <span className="text-slate-500">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 2. Vulnerabilities */}
      {activeTab === 'vulns' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-xs text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">CVE / OSV ID</th>
                <th className="px-6 py-3.5">Dependency</th>
                <th className="px-6 py-3.5">Severity</th>
                <th className="px-6 py-3.5">CVSS</th>
                <th className="px-6 py-3.5">Title</th>
                <th className="px-6 py-3.5">Fixed Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {scan.vulnerabilities.map((v) => (
                <tr key={v.id} className="hover:bg-slate-800/40">
                  <td className="px-6 py-4 font-bold text-cyan-400">{v.cve_id || v.osv_id}</td>
                  <td className="px-6 py-4 text-white">{v.dependency_name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                      v.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                      v.severity === 'HIGH' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                      'bg-amber-950 text-amber-400 border border-amber-800'
                    }`}>
                      {v.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold text-white">{v.cvss_score}</td>
                  <td className="px-6 py-4 text-slate-300">{v.title}</td>
                  <td className="px-6 py-4 text-emerald-400 font-bold">{v.fixed_version || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 3. Attack Indicators */}
      {activeTab === 'attacks' && (
        <div className="space-y-4">
          {scan.attack_indicators.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 font-mono text-xs">
              No active supply chain attack indicators (typosquatting, dependency confusion, takeover) detected.
            </div>
          ) : (
            scan.attack_indicators.map((atk) => (
              <div key={atk.id} className="bg-rose-950/20 border border-rose-800/60 rounded-2xl p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-rose-400 font-mono text-sm uppercase tracking-wide">
                    {atk.attack_type} Attack Indicator
                  </span>
                  <span className="bg-rose-950 text-rose-400 px-2 py-0.5 rounded text-[10px] font-mono border border-rose-800 uppercase">
                    {atk.severity} SEVERITY
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-mono">{atk.description}</p>
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-[11px] text-slate-400 space-y-1">
                  <div>Package Target: <span className="text-cyan-400">{atk.dependency_name}</span></div>
                  <div>Evidence Payload: {JSON.stringify(atk.evidence)}</div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* 4. Risk Analysis */}
      {activeTab === 'risk' && scan.risk_result && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono text-center">
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-400 text-xs block">Overall Risk Score</span>
              <span className="text-2xl font-bold text-cyan-400">{scan.risk_result.overall_score} / 100</span>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-400 text-xs block">Vulnerability Subscore</span>
              <span className="text-2xl font-bold text-amber-400">{scan.risk_result.vulnerability_score}</span>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-400 text-xs block">Suspicion Subscore</span>
              <span className="text-2xl font-bold text-purple-400">{scan.risk_result.suspicion_score}</span>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-400 text-xs block">Maintainer Reputation</span>
              <span className="text-2xl font-bold text-emerald-400">{scan.risk_result.reputation_score} / 100</span>
            </div>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-2">
            <h3 className="font-bold text-white mb-2">Random Forest Feature Vector Breakdown</h3>
            <pre className="text-cyan-400 overflow-x-auto">
              {JSON.stringify(scan.risk_result.feature_breakdown, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* 5. Policy Decisions */}
      {activeTab === 'policy' && (
        <div className="space-y-4 font-mono">
          {scan.policy_decisions.map((pd) => (
            <div key={pd.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{pd.policy_name}</span>
                <span className={`px-3 py-1 rounded text-xs font-bold ${
                  pd.status === 'BLOCK' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                }`}>
                  {pd.status}
                </span>
              </div>
              {pd.violations.length > 0 ? (
                <div className="space-y-1 text-xs">
                  <span className="text-rose-400 font-semibold">Policy Violations Triggered:</span>
                  <ul className="list-disc pl-5 text-slate-300 space-y-1">
                    {pd.violations.map((v, i) => (
                      <li key={i}>{v}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-xs text-emerald-400">All security policy rules passed cleanly.</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 6. Recommendations */}
      {activeTab === 'recs' && (
        <div className="space-y-4 font-mono text-xs">
          {scan.recommendations.map((r) => (
            <div key={r.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{r.dependency_name}</span>
                <span className="bg-cyan-950 text-cyan-400 px-2.5 py-1 rounded font-bold border border-cyan-800">
                  ACTION: {r.recommended_action} {r.recommended_version ? `\u2192 ${r.recommended_version}` : ''}
                </span>
              </div>
              <p className="text-slate-300">{r.rationale}</p>
            </div>
          ))}
        </div>
      )}

      {/* 7. CycloneDX SBOM */}
      {activeTab === 'sbom' && (
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 font-mono text-xs">
          <div className="flex items-center justify-between mb-4">
            <span className="text-slate-400">CycloneDX 1.4 JSON Software Bill of Materials</span>
          </div>
          <textarea
            readOnly
            rows={15}
            value={scan.sbom_content || 'No SBOM generated.'}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl p-4 text-cyan-400 font-mono text-xs focus:outline-none"
          />
        </div>
      )}
    </div>
  );
};
