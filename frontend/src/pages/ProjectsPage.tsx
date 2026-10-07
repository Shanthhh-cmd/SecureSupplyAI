import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FolderGit2, Plus, Upload, GitBranch, FileCode, Play,
  Trash2, ArrowUpRight, CheckCircle, AlertCircle, X
} from 'lucide-react';
import { projectService, scanService } from '../services/api';
import { Project } from '../types';

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectType, setProjectType] = useState('python');
  const [sourceType, setSourceType] = useState('file');
  const [gitUrl, setGitUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const data = await projectService.listProjects();
      setProjects(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('description', description);
      formData.append('project_type', projectType);
      formData.append('source_type', sourceType);
      if (gitUrl) formData.append('git_url', gitUrl);
      if (selectedFile) formData.append('file', selectedFile);

      await projectService.createProject(formData);
      setShowModal(false);
      resetForm();
      fetchProjects();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setName('');
    setDescription('');
    setProjectType('python');
    setSourceType('file');
    setGitUrl('');
    setSelectedFile(null);
  };

  const handleDeleteProject = async (id: number) => {
    if (confirm('Are you sure you want to delete this project and all its scan history?')) {
      await projectService.deleteProject(id);
      fetchProjects();
    }
  };

  const handleTriggerScan = async (projectId: number) => {
    try {
      await scanService.triggerScan(projectId);
      fetchProjects();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide">
            Project Intake & Scan Repository
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Submit source code ZIP archives, manifest files, SBOMs, or Git URLs for immediate security evaluation.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2.5 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-lg shadow-cyan-500/20 w-fit"
        >
          <Plus className="w-4 h-4" />
          <span>Intake New Project</span>
        </button>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="flex justify-center p-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-6 transition-all shadow-lg flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-cyan-400">
                      <FolderGit2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base leading-tight">{project.name}</h3>
                      <span className="text-[10px] font-mono text-cyan-400 uppercase bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                        {project.project_type} &bull; {project.source_type}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteProject(project.id)}
                    className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                    title="Delete project"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <p className="text-xs text-slate-400 mt-4 line-clamp-2">
                  {project.description || 'No description provided.'}
                </p>

                <div className="mt-6 pt-4 border-t border-slate-800/80 grid grid-cols-2 gap-4 text-xs font-mono">
                  <div>
                    <span className="text-slate-500 block">Risk Score:</span>
                    <span className="text-white font-bold text-base">
                      {project.latest_scan_risk_score ?? 0.0} / 100
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Risk Level:</span>
                    <span className={`font-bold text-xs ${
                      project.latest_scan_risk_level === 'Critical' ? 'text-rose-400' :
                      project.latest_scan_risk_level === 'High' ? 'text-orange-400' :
                      project.latest_scan_risk_level === 'Medium' ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      {project.latest_scan_risk_level || 'Low'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between gap-3 pt-4 border-t border-slate-800/80">
                <button
                  onClick={() => handleTriggerScan(project.id)}
                  className="bg-slate-950 hover:bg-slate-800 text-slate-300 font-mono text-xs px-3 py-2 rounded-xl border border-slate-800 flex items-center space-x-1.5 transition-colors"
                >
                  <Play className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Rescan</span>
                </button>

                <Link
                  to={`/scans/${project.id}`}
                  className="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 font-mono text-xs px-3 py-2 rounded-xl border border-cyan-800/50 flex items-center space-x-1 transition-colors"
                >
                  <span>Explore Findings</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Intake Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                <Upload className="w-5 h-5 text-cyan-400" />
                <span>Project Intake & Scanner</span>
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-slate-300 mb-1">Project Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Payments Gateway Microservice"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Optional architectural scope context"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-300 mb-1">Language Ecosystem</label>
                  <select
                    value={projectType}
                    onChange={(e) => setProjectType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="python">Python (pip)</option>
                    <option value="javascript">JavaScript (npm)</option>
                    <option value="java">Java (Maven)</option>
                    <option value="multi">Multi-Ecosystem</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 mb-1">Intake Source Type</label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="file">File Upload (requirements, package.json, pom.xml)</option>
                    <option value="zip">ZIP Source Archive</option>
                    <option value="sbom">CycloneDX SBOM JSON</option>
                    <option value="git">Git Repository URL</option>
                  </select>
                </div>
              </div>

              {sourceType === 'git' ? (
                <div>
                  <label className="block text-slate-300 mb-1">Git Repository URL</label>
                  <input
                    type="url"
                    required
                    value={gitUrl}
                    onChange={(e) => setGitUrl(e.target.value)}
                    placeholder="https://github.com/org/repo.git"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-slate-300 mb-1">Select File</label>
                  <input
                    type="file"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-400 file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-950 file:text-cyan-400"
                  />
                </div>
              )}

              <div className="pt-4 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-xl font-semibold shadow-lg shadow-cyan-500/20 disabled:opacity-50"
                >
                  {submitting ? 'Scanning & Ingesting...' : 'Upload & Start Scan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
