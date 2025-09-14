# Template for New Submodule Tests

When creating a new submodule (like `data_collection`), follow this structure:

## Directory Structure

```
your_new_submodule/
├── tests/
│   ├── unit/                    # Unit tests (fast, isolated, no external dependencies)
│   │   ├── test_your_module.py  # Tests for your main module
│   │   └── test_helpers.py      # Tests for helper functions
│   ├── integration/             # Integration tests (slower, require external services)
│   │   └── test_api_integration.py
│   ├── fixtures/                # Test data and fixtures
│   │   └── sample_data.py
│   └── conftest.py             # Shared pytest configuration and fixtures
└── your_module_code/            # Your actual module code
```

## Steps to Set Up Tests for a New Submodule

1. **Create the test directory structure:**
   ```bash
   mkdir -p your_new_submodule/tests/{unit,integration,fixtures}
   ```

2. **Copy the conftest.py template:**
   ```bash
   cp api_gateway/tests/conftest.py your_new_submodule/tests/
   ```

3. **Update pytest.ini to include the new test path:**
   ```ini
   testpaths = api_gateway/tests data_collection/tests your_new_submodule/tests
   ```

4. **Create your first test file:**
   ```python
   # your_new_submodule/tests/unit/test_your_module.py
   import pytest
   from your_new_submodule.your_module import YourClass
   
   class TestYourClass:
       @pytest.mark.unit
       def test_your_method(self):
           # Your test code here
           pass
   ```

5. **Run tests:**
   ```bash
   uv run pytest your_new_submodule/tests/unit/ -v
   ```

## Benefits of This Structure

- **Isolation**: Each submodule has its own tests
- **Scalability**: Easy to add new submodules
- **Maintainability**: Tests are co-located with the code they test
- **Flexibility**: Each submodule can have different test requirements
- **CI/CD Ready**: Easy to run tests for specific submodules

## Example Commands

```bash
# Run all tests for all submodules
uv run pytest -v

# Run tests for specific submodule
uv run pytest api_gateway/tests/ -v
uv run pytest data_collection/tests/ -v

# Run only unit tests across all submodules
uv run pytest -m unit -v

# Run with coverage for specific submodule
uv run pytest api_gateway/tests/ --cov=api_gateway --cov-report=html
```
