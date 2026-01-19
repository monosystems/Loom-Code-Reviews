# Contributing to Loom

Thank you for your interest in contributing to Loom! This document outlines the guidelines for contributing.

## Development Workflow

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Loom-Code-Reviews.git
   cd Loom-Code-Reviews
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
  6. **Create a Pull Request** against the `main` branch

## Code Style Guide

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Run formatting and linting before committing:
  ```bash
  black src/ tests/
  ruff check src/ tests/ --fix
  mypy src/
  ```
- Write docstrings for all public functions and classes

## PR Guidelines

- PRs should be focused and address a single concern
- Include a clear description of the changes
- Link any related issues
- Ensure all tests pass
- Update documentation as needed

## Testing Requirements

- Write unit tests for new functionality
- Ensure integration tests pass
- Aim for meaningful test coverage

## Questions?

Open an issue for discussion.
