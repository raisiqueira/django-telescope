# Django MCP Server

A Model Context Protocol (MCP) server for Django applications, inspired by [Laravel Boost](https://github.com/laravel/boost). This server exposes Django project information through MCP tools, enabling AI assistants to better understand and interact with Django codebases.

## Features

- = **Project Discovery**: List models, URLs, and management commands
- =� **Database Introspection**: View schema, migrations, and relationships
- � **Configuration Access**: Query Django settings with dot notation
- =� **Log Reading**: Access recent application logs with filtering
- = **Read-Only**: All tools are safe, read-only operations
- � **Fast**: Built on FastMCP for efficient async operations

## Installation

```bash
# Using uv (recommended)
uv pip install django-mcp

# Or with pip
pip install django-mcp
```

## Usage

### Running the Server

The server requires access to your Django project's settings:

```bash
# Set the Django settings module
export DJANGO_SETTINGS_MODULE=myproject.settings
django-mcp

# Or specify settings directly
django-mcp --settings myproject.settings

# Run with SSE transport (default is stdio)
django-mcp --settings myproject.settings --transport sse
```

### Configuration with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "django": {
      "command": "django-mcp",
      "args": ["--settings", "myproject.settings"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

## Available Tools

### 1. `application_info`
Get Django and Python versions, installed apps, middleware, database engine, and debug mode status.

### 2. `get_setting`
Retrieve any Django setting using dot notation (e.g., `DATABASES.default.ENGINE`).

### 3. `list_models`
List all Django models with fields, types, max_length, null/blank status, and relationships.

### 4. `list_urls`
Show all URL patterns with names, patterns, and view handlers (including nested includes).

### 5. `database_schema`
Get complete database schema including tables, columns, types, indexes, and foreign keys.

### 6. `list_migrations`
View all migrations per app with their applied/unapplied status.

### 7. `list_management_commands`
List all available `manage.py` commands with their source apps.

### 8. `read_recent_logs`
Read recent log entries with optional filtering by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Example Usage with AI Assistants

Once configured, you can ask your AI assistant questions like:

- "What models are in this Django project?"
- "Show me all URL patterns"
- "What's the database schema for the users table?"
- "Are there any unapplied migrations?"
- "What's the value of the DEBUG setting?"
- "Show me recent error logs"

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/django-mcp.git
cd django-mcp

# Install dependencies
uv sync --dev
```

### Testing

```bash
# Test the MCP server with the fixture project
uv run python test_server.py

# Run the MCP server with the test project
uv run django-mcp --settings testproject.settings

# Run linter
uv run ruff check .

# Format code
uv run ruff format .
```

The `fixtures/testproject/` directory contains a complete Django application for testing all MCP tools. See `fixtures/README.md` for details.

## Requirements

- Python 3.12+
- Django 4.2+
- FastMCP 2.12.4+

## License

MIT License - see LICENSE file for details.

## Inspiration

This project is inspired by [Laravel Boost](https://github.com/laravel/boost), which provides similar MCP functionality for Laravel applications.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
