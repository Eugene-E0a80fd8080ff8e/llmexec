# llmexec

A shebang interpreter that converts natural language requests into executable Python code using Large Language Models (LLMs).

## Overview

`llmexec` allows you to write scripts in plain English that get automatically converted to Python code and executed.

## Installation

1. **Install dependencies**:
   ```bash
   pip install litellm python-dotenv
   ```

2. **Download and install llmexec**:
   ```bash
   curl -o ~/.local/bin/llmexec https://raw.githubusercontent.com/Eugene-E0a80fd8080ff8e/llmexec/main/llmexec
   chmod +x ~/.local/bin/llmexec
   ```

   This will download the script to the user's local bin folder.

3. **Set up API keys**:
   `llmexec` uses environment variables for API keys. You can set them directly in your shell or use a `.env` file.

   **Option A: .env file**
   Create a file named `.env` in your project directory or in your $HOME directory with your API keys:
   ```
   OPENAI_API_KEY="sk-..."
   OPENROUTER_API_KEY="sk-or-..."
   GEMINI_API_KEY="AI..."
   ```
   `llmexec` will automatically load these variables if `python-dotenv` is installed. Please note that dotenv searches for .env files recursively at every parent.

   **Option B: Environment Variables**
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export OPENROUTER_API_KEY="your-openrouter-key"
   export GEMINI_API_KEY="your-google-ai-studio-api-key"
   ```
   For other providers, see LiteLLM documentation: https://docs.litellm.ai/docs/proxy/config_settings

4. You can change the default LLM model inside the script itself.

## Quick Start

### Method 1: Shebang Scripts (Recommended)

Create a file `hello.llm`:
```
#!/usr/bin/env -S llmexec --model "gemini/gemini-2.5-flash"
make a "Hello, World!" program
```

Make it executable and run:
```bash
chmod +x hello.llm
./hello.llm
```

### Method 2: Command Line

```bash
llmexec "print current date and time in yyyy-mm-dd hh:mm:ss format. Make sure it is 24-hours format and has all leading zeros"
```

### Method 3: Evaluation within backticks

```bash
DATEANDTIME=`llmexec "print current date and time in yyyy-mm-dd hh:mm:ss format. Make sure it is 24-hours format and has all leading zeros. make that program output only yyyy-mm-dd hh:mm:ss , no additional text"`
echo "result: $DATEANDTIME"
```

## Examples

### File Operations
```
#!/usr/bin/env -S llmexec
list all files in current directory, show their sizes in human readable format
```

### Image Processing
```
#!/usr/bin/env -S llmexec
resize all JPEG images in current directory to fit within 800x600 pixels.
save resized images with .resized.jpg extension
```

### Data Processing
```
#!/usr/bin/env -S llmexec
read all CSV files in current directory and create a summary report
showing the number of rows and columns in each file
```

### System Information
```
#!/usr/bin/env -S llmexec
show system information: OS, CPU, memory usage, and disk space
```

### Web Scraping
```
#!/usr/bin/env -S llmexec
fetch the latest news headlines from hackernews and save them to a file
```

## Usage

```
llmexec [OPTIONS] SCRIPT_FILE

Options:
  --model MODEL         LLM model to use (default: gemini/gemini-2.5-flash)
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
- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Google**: `gemini-pro`, `gemini-pro-vision`
- **Cohere**: `command-r`, `command-r-plus`

### Local Models
- **Ollama**: `ollama/llama2`, `ollama/codellama`, `ollama/mistral`
- **Together AI**: `together_ai/mistralai/Mixtral-8x7B-Instruct-v01`

### API Keys

`llmexec` automatically picks up API keys from environment variables. You can set them directly or use a `.env` file.

**Environment Variables:**
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

**Using a .env file:**
If you have `python-dotenv` installed (`pip install python-dotenv`), `llmexec` will automatically load environment variables from a `.env` file found in the current working directory or any parent directory. This is a convenient way to manage your API keys without setting them globally.

Example `.env` file:
```
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
GOOGLE_API_KEY="AI..."
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

- 📧 Issues: [GitHub Issues](https://github.com/Eugene-E0a80fd8080ff8e/llmexec/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Eugene-E0a80fd8080ff8e/llmexec/discussions)
- 📚 LiteLLM Docs: [docs.litellm.ai](https://docs.litellm.ai)