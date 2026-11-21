"""Service to analyze and inspect Java Spring Boot repositories."""
import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class JavaClassMetadata(BaseModel):
    file_path: str
    relative_path: str
    package_name: str = ""
    class_name: str = ""
    class_type: str = "OTHER"  # CONTROLLER, SERVICE, REPOSITORY, ENTITY, DTO, CONFIG, EXCEPTION_HANDLER, TEST, OTHER
    annotations: List[str] = Field(default_factory=list)
    has_test: bool = False
    lines_of_code: int = 0


class RepositoryArchitecture(BaseModel):
    root_path: str
    java_version: str = "21"
    spring_boot_version: Optional[str] = None
    build_tool: str = "Maven"
    product_vision: str = ""
    dependencies: List[str] = Field(default_factory=list)
    controllers: List[JavaClassMetadata] = Field(default_factory=list)
    services: List[JavaClassMetadata] = Field(default_factory=list)
    repositories: List[JavaClassMetadata] = Field(default_factory=list)
    entities: List[JavaClassMetadata] = Field(default_factory=list)
    dtos: List[JavaClassMetadata] = Field(default_factory=list)
    configs: List[JavaClassMetadata] = Field(default_factory=list)
    exception_handlers: List[JavaClassMetadata] = Field(default_factory=list)
    tests: List[JavaClassMetadata] = Field(default_factory=list)
    other_classes: List[JavaClassMetadata] = Field(default_factory=list)
    missing_test_targets: List[str] = Field(default_factory=list)


class RepositoryService:
    """Scans and analyzes Java Spring Boot source code and Maven configurations."""

    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)

    def scan_repository(self) -> RepositoryArchitecture:
        """Perform a complete static analysis of the Java Spring Boot repository."""
        arch = RepositoryArchitecture(root_path=self.root_path)
        self._parse_pom(arch)
        self._load_product_vision(arch)
        self._scan_java_files(arch)
        self._correlate_tests(arch)
        return arch

    def _load_product_vision(self, arch: RepositoryArchitecture) -> None:
        """Load PRODUCT_PROMPT.md if present in repository root."""
        possible_paths = [
            os.path.join(self.root_path, "PRODUCT_PROMPT.md"),
            os.path.join(self.root_path, "..", "PRODUCT_PROMPT.md")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        arch.product_vision = f.read(15000)
                    break
                except Exception:
                    pass

    def _parse_pom(self, arch: RepositoryArchitecture) -> None:
        """Parse pom.xml to extract Java version, Spring Boot parent, and dependencies."""
        pom_path = os.path.join(self.root_path, "pom.xml")
        if not os.path.exists(pom_path):
            return

        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            # Handle XML namespace if present
            ns = ""
            if root.tag.startswith("{"):
                ns = root.tag.split("}")[0] + "}"

            # Check Java version property
            properties = root.find(f"{ns}properties")
            if properties is not None:
                java_ver = properties.find(f"{ns}java.version")
                if java_ver is not None and java_ver.text:
                    arch.java_version = java_ver.text.strip()

            # Check Spring Boot parent
            parent = root.find(f"{ns}parent")
            if parent is not None:
                parent_artifact = parent.find(f"{ns}artifactId")
                parent_version = parent.find(f"{ns}version")
                if parent_artifact is not None and "spring-boot" in (parent_artifact.text or ""):
                    arch.spring_boot_version = parent_version.text.strip() if parent_version is not None else None

            # Extract dependencies
            deps_elem = root.find(f"{ns}dependencies")
            if deps_elem is not None:
                for dep in deps_elem.findall(f"{ns}dependency"):
                    art = dep.find(f"{ns}artifactId")
                    grp = dep.find(f"{ns}groupId")
                    if art is not None and art.text:
                        group_str = f"{grp.text}:" if grp is not None and grp.text else ""
                        arch.dependencies.append(f"{group_str}{art.text.strip()}")
        except Exception as e:
            # Fallback regex parsing if XML has syntax or property issues
            try:
                with open(pom_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                arch.dependencies = re.findall(r"<artifactId>([^<]+)</artifactId>", content)
            except Exception:
                pass

    def _scan_java_files(self, arch: RepositoryArchitecture) -> None:
        """Traverse directories and parse class annotations, package, and class type."""
        for root, _, files in os.walk(self.root_path):
            # Skip hidden, git, or build directories
            if any(part.startswith(".") or part in ["target", "build", "node_modules", ".venv"] for part in root.split(os.sep)):
                continue

            for file in files:
                if file.endswith(".java"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_path)
                    meta = self._parse_java_class(full_path, rel_path)

                    if meta.class_type == "CONTROLLER":
                        arch.controllers.append(meta)
                    elif meta.class_type == "SERVICE":
                        arch.services.append(meta)
                    elif meta.class_type == "REPOSITORY":
                        arch.repositories.append(meta)
                    elif meta.class_type == "ENTITY":
                        arch.entities.append(meta)
                    elif meta.class_type == "DTO":
                        arch.dtos.append(meta)
                    elif meta.class_type == "CONFIG":
                        arch.configs.append(meta)
                    elif meta.class_type == "EXCEPTION_HANDLER":
                        arch.exception_handlers.append(meta)
                    elif meta.class_type == "TEST":
                        arch.tests.append(meta)
                    else:
                        arch.other_classes.append(meta)

    def _parse_java_class(self, full_path: str, rel_path: str) -> JavaClassMetadata:
        """Inspect Java source file content for structure and annotations."""
        meta = JavaClassMetadata(file_path=full_path, relative_path=rel_path)
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            meta.lines_of_code = len(lines)
            content = "".join(lines)

            # Package
            pkg_match = re.search(r"^\s*package\s+([\w\.]+);", content, re.MULTILINE)
            if pkg_match:
                meta.package_name = pkg_match.group(1)

            # Class or Interface or Record name
            class_match = re.search(r"public\s+(?:class|interface|record|enum)\s+([A-Za-z0-9_]+)", content)
            if class_match:
                meta.class_name = class_match.group(1)
            else:
                meta.class_name = os.path.splitext(os.path.basename(full_path))[0]

            # Annotations
            annotations = re.findall(r"@([A-Za-z0-9_]+)", content)
            meta.annotations = list(set(annotations))

            # Class type classification
            if "src/test" in rel_path.replace("\\", "/") or "Test" in meta.class_name or "@Test" in content:
                meta.class_type = "TEST"
            elif any(a in ["RestController", "Controller"] for a in annotations) or "Controller" in meta.class_name:
                meta.class_type = "CONTROLLER"
            elif any(a in ["Service"] for a in annotations) or "Service" in meta.class_name:
                meta.class_type = "SERVICE"
            elif any(a in ["Repository"] for a in annotations) or "Repository" in meta.class_name or "JpaRepository" in content:
                meta.class_type = "REPOSITORY"
            elif any(a in ["Entity", "Table", "Document"] for a in annotations):
                meta.class_type = "ENTITY"
            elif "dto" in rel_path.lower() or "DTO" in meta.class_name or "Request" in meta.class_name or "Response" in meta.class_name or "record" in content:
                meta.class_type = "DTO"
            elif any(a in ["ControllerAdvice", "RestControllerAdvice"] for a in annotations):
                meta.class_type = "EXCEPTION_HANDLER"
            elif any(a in ["Configuration"] for a in annotations) or "Config" in meta.class_name:
                meta.class_type = "CONFIG"
            else:
                meta.class_type = "OTHER"

        except Exception:
            pass

        return meta

    def _correlate_tests(self, arch: RepositoryArchitecture) -> None:
        """Check which Controllers and Services lack corresponding Unit Test classes."""
        test_class_names = {t.class_name for t in arch.tests}
        for svc in arch.services:
            expected_test = f"{svc.class_name}Test"
            if expected_test in test_class_names:
                svc.has_test = True
            else:
                arch.missing_test_targets.append(f"Service: {svc.class_name} (expected {expected_test})")

        for ctrl in arch.controllers:
            expected_test = f"{ctrl.class_name}Test"
            if expected_test in test_class_names:
                ctrl.has_test = True
            else:
                arch.missing_test_targets.append(f"Controller: {ctrl.class_name} (expected {expected_test})")

    def read_file_safe(self, rel_path: str, max_chars: int = 20000) -> str:
        """Safely read file content with length limit."""
        target_path = os.path.join(self.root_path, rel_path)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File not found: {rel_path}")
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
        return content

    def write_file_safe(self, rel_path: str, content: str, allowlist_exts: List[str]) -> None:
        """Write file ensuring allowlist extension check and no path traversal."""
        _, ext = os.path.splitext(rel_path)
        if ext.lower() not in [e.lower() for e in allowlist_exts]:
            raise PermissionError(f"Extension '{ext}' not in allowed extensions: {allowlist_exts}")

        full_path = os.path.abspath(os.path.join(self.root_path, rel_path))
        if not full_path.startswith(self.root_path):
            raise PermissionError("Path traversal attempt detected.")

        # Check dangerous filenames
        base = os.path.basename(full_path).lower()
        if base in [".env", "id_rsa", "credentials", "secrets.json"]:
            raise PermissionError(f"Modifying '{base}' is forbidden.")

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
