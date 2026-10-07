export type UserRole = 'admin' | 'security_engineer' | 'developer';
export type ProjectType = 'python' | 'javascript' | 'java' | 'multi';
export type SourceType = 'zip' | 'file' | 'git' | 'sbom';
export type ScanStatus = 'pending' | 'scanning' | 'completed' | 'failed';
export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Critical';
export type VulnerabilitySeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type PolicyAction = 'ALLOW' | 'WARN' | 'RECOMMEND_UPDATE' | 'QUARANTINE' | 'BLOCK';
export type RecommendationAction = 'UPGRADE' | 'DOWNGRADE' | 'REPLACE' | 'REMOVE' | 'PATCH';

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Project {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  project_type: ProjectType;
  source_type: SourceType;
  git_url?: string;
  created_at: string;
  updated_at: string;
  latest_scan_risk_score?: number;
  latest_scan_risk_level?: RiskLevel;
  scans_count?: number;
}

export interface Dependency {
  id: number;
  scan_id: number;
  name: string;
  version: string;
  ecosystem: string;
  is_direct: boolean;
  parent_name?: string;
  license?: string;
  suspicion_score: number;
  suspicious_reasons: string[];
  vulnerability_count?: number;
}

export interface Vulnerability {
  id: number;
  scan_id: number;
  dependency_id: number;
  dependency_name?: string;
  dependency_version?: string;
  cve_id?: string;
  osv_id?: string;
  title: string;
  description?: string;
  severity: VulnerabilitySeverity;
  cvss_score: number;
  fixed_version?: string;
  reference_urls: string[];
}

export interface AttackIndicator {
  id: number;
  scan_id: number;
  dependency_name: string;
  attack_type: string;
  severity: VulnerabilitySeverity;
  description: string;
  evidence: Record<string, any>;
  created_at: string;
}

export interface SecurityPolicy {
  id: number;
  name: string;
  description?: string;
  max_allowed_cvss: number;
  max_allowed_risk_score: number;
  max_suspicion_score: number;
  block_typosquatting: boolean;
  blocked_packages: string[];
  action: PolicyAction;
  is_active: boolean;
  created_at: string;
}

export interface PolicyDecision {
  id: number;
  scan_id: number;
  policy_name: string;
  status: PolicyAction;
  violations: string[];
  created_at: string;
}

export interface Recommendation {
  id: number;
  scan_id: number;
  dependency_name: string;
  current_version: string;
  recommended_action: RecommendationAction;
  recommended_version?: string;
  rationale: string;
  severity: VulnerabilitySeverity;
  created_at: string;
}

export interface RiskResult {
  id: number;
  scan_id: number;
  overall_score: number;
  risk_level: RiskLevel;
  vulnerability_score: number;
  suspicion_score: number;
  reputation_score: number;
  feature_breakdown: Record<string, any>;
  ml_model_version: string;
}

export interface ScanSession {
  id: number;
  project_id: number;
  status: ScanStatus;
  risk_score: number;
  risk_level: RiskLevel;
  total_dependencies: number;
  vulnerable_dependencies: number;
  suspicious_dependencies: number;
  attack_indicators_count: number;
  policy_status: PolicyAction;
  sbom_content?: string;
  created_at: string;
  completed_at?: string;
}

export interface ScanDetail extends ScanSession {
  dependencies: Dependency[];
  vulnerabilities: Vulnerability[];
  risk_result?: RiskResult;
  attack_indicators: AttackIndicator[];
  policy_decisions: PolicyDecision[];
  recommendations: Recommendation[];
}

export interface ExecutiveSummary {
  total_projects: number;
  total_scans: number;
  total_dependencies: number;
  vulnerable_dependencies: number;
  critical_findings: number;
  high_findings: number;
  blocked_dependencies: number;
  risk_distribution: Record<string, number>;
  severity_breakdown: Record<string, number>;
  recent_scans: ScanSession[];
  scan_trends: Array<{
    date: string;
    risk_score: number;
    vulnerabilities: number;
    total_deps: number;
  }>;
}
