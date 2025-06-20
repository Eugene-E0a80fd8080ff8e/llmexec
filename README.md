# llmexec

A shebang interpreter that converts natural language requests into executable Python code using Large Language Models (LLMs).

## Overview

`llmexec` allows you to write "scripts" in plain English that get automatically converted to Python code and executed. It's like having an AI assistant that writes code for you on-the-fly.

## Features

- 🚀 **Shebang Support**: Use as a script interpreter with `#!/usr/bin/env -S llmexec`
- 🤖 **Multiple LLM Providers**: Supports 100+ models via LiteLLM (OpenAI, Anthropic, Google, Ollama, etc.)
- 🛡️ **Safety First**: Generated code includes error handling and safety checks
- 🔧 **Flexible Execution**: Execute immediately, save to file, or preview with dry-run
- 📁 **Context Aware**: Runs in the directory of your script file
- 🎯 **Optimized for Code**: Uses specialized prompts for generating clean, executable Python

## Installation

1. **Install dependencies**:
   ```bash
   pip install litellm
   ```

2. **Download and install llmexec**:
   ```bash
   # Download the script
   curl -o llmexec https://raw.githubusercontent.com/yourusername/llmexec/main/llmexec
   
   # Make it executable
   chmod +x llmexec
   
   # Move to PATH (optional)
   sudo mv llmexec /usr/local/bin/
   ```

3. **Set up API keys**:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export GOOGLE_API_KEY="your-google-key"
   ```

## Quick Start

### Method 1: Shebang Scripts (Recommended)

Create a file `hello.llm`:
```
#!/usr/bin/env -S llmexec --model gpt-4 --execute
print "Hello, World!" and the current date and time
```

Make it executable and run:
```bash
chmod +x hello.llm
./hello.llm
```

### Method 2: Command Line

```bash
# Create a simple script file
echo "list all Python files in current directory with their sizes" > task.llm

# Execute with llmexec
llmexec --model gpt-4 --execute task.llm
```

## Examples

### File Operations
```
#!/usr/bin/env -S llmexec --model gpt-4 --execute
list all files in current directory, show their sizes in human readable format
```

### Image Processing
```
#!/usr/bin/env -S llmexec --model gpt-4 --execute
resize all JPEG images in current directory to fit within 800x600 pixels.
save resized images with .resized.jpg extension
```

### Data Processing
```
#!/usr/bin/env -S llmexec --model claude-3-sonnet-20240229 --execute
read all CSV files in current directory and create a summary report
showing the number of rows and columns in each file
```

### System Information
```
#!/usr/bin/env -S llmexec --model gpt-4 --execute
show system information: OS, CPU, memory usage, and disk space
```

### Web Scraping
```
#!/usr/bin/env -S llmexec --model gpt-4 --execute
fetch the latest news headlines from hackernews and save them to a file
```

## Usage

```
llmexec [OPTIONS] SCRIPT_FILE

Options:
  --model MODEL         LLM model to use (default: gpt-4)
  --execute, -x         Execute the generated code immediately
  --output FILE, -o     Save generated Python code to file
  --dry-run            Show generated code without executing
  --verbose, -v        Verbose output
  --help, -h           Show help message
```

### Examples

```bash
# Execute immediately
llmexec --model gpt-4 --execute myscript.llm

# Preview generated code
llmexec --model gpt-4 --dry-run myscript.llm

# Save generated code to file
llmexec --model claude-3-sonnet-20240229 --output generated.py myscript.llm

# Verbose output
llmexec --model gpt-4 --verbose --execute myscript.llm
```

## Supported Models

Thanks to LiteLLM, `llmexec` supports 100+ models from various providers:

### Cloud Providers
- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, `o1-preview`
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Google**: `gemini-pro`, `gemini-pro-vision`
- **Cohere**: `command-r`, `command-r-plus`

### Local Models
- **Ollama**: `ollama/llama2`, `ollama/codellama`, `ollama/mistral`
- **Together AI**: `together_ai/mistralai/Mixtral-8x7B-Instruct-v01`

### API Keys

Set the appropriate environment variable for your chosen provider:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="AI..."

# For other providers, see LiteLLM documentation
```

## How It Works

1. **Parse Request**: Reads your natural language request from the script file
2. **Generate Code**: Sends request to LLM with specialized system prompt for code generation
3. **Extract Code**: Intelligently extracts Python code from LLM response
4. **Execute**: Runs the generated code in your script's directory context

## Generated Code Quality

The system prompt ensures generated code follows best practices:

- ✅ Complete, executable scripts with proper imports
- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Error handling and safety checks
- ✅ Progress reporting for long operations
- ✅ Uses standard library when possible
- ✅ Clear, readable code with comments

## Tips for Better Results

### Be Specific
```
❌ "process images"
✅ "resize all JPEG images to 800x600 and save with _resized suffix"
```

### Specify Output Format
```
❌ "analyze this data"
✅ "read data.csv and create a bar chart showing sales by month"
```

### Include Safety Requirements
```
✅ "backup all files before modifying them"
✅ "ask for confirmation before deleting files"
```

## Safety Considerations

- Generated code includes error handling and validation
- File operations check for existence before proceeding
- Destructive operations may include confirmation prompts
- Code runs in script's directory, not system directories
- Review generated code with `--dry-run` before execution

## Troubleshooting

### Common Issues

**ImportError: No module named 'litellm'**
```bash
pip install litellm
```

**API Key Errors**
```bash
# Check your API key is set
echo $OPENAI_API_KEY

# Try a different model
llmexec --model gpt-3.5-turbo --execute script.llm
```

**Permission Denied**
```bash
chmod +x llmexec
chmod +x your-script.llm
```

**Generated Code Fails**
- Use `--dry-run` to review code first
- Try a different model (e.g., `claude-3-sonnet-20240229`)
- Make your request more specific
- Check if required packages are installed

## Advanced Usage

### Custom Model Configurations

```bash
# Use local Ollama model
llmexec --model ollama/codellama --execute script.llm

# Use Together AI model
llmexec --model together_ai/mistralai/Mixtral-8x7B-Instruct-v01 --execute script.llm
```

### Batch Processing

Create multiple `.llm` files and process them:

```bash
#!/bin/bash
for script in *.llm; do
    echo "Processing $script..."
    llmexec --model gpt-4 --execute "$script"
done
```

### Integration with Other Tools

```bash
# Use with cron for scheduled tasks
0 9 * * * /usr/local/bin/llmexec --model gpt-4 --execute /path/to/daily-report.llm

# Pipe output to other commands
llmexec --model gpt-4 --execute data-export.llm | gzip > backup.gz
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API interface
- [aider](https://github.com/paul-gauthier/aider) - AI pair programming
- [gpt-engineer](https://github.com/AntonOsika/gpt-engineer) - AI code generation

## Support

- 📧 Issues: [GitHub Issues](https://github.com/yourusername/llmexec/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/llmexec/discussions)
- 📚 LiteLLM Docs: [docs.litellm.ai](https://docs.litellm.ai)