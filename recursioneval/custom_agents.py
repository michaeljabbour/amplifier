"""Extends terminal-bench's AbstractInstalledAgent to create a custom agent that uses amplifier."""

import os
import shlex
import tempfile
from pathlib import Path

from terminal_bench.agents.agent_name import AgentName
from terminal_bench.agents.installed_agents.abstract_installed_agent import AbstractInstalledAgent
from terminal_bench.terminal.models import TerminalCommand


class CustomAmplifierAgent(AbstractInstalledAgent):
    @staticmethod
    def name() -> str:
        return "amplifier"

    def _create_env_setup_file(self) -> str:
        """Override to use double quotes for proper variable expansion."""
        lines = []
        for key, value in self._env.items():
            # Use double quotes and escape any special characters
            escaped_value = value.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
            lines.append(f'export {key}="{escaped_value}"')
        return "\n".join(lines)

    ALLOWED_TOOLS = [
        "Bash",
        "mcp__deepwiki",
        "WebFetch",
        "TodoWrite",
        "Edit",
        "Write",
        "Read",
        "Glob",
        "Grep",
        "LS",
        "WebFetch",
        "NotebookEdit",
        "NotebookRead",
        "TodoRead",
        "Agent",
        "WebSearch",
    ]

    def __init__(self, model_name: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_name = model_name
        self._version = kwargs.get("version", "latest")

    @property
    def _env(self) -> dict[str, str]:
        env = {
            "ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"],
            "FORCE_AUTO_BACKGROUND_TASKS": "1",
            "ENABLE_BACKGROUND_TASKS": "1",
            "BASH_DEFAULT_TIMEOUT_MS": "300000",  # 5 minutes
            "BASH_MAX_TIMEOUT_MS": "600000",  # 10 minutes
        }
        if self._model_name:
            env["ANTHROPIC_MODEL"] = self._model_name.removeprefix("anthropic/")
        elif "ANTHROPIC_MODEL" in os.environ:
            env["ANTHROPIC_MODEL"] = os.environ["ANTHROPIC_MODEL"]
        return env

    @property
    def _install_agent_script_path(self) -> Path:
        """Create the installation script for claude-code."""
        script_content = """#!/bin/bash

apt-get update
apt-get install -y curl git make build-essential

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Install nvm and Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
source "$HOME/.nvm/nvm.sh"

nvm install 22
npm -v

# Install pnpm
curl -fsSL https://get.pnpm.io/install.sh | sh -
export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"

# Clone amplifier to temporary location
git clone https://github.com/microsoft/amplifier.git /tmp/amplifier

# Copy all amplifier files into current working directory
cp -r -n /tmp/amplifier/. .

# Install Python dependencies for amplifier
uv pip install pydantic rich typer colorama typing-extensions

# Create necessary directories for claude-code
mkdir -p ~/.claude
mkdir -p .claude
mkdir -p .data

# Create claude settings.json in BOTH home and local directories
cat > ~/.claude/settings.json << EOF
{
  "env": {
    "ANTHROPIC_API_KEY": "$ANTHROPIC_API_KEY",
    "BASH_DEFAULT_TIMEOUT_MS": "300000",
    "BASH_MAX_TIMEOUT_MS": "600000",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000"
  },
  "model": "opus",
  "permissions": {
    "allowedTools": ["Bash", "mcp__deepwiki", "WebFetch", "TodoWrite", "Edit", "Write", "Read", "Glob", "Grep", "LS", "WebFetch", "NotebookEdit", "NotebookRead", "TodoRead", "Agent", "WebSearch"]
  }
}
EOF

# Also create local settings
cp ~/.claude/settings.json .claude/settings.json

# Also export API key for environment (fallback)
echo "export ANTHROPIC_API_KEY=\"$ANTHROPIC_API_KEY\"" >> ~/.bashrc
echo "export ANTHROPIC_API_KEY=\"$ANTHROPIC_API_KEY\"" > ~/.claude_api_key
chmod 600 ~/.claude_api_key
export ANTHROPIC_API_KEY

make install

# Create wrapper script for claude that ensures environment is set
cat > /usr/local/bin/claude-wrapper << 'WRAPPER_EOF'
#!/bin/bash
# Source API key if not already set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    source ~/.claude_api_key 2>/dev/null || source /installed-agent/setup-env.sh 2>/dev/null
fi
# Ensure .data directory exists
mkdir -p .data 2>/dev/null
# CRITICAL: Export the API key so claude can see it
export ANTHROPIC_API_KEY
exec claude "$@"
WRAPPER_EOF
chmod +x /usr/local/bin/claude-wrapper

# Verify claude-code can authenticate
echo "Testing claude installation..."
claude --version || echo "Claude installation may have issues"
echo "API key is set in config: $(grep ANTHROPIC_API_KEY ~/.claude/settings.json | head -1)"

# Modify Claude settings to use acceptEdits mode instead of bypassPermissions
if [ -f .claude/settings.json ]; then
    sed -i 's/"defaultMode": "bypassPermissions"/"defaultMode": "acceptEdits"/g' .claude/settings.json
fi"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as temp_file:
            temp_file.write(script_content)
            temp_path = Path(temp_file.name)

        temp_path.chmod(0o755)
        return temp_path

    def _run_agent_commands(self, instruction: str) -> list[TerminalCommand]:
        instruction = f"/ultrathink-task {instruction}"
        escaped_instruction = shlex.quote(instruction)
        return [
            TerminalCommand(
                command=f"claude-wrapper --model opus --verbose --output-format stream-json "
                f"-p {escaped_instruction} --allowedTools "
                f"{' '.join(self.ALLOWED_TOOLS)}",
                min_timeout_sec=0.0,
                max_timeout_sec=float("inf"),
                block=True,
                append_enter=True,
            ),
        ]


class ClaudeCodeAgent(AbstractInstalledAgent):
    @staticmethod
    def name() -> str:
        return AgentName.CLAUDE_CODE.value

    def _create_env_setup_file(self) -> str:
        """Override to use double quotes for proper variable expansion."""
        lines = []
        for key, value in self._env.items():
            # Use double quotes and escape any special characters
            escaped_value = value.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
            lines.append(f'export {key}="{escaped_value}"')
        return "\n".join(lines)

    ALLOWED_TOOLS = [
        "Bash",
        "Edit",
        "Write",
        "Read",
        "Glob",
        "Grep",
        "LS",
        "WebFetch",
        "NotebookEdit",
        "NotebookRead",
        "TodoRead",
        "TodoWrite",
        "Agent",
        "WebSearch",
    ]

    def __init__(self, model_name: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model_name = model_name
        self._version = kwargs.get("version", "latest")

    @property
    def _env(self) -> dict[str, str]:
        env = {
            "ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"],
            "FORCE_AUTO_BACKGROUND_TASKS": "1",
            "ENABLE_BACKGROUND_TASKS": "1",
            "BASH_DEFAULT_TIMEOUT_MS": "300000",  # 5 minutes
            "BASH_MAX_TIMEOUT_MS": "600000",  # 10 minutes
        }
        if self._model_name:
            env["ANTHROPIC_MODEL"] = self._model_name.removeprefix("anthropic/")
        elif "ANTHROPIC_MODEL" in os.environ:
            env["ANTHROPIC_MODEL"] = os.environ["ANTHROPIC_MODEL"]
        return env

    @property
    def _install_agent_script_path(self) -> Path:
        """Create the installation script for claude-code."""
        script_content = """#!/bin/bash

apt-get update
apt-get install -y curl

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash

source "$HOME/.nvm/nvm.sh"

nvm install 22
npm -v

npm install -g @anthropic-ai/claude-code

# Create necessary directories for claude-code
mkdir -p ~/.claude
mkdir -p .claude
mkdir -p .data

# Create claude settings.json in BOTH home and local directories
cat > ~/.claude/settings.json << EOF
{
  "env": {
    "ANTHROPIC_API_KEY": "$ANTHROPIC_API_KEY",
    "BASH_DEFAULT_TIMEOUT_MS": "300000",
    "BASH_MAX_TIMEOUT_MS": "600000",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000"
  },
  "model": "opus",
  "permissions": {
    "allowedTools": ["Bash", "Edit", "Write", "Read", "Glob", "Grep", "LS", "WebFetch", "NotebookEdit", "NotebookRead", "TodoRead", "TodoWrite", "Agent", "WebSearch"]
  }
}
EOF

# Also create local settings
cp ~/.claude/settings.json .claude/settings.json

# Also export API key for environment (fallback)
echo "export ANTHROPIC_API_KEY=\"$ANTHROPIC_API_KEY\"" >> ~/.bashrc
echo "export ANTHROPIC_API_KEY=\"$ANTHROPIC_API_KEY\"" > ~/.claude_api_key
chmod 600 ~/.claude_api_key
export ANTHROPIC_API_KEY

# Create wrapper script for claude that ensures environment is set
cat > /usr/local/bin/claude-wrapper << 'WRAPPER_EOF'
#!/bin/bash
# Source API key if not already set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    source ~/.claude_api_key 2>/dev/null || source /installed-agent/setup-env.sh 2>/dev/null
fi
# Ensure .data directory exists
mkdir -p .data 2>/dev/null
# CRITICAL: Export the API key so claude can see it
export ANTHROPIC_API_KEY
# Try to find claude in various locations
if [ -x /root/.nvm/versions/node/v22.21.1/bin/claude ]; then
    exec /root/.nvm/versions/node/v22.21.1/bin/claude "$@"
elif which claude >/dev/null 2>&1; then
    exec claude "$@"
else
    echo "Error: claude command not found" >&2
    exit 1
fi
WRAPPER_EOF
chmod +x /usr/local/bin/claude-wrapper

# Verify claude-code can authenticate
echo "Testing claude installation..."
claude --version || echo "Claude installation may have issues"
echo "API key is set in config: $(grep ANTHROPIC_API_KEY ~/.claude/settings.json | head -1)" """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as temp_file:
            temp_file.write(script_content)
            temp_path = Path(temp_file.name)

        temp_path.chmod(0o755)
        return temp_path

    def _run_agent_commands(self, instruction: str) -> list[TerminalCommand]:
        escaped_instruction = shlex.quote(instruction)
        return [
            TerminalCommand(
                command=f"claude-wrapper --model opus --verbose --output-format stream-json "
                f"-p {escaped_instruction} --allowedTools "
                f"{' '.join(self.ALLOWED_TOOLS)}",
                min_timeout_sec=0.0,
                max_timeout_sec=float("inf"),
                block=True,
                append_enter=True,
            ),
        ]
