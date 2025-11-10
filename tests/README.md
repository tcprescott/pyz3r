# pyz3r Tests

This directory contains the unit test suite for the pyz3r library.

## Running Tests

### Basic Test Run
```bash
pytest tests/
```

### Verbose Output
```bash
pytest tests/ -v
```

### With Coverage Report
```bash
pytest tests/ --cov=pyz3r --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_exceptions.py -v
```

### Run Specific Test Class or Function
```bash
pytest tests/test_rom.py::TestRomBasic::test_rom_write_byte -v
```

## Test Structure

- `test_exceptions.py` - Tests for exception classes
- `test_misc.py` - Tests for utility functions
- `test_rom.py` - Tests for ROM manipulation
- `test_customizer.py` - Tests for customizer settings conversion
- `test_mystery.py` - Tests for mystery seed generation
- `test_alttpr.py` - Tests for ALTTPR API client
- `conftest.py` - Pytest fixtures and configuration

## Test Coverage

Current coverage: ~49% (79 tests passing)

Coverage focuses on:
- Core utility functions (100% coverage for misc.py)
- Exception classes (100% coverage)
- Customizer conversion logic (88% coverage)
- ROM manipulation functions (41% coverage)
- Mystery seed generation (65% coverage)

## Writing New Tests

When adding new tests:
1. Follow the existing naming conventions (`test_*.py`, `Test*` classes, `test_*` methods)
2. Use descriptive test names that explain what is being tested
3. Include docstrings for test classes and methods
4. Use pytest fixtures from `conftest.py` when appropriate
5. Mock external API calls to avoid network dependencies

## Requirements

Tests require:
- pytest
- pytest-asyncio (for async tests)
- pytest-cov (for coverage reports)

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov
```
