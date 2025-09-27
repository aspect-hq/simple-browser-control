# Simple Browser Control

A command-line browser automation tool powered by the [Aspect SDK](https://docs.aspect.inc/sdk-reference/python) for intelligent element detection and clicking.

## Overview

This tool provides an interactive command-line interface for controlling a Chrome browser. It uses the Aspect SDK to analyze screenshots and intelligently identify clickable elements based on natural language queries.

## Features

- **Browser Control**: Automated Chrome browser management
- **Intelligent Clicking**: AI-powered element detection using Aspect SDK
- **Mock Mode**: Test the interface without API calls
- **Visual Feedback**: Neon pink dots mark detected click points
- **Flexible Window Sizing**: Configurable browser dimensions
- **Comprehensive Logging**: Both console and file logging

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+**: Download from [python.org](https://python.org)
- **uv**: Fast Python package installer and virtual environment manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Google Chrome**: The browser used for automation

> **Note**: No need to manually create virtual environments! uv automatically handles virtual environment creation and dependency isolation for you.

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd simple-browser-control
   ```

2. **Setup the project**
   ```bash
   make setup
   ```
   This will:
   - Install all Python dependencies
   - Create a `.env` file from the example
   - Setup the development environment

3. **Configure your API key**
   
   Edit the `.env` file and add your Aspect API key:
   ```bash
   ASPECT_API_KEY=your_actual_api_key_here
   ```
   
   To get an API key:
   - Sign up at [Aspect](https://aspect.inc)
   - Go to the API keys tab in your dashboard
   - Generate a new API key

## Usage

### Running the Application

Start the browser control tool:

```bash
make run
```

Or directly with uv:

```bash
uv run main.py
```

### Available Commands

Once the application starts, you'll see an interactive prompt with these commands:

#### `navigate <url>`
Navigate to a webpage.
```
> navigate https://example.com
> navigate google.com
```

#### `locate <query>`
Find and mark elements on the current page using natural language.
```
> locate search button
> locate login form
> locate red buy now button
```

The tool will:
1. Take a screenshot of the current page
2. Analyze it using the Aspect SDK
3. Display neon pink dots at detected locations
4. Prompt you to confirm or cancel the click

#### `resize <width> <height>`
Resize the browser window.
```
> resize 1280 720
> resize 1920 1080
```

#### `exit`
Close the browser and quit the application.

### Mock Mode

For testing without API calls, set `MOCK_MODE=true` in your `.env` file. In mock mode:
- You'll be prompted to enter X,Y coordinates manually
- No actual API calls are made to Aspect
- Good for development and testing

## Configuration

### Environment Variables

Configure the application by editing `.env`:

```bash
# Your Aspect API key (required for real mode)
ASPECT_API_KEY=sk_test_yourapikeyhere

# Enable mock mode (true/false)
MOCK_MODE=false
```

### Window Size

The application will prompt you for initial browser window size on startup. You can also resize during use with the `resize` command.

## Development

### Project Structure

```
simple-browser-control/
├── src/
│   ├── aspect_client.py    # Aspect SDK integration
│   ├── browser.py          # Browser control with Selenium
│   └── logger.py           # Logging configuration
├── main.py                 # Application entry point
├── pyproject.toml          # Python project configuration
├── Makefile               # Development commands
├── .env.example           # Environment variable template
└── README.md              # This file
```

### Development Commands

```bash
# Install dependencies
make install

# Run the application
make run

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Clean generated files
make clean
```

### Adding Dependencies

Add new dependencies to `pyproject.toml` and run:
```bash
uv sync
```

## Troubleshooting

### Common Issues

**ChromeDriver not found**
- The application uses `webdriver-manager` to automatically download ChromeDriver
- Ensure you have Google Chrome installed

**API key issues**
- Verify your `.env` file contains a valid `ASPECT_API_KEY`
- Check the [Aspect documentation](https://docs.aspect.inc/sdk-reference/python) for API key format

**Permission errors**
- On macOS, you may need to allow Chrome to be controlled by automation
- Check System Preferences > Security & Privacy > Privacy > Automation

**Network connectivity**
- Ensure you have internet access for both browser navigation and API calls
- Check firewall settings if API calls fail

### Logs

Application logs are stored in the `logs/` directory with timestamps. Check these files for detailed error information.


## License

MIT License - see LICENSE file for details.

## Support

For issues related to:
- **This tool**: Check the logs and troubleshooting section above
- **Aspect SDK**: Visit [Aspect documentation](https://docs.aspect.inc/sdk-reference/python)
- **Selenium**: Check [Selenium documentation](https://selenium-python.readthedocs.io/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `make lint test`
5. Submit a pull request
