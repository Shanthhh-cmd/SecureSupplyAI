import React, { useEffect, useState } from 'react';
import { ShieldAlert, Plus, CheckCircle, ShieldCheck, X } from 'lucide-react';
import { policyService } from '../services/api';
import { SecurityPolicy } from '../types';

export const PoliciesPage: React.FC = () => {
  const [policies, setPolicies] = useState<SecurityPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Policy Form State
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [maxCvss, setMaxCvss] = useState(7.0);
  const [maxRisk, setMaxRisk] = useState(50.0);
  const [maxSuspicion, setMaxSuspicion] = useState(40.0);
  const [blockTyposquatting, setBlockTyposquatting] = useState(true);
  const [blockedPackagesStr, setBlockedPackagesStr] = useState('flatmap-stream, malicious-pkg');
  const [action, setAction] = useState('BLOCK');

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const data = await policyService.listPolicies();
      setPolicies(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleActivatePolicy = async (id: number) => {
    await policyService.activatePolicy(id);
    fetchPolicies();
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    const blockedList = blockedPackagesStr.split(',').map((p) => p.trim()).filter(Boolean);
    await policyService.createPolicy({
      name,
      description,
      max_allowed_cvss: maxCvss,
      max_allowed_risk_score: maxRisk,
      max_suspicion_score: maxSuspicion,
      block_typosquatting: blockTyposquatting,
      blocked_packages: blockedList,
      action: action as any,
      is_active: true
    });
    setShowModal(false);
    fetchPolicies();
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">
            Automated Security Policy Engine
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Define organization-wide thresholds for vulnerability CVSS scores, risk metrics, typosquatting blocks, and package blacklists.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2.5 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-lg shadow-cyan-500/20 w-fit"
        >
          <Plus className="w-4 h-4" />
          <span>Create Custom Security Policy</span>
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center p-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {policies.map((p) => (
            <div
              key={p.id}
              className={`bg-slate-900 border rounded-2xl p-6 transition-all shadow-xl font-mono text-xs ${
                p.is_active ? 'border-cyan-500/80 shadow-cyan-950/30' : 'border-slate-800'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-base font-bold text-white">{p.name}</h3>
                    {p.is_active ? (
                      <span className="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2.5 py-0.5 rounded-full text-[10px] font-bold flex items-center space-x-1">
                        <CheckCircle className="w-3 h-3" />
                        <span>ACTIVE POLICY</span>
                      </span>
                    ) : (
                      <button
                        onClick={() => handleActivatePolicy(p.id)}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-0.5 rounded text-[10px]"
                      >
                        Activate Policy
                      </button>
                    )}
                  </div>
                  <p className="text-slate-400 text-xs font-sans">{p.description}</p>
                </div>

                <div className="text-right">
                  <span className="text-slate-500 block text-[10px]">Action Strategy:</span>
                  <span className={`font-bold text-sm ${p.action === 'BLOCK' ? 'text-rose-400' : 'text-amber-400'}`}>
                    {p.action}
                  </span>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-800">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Max Allowed CVSS:</span>
                  <span className="text-white font-bold text-sm">{p.max_allowed_cvss} / 10.0</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Max Risk Score:</span>
                  <span className="text-white font-bold text-sm">{p.max_allowed_risk_score} / 100</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Max Suspicion Score:</span>
                  <span className="text-white font-bold text-sm">{p.max_suspicion_score} / 100</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Typosquatting Protection:</span>
                  <span className="text-cyan-400 font-bold text-sm">{p.block_typosquatting ? 'ENABLED' : 'DISABLED'}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
                <span>Blacklisted Packages: <span className="text-rose-400 font-bold">{(p.blocked_packages || []).join(', ') || 'None'}</span></span>
                <span>Created: {new Date(p.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-base font-bold text-white">Create Security Policy</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePolicy} className="space-y-4 font-mono text-xs">
              <div>
                <label className="block text-slate-300 mb-1">Policy Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. PCI-DSS Compliance Policy"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-300 mb-1">Max CVSS Allowed</label>
                  <input
                    type="number"
                    step="0.1"
                    value={maxCvss}
                    onChange={(e) => setMaxCvss(parseFloat(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1">Max Risk Score</label>
                  <input
                    type="number"
                    value={maxRisk}
                    onChange={(e) => setMaxRisk(parseFloat(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Blacklisted Packages (comma-separated)</label>
                <input
                  type="text"
                  value={blockedPackagesStr}
                  onChange={(e) => setBlockedPackagesStr(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Enforcement Action Strategy</label>
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                >
                  <option value="BLOCK">BLOCK (Halt Deployment)</option>
                  <option value="WARN">WARN (Log Warning & Continue)</option>
                  <option value="QUARANTINE">QUARANTINE (Isolate Build Artifact)</option>
                </select>
              </div>

              <div className="pt-3 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-cyan-500 text-slate-950 font-bold rounded-xl shadow-lg shadow-cyan-500/20"
                >
                  Save & Activate Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
