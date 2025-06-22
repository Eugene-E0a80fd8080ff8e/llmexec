#!/usr/bin/env python3
"""
llmexec - LLM-powered shebang script executor
Converts natural language requests into executable Python code using LLM APIs
"""

import os
import re
import sys
import argparse
import subprocess
import tempfile
import json
import hashlib
import time
from pathlib import Path
from platformdirs import PlatformDirs


try:
    import litellm
except ImportError:
    print("Error: litellm package is required. Install with: pip install litellm", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False


PLATFORMDIRS = PlatformDirs(appname="llmexec", appauthor="Eugene-E0a80fd8080ff8e on github")
local_cache_dir = Path.cwd() / ".llmexec-cache"
if local_cache_dir.is_dir():
    cache_dir = local_cache_dir
else:
    cache_dir = PLATFORMDIRS.user_cache_dir
os.makedirs(cache_dir, exist_ok=True)

# System prompt for code generation
SYSTEM_PROMPT = """You are a code generation assistant that creates Python scripts based on natural language requests. Your task is to convert user requests into complete, executable Python programs.

## Core Requirements

1. **Output Format**: Always respond with a complete Python script that can be executed directly
2. **Imports**: Include all necessary imports at the top of the script
3. **Error Handling**: Add appropriate error handling for file operations, network requests, etc.
4. **Cross-platform**: Write code that works on Windows, macOS, and Linux when possible
5. **Dependencies**: Use only standard library modules when possible. If external libraries are needed, include a comment at the top listing required packages

## Code Structure

```python
#!/usr/bin/env python3
# Required packages: package1, package2 (if any external dependencies)

import os
import sys
# other imports...

def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()
```

## Guidelines

### File Operations
- Always check if files/directories exist before operating on them
- Use `os.path.join()` or `pathlib.Path` for cross-platform path handling
- Handle permissions errors gracefully
- For batch operations, show progress when processing multiple files

### Safety
- Never overwrite files without checking if they exist (unless explicitly requested)
- For destructive operations, consider adding confirmation prompts
- Validate input parameters before processing

### Output
- Provide informative output about what the script is doing
- Use `print()` statements to show progress for long-running operations
- Format output clearly and consistently

### Common Patterns
- **Directory listing**: Use `os.listdir()` or `pathlib.Path.iterdir()`
- **File filtering**: Use `glob.glob()` or list comprehensions with appropriate filters
- **Image processing**: Use PIL/Pillow for image operations
- **Text processing**: Handle encoding properly (UTF-8 by default)
- **Network operations**: Include timeouts and error handling

Remember: Generate complete, ready-to-run Python scripts that accomplish exactly what the user requested. Only output the Python code, no explanations or markdown formatting."""


def get_cache_path(model, prompt):
    """Generate a unique cache file path based on model and prompt."""
    # Create a hash of the model and prompt to use as filename
    # This ensures a unique, yet consistent, filename for each query
    p = re.sub("[. ]","_",prompt)
    p = re.sub("[^-_A-Za-z0-9]","",p)
    p = p[:30]

    m = model[model.rfind("/")+1:]
    m = re.sub("[.]","_",m)
    m = re.sub("[^-_A-Za-z0-9]","",m)

    prompt_hash = hashlib.sha256(f"{model}-{prompt}".encode('utf-8')).hexdigest()
    return Path(cache_dir) / f"{p}.{m}.{prompt_hash[:10]}.json"


def generate_code(model, prompt, cache_ttl=0, no_cache=False, verbose=False):
    """Generate code using LiteLLM with custom caching."""
    cache_file = get_cache_path(model, prompt)

    if not no_cache and cache_file.exists():
        # Check if cache is still valid
        if cache_ttl > 0:
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < cache_ttl:
                if verbose:
                    print(f"Using cached response from {cache_file}", file=sys.stderr)
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)['content']
            else:
                if verbose:
                    print(f"Cache expired for {cache_file}", file=sys.stderr)
                os.remove(cache_file) # Invalidate cache
        else: # cache_ttl == 0 means infinite cache
            if verbose:
                print(f"Using cached response from {cache_file}", file=sys.stderr)
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)['content']

    try:
        # Set temperature low for more consistent code generation
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        generated_content = response.choices[0].message.content.strip()

        # Save to cache
        if not no_cache:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({'model': model, 'prompt': prompt, 'content': generated_content, 'timestamp': time.time()}, f, indent=4, ensure_ascii=False)
            if verbose:
                print(f"Cached response to {cache_file}", file=sys.stderr)

        return generated_content
    except Exception as e:
        raise RuntimeError(f"LLM API error: {e}")


def extract_python_code(response):
    """Extract Python code from LLM response, handling various formats"""
    lines = response.split('\n')
    
    # Look for code block markers
    in_code_block = False
    code_lines = []
    
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                break
            else:
                in_code_block = True
                continue
        
        if in_code_block:
            code_lines.append(line)
        elif line.strip().startswith('#!/usr/bin/env python') or line.strip().startswith('import '):
            # Looks like raw Python code without code blocks
            code_lines = lines
            break
    
    code = '\n'.join(code_lines).strip()
    
    # If no code found, return the entire response (might be raw Python)
    if not code:
        code = response.strip()
    
    return code


def main():
    # Load environment variables from .env file if dotenv is available
    if _DOTENV_AVAILABLE:
        load_dotenv()
    else:
        print("Warning: python-dotenv not installed. Environment variables will not be loaded from .env file.", file=sys.stderr)

    parser = argparse.ArgumentParser(
        description="LLM-powered shebang script executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  llmexec "say hello"
  llmexec --model gpt-4.1 --execute script.llm
  llmexec --model gpt-4.1 --dry-run script.llm
  llmexec --model gemini-2.5-pro script.llm
  echo `llmexec "say hello world!"`

  You can change default model in the script itself. Normally it would be located at ~/.local/bin/llmexec

Environment variables for API keys:
  - OPENAI_API_KEY (for OpenAI models)
  - ANTHROPIC_API_KEY (for Anthropic models)  
  - GOOGLE_API_KEY (for Google models)
  - OPENROUTER_API_KEY (for the models accessible via OpenRouter)
  - See LiteLLM docs for other providers: https://docs.litellm.ai/docs/proxy/config_settings
        """
    )
    
    parser.add_argument("script", help="Script file containing natural language request")
    parser.add_argument("--model", default="gemini/gemini-2.5-flash", help="LLM model to use (default: gemini/gemini-2.5-flash)")
    parser.add_argument("--execute", "-x", action="store_true", help="Execute the generated code immediately")
    parser.add_argument("--output", "-o", help="Save generated Python code to file")
    parser.add_argument("--dry-run", action="store_true", help="Show generated code without executing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--cache-ttl", type=int, default=0, help="Cache time-to-live in seconds (0 for infinite, -1 to disable caching for this call)")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching for this call")
    
    args = parser.parse_args()
    
    # Determine if the script argument is a file or a direct message
    script_path = Path(args.script)
    if script_path.is_file():
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except Exception as e:
            print(f"Error reading script file '{script_path}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # If it's not a file, treat the argument as the content itself
        content = args.script
        if args.verbose:
            print(f"'{args.script}' is not a file. Interpreting as direct message.", file=sys.stderr)
    
    # Skip shebang line if present
    lines = content.split('\n')
    if lines[0].startswith('#!'):
        content = '\n'.join(lines[1:]).strip()
    
    if not content:
        print("Error: Empty script content", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Using model: {args.model}")
        print(f"Request: {content}")
        print("-" * 50)
    
    # Generate code using LLM
    try:
        response = generate_code(
            args.model,
            content,
            cache_ttl=args.cache_ttl,
            no_cache=args.no_cache or args.cache_ttl == -1,
            verbose=args.verbose
        )
        python_code = extract_python_code(response)
        
        if args.verbose:
            print("Generated code:")
            print("-" * 50)
        
        if args.dry_run or args.verbose:
            print(python_code)
            if args.dry_run:
                sys.exit(0)
        
        # Save to output file if specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(python_code)
            if args.verbose:
                print(f"\nCode saved to: {args.output}")
        
        # Execute the code
        if args.execute or not args.output:
            if args.verbose:
                print("\nExecuting generated code:")
                print("-" * 50)
            
            # Create temporary file and execute
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(python_code)
                temp_file = f.name
            
            try:
                # Change to the directory of the original script
                script_dir = os.path.dirname(os.path.abspath(args.script))
                os.chdir(script_dir)
                
                # Execute the generated Python code
                result = subprocess.run([sys.executable, temp_file], 
                                      capture_output=False, 
                                      text=True)
                sys.exit(result.returncode)
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()