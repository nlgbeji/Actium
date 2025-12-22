# Configuration Module

The `config` module manages LLM configuration and global settings for Actium.

## Overview

The configuration module handles:
- **LLM Interface Creation**: Creates LLM interfaces from model identifiers and `provider.json`
- **Global Configuration**: Manages global settings (currently minimal, as each agent has its own config)

## Components

### LLM Interface Creation

The `_create_llm_interface` function creates LLM interfaces from model identifiers.

#### Function

```python
def _create_llm_interface(
    model: str,
    provider_config_path: str = "provider.json"
) -> LLM_Interface
```

#### Parameters

- **`model`** (str): Model identifier in format `"provider/model-name"` or just `"model-name"` (defaults to `"openai"` provider)
- **`provider_config_path`** (str): Path to `provider.json` configuration file

#### Returns

- **`LLM_Interface`**: SimpleLLMFunc LLM interface instance

#### Model Identifier Format

- **Full Format**: `"provider/model-name"` (e.g., `"openai/gpt-3.5-turbo"`)
- **Short Format**: `"model-name"` (defaults to `"openai"` provider, e.g., `"gpt-3.5-turbo"`)

#### Example Usage

```python
from actium.config import _create_llm_interface

# Full format
llm = _create_llm_interface("openai/gpt-3.5-turbo", "provider.json")

# Short format (defaults to openai)
llm = _create_llm_interface("gpt-4", "provider.json")
```

#### Error Handling

- **`FileNotFoundError`**: If `provider.json` doesn't exist
- **`ValueError`**: If model not found in configuration or configuration format is invalid

### Provider Configuration

The module loads LLM configurations from `provider.json` using SimpleLLMFunc's `OpenAICompatible.load_from_json_file`.

#### Configuration Format

```json
{
  "openai": [
    {
      "model_name": "gpt-3.5-turbo",
      "api_keys": ["sk-your-api-key-here"],
      "base_url": "https://api.openai.com/v1",
      "max_retries": 5,
      "retry_delay": 1.0,
      "rate_limit_capacity": 20,
      "rate_limit_refill_rate": 3.0
    }
  ],
  "anthropic": [
    {
      "model_name": "claude-3-opus",
      "api_keys": ["sk-ant-your-key"],
      "base_url": "https://api.anthropic.com/v1"
    }
  ]
}
```

#### Configuration Path Resolution

1. **Environment Variable**: `SIMPLELLMFUNC_PROVIDER_CONFIG` (if set)
2. **Parameter**: `provider_config_path` parameter (if provided)
3. **Default**: `"provider.json"` in current directory

### Global Configuration (Legacy)

The module includes global configuration management, though it's primarily used for backward compatibility. Each agent now has its own configuration.

#### Functions

##### `set_global_config(config: GlobalConfig) -> None`

Sets the global configuration instance.

```python
from actium.config import set_global_config, GlobalConfig

config = GlobalConfig(
    sandbox_dir="./sandbox",
    skills_dir="./skills"
)
set_global_config(config)
```

##### `get_global_config() -> GlobalConfig`

Gets the global configuration instance, initializing from environment variables if not set.

```python
from actium.config import get_global_config

config = get_global_config()
# Returns GlobalConfig or raises ValueError
```

#### Environment Variables (Backward Compatibility)

- **`ACTIUM_SANDBOX_DIR`**: Sandbox directory path
- **`ACTIUM_SKILLS_DIR`**: Skills directory path

## Type Definitions

### GlobalConfig

Pydantic model for global configuration:

```python
class GlobalConfig(BaseModel):
    """Global configuration (using Pydantic)"""
    sandbox_dir: str
    skills_dir: str
    
    @field_validator('sandbox_dir', 'skills_dir', mode='before')
    @classmethod
    def validate_and_resolve_path(cls, v: str) -> str:
        """Validate and resolve path to absolute path"""
        if not v:
            raise ValueError("Path cannot be empty")
        return str(Path(v).resolve())
    
    model_config = ConfigDict(
        frozen=True,  # Immutable config
        validate_assignment=True,  # Validate on assignment
    )
```

**Features**:
- **Path Validation**: Automatically validates and resolves paths
- **Immutable**: Frozen model prevents accidental modification
- **Type Safety**: Uses Pydantic for type validation

### RuntimeConfig (Legacy)

Dataclass for runtime configuration (primarily for backward compatibility):

```python
@dataclass
class RuntimeConfig:
    """Runtime configuration (simplified, reads paths from global config)"""
    model: Union[str, LLM_Interface]
    max_steps: int = 20
    timeout: int = 300
    system_prompt: str = "You are a CodeAct agent."
    provider_config_path: str = "provider.json"
    llm_interface: Optional[LLM_Interface] = field(default_factory=lambda: None)
    
    @property
    def sandbox_dir(self) -> str:
        """Read sandbox_dir from global config"""
        from actium.config import get_global_config
        return get_global_config().sandbox_dir
    
    @property
    def skills_dir(self) -> str:
        """Read skills_dir from global config"""
        from actium.config import get_global_config
        return get_global_config().skills_dir
```

## Usage in Agents

The agent decorator uses configuration functions internally:

```python
# In agent decorator
provider_path = provider_config_path or "provider.json"
llm_interface = _create_llm_interface(model, provider_path)
```

## Best Practices

1. **Provider Configuration**: Use `provider.json` for all LLM API keys (not environment variables)
2. **Model Identifiers**: Use full format `"provider/model-name"` for clarity
3. **Path Resolution**: Let the module handle path resolution automatically
4. **Error Handling**: Handle `FileNotFoundError` and `ValueError` when creating LLM interfaces

## Configuration File Example

See `provider.json.example` for a complete example configuration file.

## See Also

- [Agent Module](./agent.md): How configuration is used in agents
- SimpleLLMFunc Documentation: For detailed `provider.json` format and LLM interface usage

