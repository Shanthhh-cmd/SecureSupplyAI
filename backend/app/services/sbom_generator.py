import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

class SBOMGenerator:
    @staticmethod
    def generate_cyclonedx_json(project_name: str, dependencies: List[Dict[str, Any]]) -> str:
        components = []
        for d in dependencies:
            eco_purl_map = {
                "PyPI": f"pkg:pypi/{d.get('name')}@{d.get('version')}",
                "npm": f"pkg:npm/{d.get('name')}@{d.get('version')}",
                "Maven": f"pkg:maven/{d.get('name')}@{d.get('version')}"
            }
            purl = eco_purl_map.get(d.get("ecosystem"), f"pkg:generic/{d.get('name')}@{d.get('version')}")
            
            comp = {
                "type": "library",
                "bom-ref": f"{d.get('name')}@{d.get('version')}",
                "name": d.get("name"),
                "version": d.get("version"),
                "purl": purl,
                "licenses": [
                    {
                        "license": {
                            "id": d.get("license") or "MIT"
                        }
                    }
                ]
            }
            components.append(comp)

        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": [
                    {
                        "vendor": "SecureSupply AI",
                        "name": "Dependency Discovery Engine",
                        "version": "1.0.0"
                    }
                ],
                "component": {
                    "type": "application",
                    "name": project_name,
                    "version": "1.0.0"
                }
            },
            "components": components
        }
        return json.dumps(sbom, indent=2)
