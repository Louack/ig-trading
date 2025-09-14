# IG Trading API Gateway Test Suite

This directory contains the test suite for the IG Trading API gateway submodule.

## Structure

```
api_gateway/
├── tests/
│   ├── unit/                    # Unit tests (fast, isolated, no external dependencies)
│   │   ├── test_validators.py   # Tests for input validation
│   │   ├── test_error_handling.py # Tests for error handling decorators
│   │   ├── test_rest_client.py  # Tests for REST client with mocking
│   │   └── test_auth.py         # Tests for authentication
│   ├── integration/             # Integration tests (slower, require external services)
│   ├── fixtures/                # Test data and fixtures
│   └── conftest.py             # Shared pytest configuration and fixtures
└── ig_client/                   # The actual API client code
```

## Running Tests

### Run all unit tests
```bash
uv run pytest api_gateway/tests/unit/ -v
```

### Run specific test file
```bash
uv run pytest api_gateway/tests/unit/test_validators.py -v
```

### Run with coverage
```bash
uv run pytest api_gateway/tests/unit/ --cov=api_gateway --cov-report=html
```

### Run only fast tests (unit tests)
```bash
uv run pytest -m unit -v
```

### Run integration tests (requires API access)
```bash
uv run pytest -m integration -v
```

## Test Categories

- **Unit Tests**: Fast, isolated tests that don't require external dependencies
- **Integration Tests**: Tests that interact with real external services
- **Validation Tests**: Tests focused on input validation logic
- **Auth Tests**: Tests related to authentication functionality

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (require external services)
- `@pytest.mark.validation` - Validation-specific tests
- `@pytest.mark.auth` - Authentication-specific tests
- `@pytest.mark.slow` - Tests that take a long time to run

## Fixtures

The `conftest.py` file provides shared fixtures for:
- Mock IG client instances
- Sample API responses
- Test data for various scenarios
- Mock authentication sessions

## Coverage

The test suite aims for 80%+ code coverage. Coverage reports are generated in HTML format in the `htmlcov/` directory.

## Best Practices

1. **Unit tests should be fast** - No network calls, no file I/O
2. **Use mocking** - Mock external dependencies
3. **Test edge cases** - Invalid inputs, error conditions
4. **Parametrize tests** - Use `@pytest.mark.parametrize` for multiple test cases
5. **Clear test names** - Test names should describe what is being tested
6. **One assertion per test** - Keep tests focused and simple

## Example Test

```python
@pytest.mark.unit
@pytest.mark.validation
def test_validate_epic_valid(valid_epic):
    """Test valid epic validation."""
    result = PathValidators.validate_epic(valid_epic)
    assert result == valid_epic

@pytest.mark.unit
@pytest.mark.validation
@pytest.mark.parametrize("epic", [
    "IX.D.NASDAQ.IFE.IP",
    "CS.D.EURGBP.CFD.IP",
])
def test_validate_epic_valid_cases(epic):
    """Test various valid epic formats."""
    result = PathValidators.validate_epic(epic)
    assert result == epic
```
