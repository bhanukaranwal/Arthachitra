# Contributing to Arthachitra (अर्थचित्र)

Thank you for your interest in contributing to Arthachitra! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
git clone https://github.com/your-username/arthachitra.git
cd arthachitra

text
3. **Set up the development environment** (see Development Setup below)
4. **Create a branch** for your feature:
git checkout -b feature/your-feature-name

text

## Development Setup

Follow the setup instructions in [DEV_GUIDE.md](docs/DEV_GUIDE.md) to get your development environment running.

### Quick Setup
./scripts/setup.sh
docker-compose up -d

text

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues and improve stability
- **Features** - Add new functionality
- **Documentation** - Improve docs, tutorials, examples
- **Tests** - Add or improve test coverage
- **Performance** - Optimize performance
- **UI/UX** - Improve user interface and experience
- **Themes** - Create new beautiful themes
- **Brokers** - Add support for new brokers
- **Indicators** - Add new technical indicators
- **Translations** - Add support for new languages

### Areas of Focus

- **Indian Market Features** - NSE/BSE specific functionality
- **Order Flow Analysis** - Bookmap-style visualization improvements
- **AI/ML Models** - Pattern recognition and sentiment analysis
- **Performance** - Ultra-low latency optimizations
- **Mobile Support** - React Native mobile app
- **Educational Content** - Tutorials and learning materials

### Before You Start

1. **Check existing issues** - Look for related issues or discussions
2. **Create an issue** - Discuss major changes before implementing
3. **Ask questions** - Use GitHub Discussions for questions

## Pull Request Process

1. **Update documentation** - Include relevant documentation updates
2. **Add tests** - Ensure new features have appropriate tests
3. **Update CHANGELOG** - Add entry describing your changes
4. **Ensure CI passes** - All automated tests must pass
5. **Request review** - Ask for review from maintainers

### PR Guidelines

- Use clear, descriptive titles
- Provide detailed description of changes
- Include screenshots for UI changes
- Reference related issues
- Keep PRs focused and reasonably sized

## Coding Standards

### Frontend (TypeScript/React)
- Use TypeScript for all new code
- Follow React best practices and hooks patterns
- Use ESLint and Prettier configurations
- Write meaningful component and variable names
- Document complex logic with comments

### Backend (Python)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Write docstrings for all public functions/classes
- Use async/await for I/O operations
- Follow FastAPI best practices

### C++ (Tick Engine)
- Follow Google C++ Style Guide
- Use smart pointers for memory management
- Write unit tests for critical functionality
- Document performance-critical sections
- Use const-correctness

### VedaScript
- Keep syntax simple and trader-friendly
- Document all built-in functions
- Provide clear error messages
- Include usage examples

## Testing

### Running Tests
Frontend tests
cd frontend && npm test

Backend tests
cd backend && pytest

C++ tests
cd tick_engine && make test

E2E tests
npm run test:e2e

text

### Test Guidelines
- Write tests for new features
- Maintain or improve test coverage
- Include both positive and negative test cases
- Mock external dependencies
- Test edge cases and error conditions

## Documentation

### Documentation Types
- **Code comments** - Explain complex logic
- **API documentation** - Document all endpoints
- **User guides** - Step-by-step tutorials
- **Developer docs** - Setup and architecture
- **README updates** - Keep project info current

### Documentation Standards
- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date
- Write for different skill levels

## Commit Message Convention

Use conventional commit messages:
type(scope): description

feat(charts): add support for Renko charts
fix(orderbook): resolve WebSocket connection issue
docs(readme): update installation instructions
style(ui): improve dark theme colors
test(api): add integration tests for orders
perf(engine): optimize tick processing performance

text

### Commit Types
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code style changes
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `perf` - Performance improvements
- `chore` - Maintenance tasks

## Release Process

1. Create release branch: `release/v1.x.x`
2. Update version numbers
3. Update CHANGELOG.md
4. Create pull request
5. After merge, create GitHub release
6. Deploy to production

## Community

- **Discord**: [Join our server](https://discord.gg/arthachitra)
- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs and request features
- **Email**: contact@arthachitra.com

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes for significant contributions
- Community showcases

## Getting Help

If you need help:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/yourusername/arthachitra/issues)
3. Ask in [GitHub Discussions](https://github.com/yourusername/arthachitra/discussions)
4. Join our [Discord server](https://discord.gg/arthachitra)

Thank you for contributing to Arthachitra! Your contributions help make trading technology more accessible and powerful for everyone. 🚀

---

*"Together, we're building the future of trading technology"* - Arthachitra Team
