# Project Dependencies

This document outlines the dependencies used in the pAIssive Income project across different components.

## Python Dependencies

The project uses Python packages defined in both `pyproject.toml` and `requirements.txt`. The core dependencies are managed through these files.

### Core Dependencies

- **FastAPI (>=0.95.0)**: Modern, fast web framework for building APIs
- **Uvicorn (>=0.22.0)**: ASGI server implementation
- **Pydantic (>=2.0.0)**: Data validation using Python type annotations
- **Redis (>=4.5.0)**: In-memory data structure store
- **Flask (>=2.0.1)**: Web framework for specific components
- **HTTPX (>=0.24.0)**: Async HTTP client
- **CrewAI (>=0.21.4)**: AI agent orchestration framework

### Service Dependencies

- **gRPC (>=1.54.0)**: High-performance RPC framework
- **Protocol Buffers**: Interface description language for gRPC

### AI and Machine Learning

- **PyTorch (>=1.10.0)**: Deep learning framework
- **Transformers (>=4.20.0)**: State-of-the-art Natural Language Processing
- **Sentence Transformers (>=2.2.0)**: Text embeddings and similarity
- **NumPy (>=1.24.3)**: Scientific computing
- **scikit-learn (>=1.0.0)**: Machine learning utilities

### Development and Testing

- **pytest (>=7.0.0)**: Testing framework
- **pytest-cov**: Test coverage
- **pytest-mock**: Mocking for tests
- **pytest-asyncio**: Async test support

## Node.js Dependencies

The project uses Node.js packages defined in `package.json` for the frontend components.

### Production Dependencies

- **@mui/material (^7.1.0)**: Material-UI components
- **@mui/icons-material (^7.1.0)**: Material-UI icons
- **React (^19.1.0)**: UI framework
- **React Router (^7.5.3)**: Routing for React
- **Recharts (^2.12.0)**: Charting library

### Development Dependencies

- **Webpack (^5.99.8)**: Module bundler
- **Babel (^7.27.1)**: JavaScript compiler
- **Various loaders and plugins**: For handling different file types and build processes

## Version Management

- Python packages use semantic versioning with minimum version requirements
- Node.js packages use caret (^) versioning for minor version updates
- Dependencies are regularly reviewed and updated for security and performance improvements

## Adding New Dependencies

When adding new dependencies:
1. Update the appropriate file (`requirements.txt`, `pyproject.toml`, or `package.json`)
2. Document the dependency in this file
3. Include the minimum required version
4. Add any necessary configuration or setup instructions

## Security Considerations

- Dependencies are automatically scanned for vulnerabilities
- Updates are managed through automated security checks
- Version constraints help maintain stability while allowing security patches
