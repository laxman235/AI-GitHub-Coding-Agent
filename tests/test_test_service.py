import pytest
from agent.services.test_service import TestService, MavenTestResult


def test_parse_maven_success(tmp_path):
    service = TestService(str(tmp_path))
    sample_success_output = """
    [INFO] -------------------------------------------------------
    [INFO]  T E S T S
    [INFO] -------------------------------------------------------
    [INFO] Running com.example.demo.service.ProductServiceTest
    [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.12 s
    [INFO] 
    [INFO] Results:
    [INFO] 
    [INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
    [INFO] 
    [INFO] ------------------------------------------------------------------------
    [INFO] BUILD SUCCESS
    [INFO] ------------------------------------------------------------------------
    """
    res = service._parse_maven_output(sample_success_output, True)
    assert res.success is True
    assert res.tests_run == 8
    assert res.failures == 0
    assert res.compilation_success is True


def test_parse_maven_compilation_failure(tmp_path):
    service = TestService(str(tmp_path))
    sample_fail_output = """
    [INFO] -------------------------------------------------------------
    [ERROR] COMPILATION ERROR : 
    [INFO] -------------------------------------------------------------
    [ERROR] /src/main/java/com/example/demo/Product.java:[15,22] cannot find symbol
      symbol:   class NonExistent
      location: class com.example.demo.Product
    [INFO] 1 error
    [INFO] -------------------------------------------------------------
    [INFO] BUILD FAILURE
    """
    res = service._parse_maven_output(sample_fail_output, False)
    assert res.success is False
    assert res.compilation_success is False
    assert len(res.compilation_errors) >= 1
    assert "cannot find symbol" in res.compilation_errors[0]


def test_parse_maven_test_failure(tmp_path):
    service = TestService(str(tmp_path))
    sample_test_fail = """
    [INFO] Results:
    [INFO] 
    [ERROR] Failures: 
    [ERROR]   ProductServiceTest.testGetProductById:35 expected: <Laptop> but was: <Desktop>
    [INFO] 
    [ERROR] Tests run: 5, Failures: 1, Errors: 0, Skipped: 0
    [INFO] ------------------------------------------------------------------------
    [INFO] BUILD FAILURE
    """
    res = service._parse_maven_output(sample_test_fail, False)
    assert res.success is False
    assert res.failures == 1
    assert any("ProductServiceTest" in t for t in res.failed_tests)
