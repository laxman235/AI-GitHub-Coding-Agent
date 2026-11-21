import os
import pytest
from agent.services.repository_service import RepositoryService


def test_scan_sample_spring_boot_app():
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample-spring-boot-app")
    service = RepositoryService(sample_path)
    arch = service.scan_repository()

    assert arch.java_version == "21"
    assert arch.build_tool == "Maven"
    assert any("spring-boot-starter-web" in d for d in arch.dependencies)
    assert len(arch.controllers) >= 1
    assert any(c.class_name == "ProductController" for c in arch.controllers)
    assert len(arch.services) >= 1
    assert any(s.class_name == "ProductService" for s in arch.services)
    assert len(arch.repositories) >= 1
    assert len(arch.entities) >= 1
    assert len(arch.tests) >= 2


def test_safe_read_and_write(tmp_path):
    service = RepositoryService(str(tmp_path))

    # Writing an allowed file
    service.write_file_safe("src/TestClass.java", "public class TestClass {}", [".java"])
    content = service.read_file_safe("src/TestClass.java")
    assert "TestClass" in content

    # Disallowed extension
    with pytest.raises(PermissionError):
        service.write_file_safe("script.exe", "binary", [".java"])

    # Forbidden filename
    with pytest.raises(PermissionError):
        service.write_file_safe(".env", "SECRET=123", [".env", ".java"])
