# Loom Code Reviews

Self-hosted AI code review platform.

## Description

Loom is an AI-powered code review platform that integrates with GitHub and GitLab to provide automated code analysis and feedback.

## Features

- AI-powered code review
- GitHub and GitLab integration
- FastAPI-based backend
- PostgreSQL database
- Docker support

## Quick Start

```bash
# Clone the repository
git clone https://github.com/monosystems/Loom-Code-Reviews.git
cd Loom-Code-Reviews

# Start with Docker
docker-compose up -d
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start services (Docker)
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head
```

## Documentation

See the [docs](./docs/) directory for more information.

## Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Code of Conduct

Please note that this project is governed by our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

For security vulnerabilities, please read our [SECURITY.md](SECURITY.md).

## License

This project is licensed under the AGPL-3.0 license. See the [LICENSE](LICENSE) file for details.
