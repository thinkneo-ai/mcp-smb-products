# Contributing to ThinkNEO MCP SMB Products

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/mcp-smb-products.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `make test`

## Development Setup

```bash
cp .env.example .env    # Configure environment
make migrate            # Set up database
make build              # Build all 8 product images
make up                 # Start services
```

## Pull Request Process

1. Ensure tests pass: `pytest tests/ -v`
2. Update documentation if needed
3. Follow existing code style
4. One feature/fix per PR
5. Reference any related issues

## Code of Conduct

Be respectful, constructive, and professional. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## Questions?

Open a discussion or email hello@thinkneo.ai.
