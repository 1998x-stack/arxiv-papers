# Tests for arxiv-papers

This directory contains unit and integration tests for the arxiv-papers project.

## Test Structure

- `unit/` - Unit tests for individual modules
- `integration/` - Integration tests for combined functionality
- `fixtures/` - Test data and fixtures

## Running Tests

### Run all tests:
```bash
python -m pytest tests/
```

### Run specific test modules:
```bash
python -m pytest tests/unit/test_paper_fetcher.py
python -m pytest tests/unit/test_email_sender.py
python -m pytest tests/integration/
```

### Run with verbose output:
```bash
python -m pytest tests/ -v
```

## Test Coverage

The test suite covers:

### Main arxiv-papers functionality:
- Paper fetching from arXiv API
- Email sending functionality
- Markdown formatting of papers
- Word cloud generation
- Logging setup
- News email scheduling

### AI paper submodule (partially):
- Configuration module
- Utility functions
- Parser functionality
- Paper processing
- Metadata processing

## Test Descriptions

### Unit Tests
Each module has corresponding unit tests that verify:
- Proper initialization
- Edge case handling
- Error condition management
- External dependency mocking
- Input validation

### Integration Tests
End-to-end tests that verify:
- Combined module functionality
- Data flow between components
- Error propagation
- Real-world usage scenarios