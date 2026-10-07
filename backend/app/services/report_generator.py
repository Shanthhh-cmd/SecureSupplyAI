import os
import json
import csv
from io import StringIO
from datetime import datetime, timezone
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportGeneratorService:
    @staticmethod
    def generate_json_report(scan_data: Dict[str, Any], output_file: str) -> str:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(scan_data, f, indent=2, default=str)
        return output_file

    @staticmethod
    def generate_csv_report(scan_data: Dict[str, Any], output_file: str) -> str:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        deps = scan_data.get("dependencies", [])
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Dependency Name", "Version", "Ecosystem", "Direct", "License", "Suspicion Score", "Vulnerabilities"])
            for d in deps:
                writer.writerow([
                    d.get("name"),
                    d.get("version"),
                    d.get("ecosystem"),
                    "Yes" if d.get("is_direct") else "No",
                    d.get("license", "UNKNOWN"),
                    d.get("suspicion_score", 0.0),
                    d.get("vulnerability_count", 0)
                ])
        return output_file

    @staticmethod
    def generate_pdf_report(scan_data: Dict[str, Any], output_file: str) -> str:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        doc = SimpleDocTemplate(output_file, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=14,
            spaceAfter=6
        )
        normal_style = styles['Normal']

        # Header Title
        story.append(Paragraph("SecureSupply AI — Supply Chain Security Report", title_style))
        story.append(Paragraph(f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", normal_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=15))

        # Executive Summary Section
        project_name = scan_data.get("project_name", "Software Project")
        risk_level = scan_data.get("risk_level", "Low")
        risk_score = scan_data.get("risk_score", 0.0)

        story.append(Paragraph("Executive Summary", heading_style))
        
        summary_data = [
            ["Project Name:", project_name, "Overall Risk Level:", risk_level],
            ["Total Dependencies:", str(scan_data.get("total_dependencies", 0)), "Risk Score:", f"{risk_score} / 100"],
            ["Vulnerable Dependencies:", str(scan_data.get("vulnerable_dependencies", 0)), "Policy Decision:", scan_data.get("policy_status", "ALLOW")],
            ["Attack Indicators:", str(scan_data.get("attack_indicators_count", 0)), "Suspicious Packages:", str(scan_data.get("suspicious_dependencies", 0))]
        ]
        
        summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        # Vulnerabilities Table
        story.append(Paragraph("Vulnerability Assessment Findings", heading_style))
        vulns = scan_data.get("vulnerabilities", [])
        if vulns:
            v_table_data = [["Dependency", "CVE / OSV ID", "Severity", "CVSS", "Fixed Version"]]
            for v in vulns[:15]: # Limit to top 15 in PDF summary
                v_table_data.append([
                    v.get("dependency_name", "N/A"),
                    v.get("cve_id") or v.get("osv_id") or "N/A",
                    v.get("severity", "MEDIUM"),
                    str(v.get("cvss_score", 0.0)),
                    v.get("fixed_version", "N/A")
                ])
            v_table = Table(v_table_data, colWidths=[120, 110, 80, 60, 150])
            v_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(v_table)
        else:
            story.append(Paragraph("No known vulnerabilities detected in scanned dependencies.", normal_style))

        story.append(Spacer(1, 15))

        # Recommendations Section
        story.append(Paragraph("Security Recommendations & Remediation", heading_style))
        recs = scan_data.get("recommendations", [])
        if recs:
            r_table_data = [["Dependency", "Action", "Target Version", "Rationale"]]
            for r in recs[:10]:
                r_table_data.append([
                    r.get("dependency_name", "N/A"),
                    r.get("recommended_action", "UPGRADE"),
                    r.get("recommended_version", "Latest"),
                    Paragraph(r.get("rationale", ""), normal_style)
                ])
            r_table = Table(r_table_data, colWidths=[100, 80, 90, 250])
            r_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ]))
            story.append(r_table)
        else:
            story.append(Paragraph("No immediate remediation actions required.", normal_style))

        doc.build(story)
        return output_file
