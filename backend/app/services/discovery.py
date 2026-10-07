import os
import json
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

class DependencyInfo:
    def __init__(self, name: str, version: str, ecosystem: str, is_direct: bool = True, parent_name: str = None, license: str = None):
        self.name = name
        self.version = version.strip() if version else "0.0.0"
        self.ecosystem = ecosystem # PyPI, npm, Maven
        self.is_direct = is_direct
        self.parent_name = parent_name
        self.license = license or "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "ecosystem": self.ecosystem,
            "is_direct": self.is_direct,
            "parent_name": self.parent_name,
            "license": self.license
        }

class DiscoveryEngine:
    @staticmethod
    def parse_python_requirements(content: str) -> List[DependencyInfo]:
        deps = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-e") or line.startswith("-r"):
                continue
            
            # Clean specifiers like package==1.2.3, package>=1.2.3, package~=1.2.3
            parts = re.split(r'(==|>=|<=|~=|>|<|!=)', line)
            name = parts[0].strip()
            version = "1.0.0"
            if len(parts) >= 3:
                version = parts[2].split(";")[0].split("#")[0].strip()
            
            if name:
                deps.append(DependencyInfo(name=name, version=version, ecosystem="PyPI", is_direct=True))
        return deps

    @staticmethod
    def parse_package_json(content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = json.loads(content)
            direct_deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})

            for name, ver_spec in direct_deps.items():
                version = re.sub(r'[\^~>=<]', '', ver_spec).strip()
                deps.append(DependencyInfo(name=name, version=version or "1.0.0", ecosystem="npm", is_direct=True))

            for name, ver_spec in dev_deps.items():
                version = re.sub(r'[\^~>=<]', '', ver_spec).strip()
                deps.append(DependencyInfo(name=name, version=version or "1.0.0", ecosystem="npm", is_direct=False, parent_name="devDependencies"))

        except Exception:
            pass
        return deps

    @staticmethod
    def parse_pom_xml(content: str) -> List[DependencyInfo]:
        deps = []
        try:
            root = ET.fromstring(content)
            ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
            
            # Find all dependency tags with or without namespace
            for dep in root.findall('.//dependency') or root.findall('.//mvn:dependency', ns):
                group_id = dep.find('groupId') or dep.find('mvn:groupId', ns)
                artifact_id = dep.find('artifactId') or dep.find('mvn:artifactId', ns)
                version_elem = dep.find('version') or dep.find('mvn:version', ns)

                g_text = group_id.text if group_id is not None else ""
                a_text = artifact_id.text if artifact_id is not None else ""
                v_text = version_elem.text if version_elem is not None else "1.0.0"

                if g_text and a_text:
                    full_name = f"{g_text}:{a_text}"
                    deps.append(DependencyInfo(name=full_name, version=v_text, ecosystem="Maven", is_direct=True))
        except Exception:
            pass
        return deps

    @staticmethod
    def parse_cyclonedx_sbom(content: str) -> List[DependencyInfo]:
        deps = []
        try:
            data = json.loads(content)
            components = data.get("components", [])
            for comp in components:
                name = comp.get("name", "")
                version = comp.get("version", "1.0.0")
                purl = comp.get("purl", "")
                ecosystem = "PyPI"
                if "pkg:npm" in purl:
                    ecosystem = "npm"
                elif "pkg:maven" in purl:
                    ecosystem = "Maven"

                licenses = comp.get("licenses", [])
                lic_name = "UNKNOWN"
                if licenses and isinstance(licenses, list):
                    lic_obj = licenses[0]
                    if "license" in lic_obj:
                        lic_name = lic_obj["license"].get("id") or lic_obj["license"].get("name", "UNKNOWN")

                if name:
                    deps.append(DependencyInfo(name=name, version=version, ecosystem=ecosystem, is_direct=True, license=lic_name))
        except Exception:
            pass
        return deps

    @classmethod
    def discover_dependencies_from_path(cls, path: str) -> List[DependencyInfo]:
        all_deps = []
        if os.path.isfile(path):
            filename = os.path.basename(path).lower()
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if "requirements" in filename or filename.endswith(".txt"):
                all_deps.extend(cls.parse_python_requirements(content))
            elif filename == "package.json":
                all_deps.extend(cls.parse_package_json(content))
            elif filename == "pom.xml":
                all_deps.extend(cls.parse_pom_xml(content))
            elif filename.endswith(".json") and ("bom" in filename or "cyclonedx" in content or "components" in content):
                all_deps.extend(cls.parse_cyclonedx_sbom(content))
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    file_path = os.path.join(root, f)
                    fname_lower = f.lower()
                    if fname_lower in ["requirements.txt", "package.json", "pom.xml"] or fname_lower.endswith("-sbom.json") or fname_lower.endswith(".bom.json"):
                        all_deps.extend(cls.discover_dependencies_from_path(file_path))

        # Deduplicate dependencies by (name, ecosystem)
        unique_deps = {}
        for d in all_deps:
            key = f"{d.ecosystem}:{d.name.lower()}"
            if key not in unique_deps:
                unique_deps[key] = d
        
        return list(unique_deps.values())
