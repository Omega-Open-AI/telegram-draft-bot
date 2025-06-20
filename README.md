# Telegram AI Image Generation Bot

A sophisticated Telegram bot that generates high-quality images from text descriptions using state-of-the-art AI models. The bot leverages multiple Hugging Face models including FLUX, Stable Diffusion, and specialized prompt enhancement systems to create stunning visual content.

## Repository Information

**GitHub Repository:** https://github.com/Omega-Open-AI/telegram-draft-bot.git

**Current Version:** 1.0.0

**License:** MIT

## Features and Capabilities

The bot provides comprehensive image generation capabilities with intelligent model selection, prompt enhancement, image analysis, and user preference management. Users can generate images through simple text commands, enhance their prompts using AI assistance, analyze uploaded images for detailed descriptions, and customize their preferred generation models.

The system includes robust rate limiting to ensure fair usage, automatic model optimization based on prompt characteristics, image processing and optimization for Telegram delivery, and comprehensive error handling with detailed logging. Redis-based caching provides efficient user preference storage and rate limiting functionality.

## Supported AI Models

### Text-to-Image Generation Models

The bot supports multiple premium and free models for different use cases. FLUX.1-pro delivers premium quality image generation with superior detail and accuracy, while FLUX.1-dev provides development-grade features with high quality output. FLUX.1-schnell offers fast generation with excellent quality balance, and FLUX.1-schnell-Free provides free tier access with good quality results.

Additional models include Kwai-Kolors for advanced artistic rendering with vibrant color reproduction, Stable Diffusion 3.5 for latest text understanding capabilities, classic Stable Diffusion v1.5 for reliable fast generation, and SDXL for high-resolution detailed image output.

### Text Processing and Enhancement

The system incorporates specialized text processing models for prompt optimization. The Flux Prompt Enhancer optimizes prompts specifically for better image generation results, while the Text-to-Image Prompt Generator creates detailed prompts from simple descriptions.

### Image Analysis Capabilities

Advanced image analysis functionality enables users to upload images for detailed description generation. The BLIP Image Captioning model provides comprehensive image analysis and description generation, supporting reverse engineering of prompts from existing images.

## Prerequisites and Dependencies

### System Requirements

The bot requires Python 3.8 or higher for optimal compatibility with all dependencies. Redis server installation is necessary for caching and rate limiting functionality. Sufficient system memory is recommended, with at least 1GB RAM for stable operation under moderate load.

### API Credentials Required

Users must obtain a Telegram Bot Token from BotFather on Telegram and a Hugging Face API key with read permissions for model access. Optional Sentry DSN can be configured for enhanced error monitoring and debugging capabilities.

## Installation Instructions

### Local Development Setup

Begin by cloning the repository to your local development environment:

```bash
git clone https://github.com/Omega-Open-AI/telegram-draft-bot.git
cd telegram-draft-bot
```

Create and activate a Python virtual environment to isolate dependencies:

```bash
python -m venv telegram_bot_env
```

Activate the virtual environment using the appropriate command for your operating system:

**Windows:**
```cmd
telegram_bot_env\Scripts\activate
```

**Linux/macOS:**
```bash
source telegram_bot_env/bin/activate
```

Install all required dependencies from the requirements file:

```bash
pip install -r requirements.txt
```

### Windows-Specific Installation

Windows users should ensure Python 3.8+ is properly installed and added to the system PATH. Download Python from the official website and select the option to add Python to PATH during installation. Windows Subsystem for Linux (WSL) provides an alternative environment that may offer better compatibility with certain dependencies.

For Redis installation on Windows, download Redis for Windows from the Microsoft Archive or use the Windows Subsystem for Linux. Alternatively, Docker Desktop can provide Redis through containerization:

```cmd
docker run -d -p 6379:6379 redis:alpine
```

Configure environment variables through System Properties > Advanced > Environment Variables, or create a .env file in the project directory containing the required configuration values.

### Termux Android Installation

Termux provides a Linux environment on Android devices, enabling bot deployment directly on mobile hardware. Begin by installing Termux from F-Droid or Google Play Store, then update the package repository:

```bash
pkg update && pkg upgrade
```

Install Python and required system packages:

```bash
pkg install python git redis
```

Install build tools and dependencies required for Python package compilation:

```bash
pkg install clang make libjpeg-turbo-dev zlib-dev
```

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Omega-Open-AI/telegram-draft-bot.git
cd telegram-draft-bot
```

Install Python dependencies with specific flags for Termux compatibility:

```bash
pip install -r requirements.txt --no-build-isolation
```

Start Redis server in a separate terminal session:

```bash
redis-server
```

## Configuration Setup

### Environment Variables Configuration

Create a `.env` file in the project root directory with the following configuration:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
```

### Obtaining Required Credentials

**Telegram Bot Token:** Open Telegram and search for @BotFather. Send the command `/newbot` and follow the prompts to create your bot. BotFather will provide a unique token that must be kept secure and used in your configuration.

**Hugging Face API Key:** Register an account at huggingface.co and navigate to your profile settings. Generate an API token with read permissions, which will enable access to the AI models used by the bot.

### Redis Configuration

Start Redis server before running the bot. The default configuration connects to localhost on port 6379. For production deployments, configure Redis with appropriate security settings and persistent storage:

```bash
redis-server --appendonly yes --requirepass your_secure_password
```

## Running the Bot

### Local Development Execution

Ensure Redis server is running and environment variables are properly configured. Start the bot using the following command:

```bash
python telegram_bot_complete.py
```

The bot will begin polling for messages and display startup information in the console. Monitor the logs for successful initialization and any potential configuration issues.

### Production Deployment Considerations

For production environments, implement proper logging configuration, error monitoring integration, and automated restart capabilities. Consider using process managers such as PM2 or systemd for service management:

```bash
# Using PM2
pm2 start telegram_bot_complete.py --name telegram-image-bot --interpreter python3

# Using systemd (create service file)
sudo systemctl start telegram-image-bot
sudo systemctl enable telegram-image-bot
```

## Cloud Hosting Deployment

### Railway Platform Deployment

Railway provides seamless deployment with integrated Redis support and automatic scaling capabilities. Connect your GitHub repository to Railway and configure the following environment variables in the Railway dashboard:

- TELEGRAM_BOT_TOKEN
- HUGGINGFACE_API_KEY  
- REDIS_URL (automatically provided by Railway Redis service)

The platform automatically detects Python applications and installs dependencies from requirements.txt. Deployment occurs automatically upon code commits to the connected repository.

### Render Platform Deployment

Render offers robust free tier hosting with automatic SSL certificates and deployment automation. Create a new Web Service in the Render dashboard and connect your GitHub repository. Configure build and start commands in the service settings:

**Build Command:** `pip install -r requirements.txt`
**Start Command:** `python telegram_bot_complete.py`

Add a separate Redis service within your Render account and configure the connection URL in your web service environment variables.

### Alternative Cloud Providers

Google Cloud Platform App Engine provides serverless deployment with automatic scaling and integrated logging. Configure deployment using the app.yaml file for GAE standard environment.

Heroku offers straightforward deployment through Git integration, though the free tier has been discontinued. Consider Heroku alternatives such as Fly.io or DigitalOcean App Platform for similar deployment experiences.

## Bot Usage and Commands

### Available Commands

The bot responds to several commands that provide different functionality:

`/start` - Display welcome message and quick start guide
`/help` - Show detailed usage instructions and prompt writing tips
`/generate <prompt>` - Generate image from specified text description
`/models` - List all available AI models with descriptions and capabilities
`/setmodel <model_name>` - Configure preferred model for image generation
`/enhance <prompt>` - Improve prompt using AI enhancement algorithms

### Text Message Handling

Send any text message to the bot to generate an image using the content as a prompt. The bot automatically selects the optimal model based on prompt characteristics and user preferences. Enhanced prompts are generated automatically to improve output quality.

### Image Analysis Feature

Upload any image to the bot to receive detailed analysis and description. The generated description can serve as a prompt for creating similar images, enabling reverse engineering of visual concepts.

## Rate Limiting and Usage Policies

The bot implements rate limiting to ensure fair usage across all users. Each user can generate up to 10 images per hour, with the limit resetting automatically. Rate limiting information is stored in Redis with automatic expiration.

Prompts are automatically sanitized to prevent generation of inappropriate content. The system blocks requests containing harmful keywords and maintains content policy compliance.

## Troubleshooting and Support

### Common Issues and Solutions

**ModuleNotFoundError:** Ensure all dependencies are installed correctly using `pip install -r requirements.txt`. Verify that the virtual environment is activated before installation.

**Redis Connection Errors:** Confirm Redis server is running and accessible at the configured URL. Check firewall settings and network connectivity for remote Redis instances.

**API Authentication Failures:** Verify that environment variables are properly set and API credentials are valid. Test credentials independently before running the bot.

**Image Generation Timeouts:** Hugging Face models may require loading time on first use. The bot automatically retries after model loading completion. Monitor API status for service availability.

### Logging and Monitoring

The bot provides comprehensive logging for debugging and monitoring purposes. Log levels can be adjusted in the configuration for development versus production environments. Integration with Sentry provides real-time error monitoring and performance tracking.

### Performance Optimization

For high-traffic deployments, consider implementing connection pooling for Redis and HTTP clients. Monitor memory usage during image processing operations and implement appropriate garbage collection strategies.

## Contributing and Development

### Code Standards and Guidelines

The project follows Python PEP 8 style guidelines with Black code formatting. Type hints are used throughout the codebase for improved maintainability and IDE support. Comprehensive error handling ensures graceful degradation under various failure scenarios.

### Testing Framework

The project includes pytest configuration for unit and integration testing. Test coverage focuses on core functionality including image generation, command handling, and error scenarios.

### Development Workflow

Fork the repository and create feature branches for new functionality. Submit pull requests with detailed descriptions of changes and appropriate test coverage. Code review process ensures quality and consistency across contributions.

## Security Considerations

### API Key Management

Store API keys and sensitive credentials as environment variables rather than hardcoding in source files. Use platform-specific secret management services for production deployments. Implement key rotation procedures for enhanced security.

### Content Filtering

The bot includes automatic content filtering to prevent generation of inappropriate images. Harmful keywords are blocked at the prompt sanitization stage. Additional filtering can be implemented based on specific requirements.

### User Privacy

User interactions are logged for debugging purposes but personal information is not permanently stored. Rate limiting data expires automatically and user preferences can be cleared upon request.

## License and Legal Information

This project is released under the MIT License, permitting commercial and personal use with attribution. Users remain responsible for compliance with Telegram Terms of Service and Hugging Face API usage policies.

The bot leverages third-party AI models subject to their respective licensing terms. Users should review model-specific usage rights and restrictions before commercial deployment.

## Support and Contact Information

For technical support and bug reports, create issues in the GitHub repository with detailed descriptions and reproduction steps. Feature requests and enhancement suggestions are welcome through the repository issue system.

Community discussions and usage questions can be addressed through GitHub Discussions or relevant Telegram development groups.
