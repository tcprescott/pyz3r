# Migration Guide for pyz3r 6.1.0+

## Overview
Version 6.1.0 introduces comprehensive type hints, improved documentation, and enhanced logging throughout the library. **All existing code remains compatible** - no changes are required to your code.

## What's New

### Type Hints
All public APIs now include type hints for better IDE support and type checking:

```python
from pyz3r import ALTTPR
from typing import Dict, Any

# Type hints help your IDE provide better autocomplete
settings: Dict[str, Any] = {
    "glitches": "none",
    "item_placement": "advanced",
    # ...
}

# Return types are now explicit
seed: ALTTPR = await ALTTPR.generate(settings=settings)
```

### Enhanced Logging
The library now uses Python's logging module instead of print statements:

```python
import logging
import pyz3r

# Configure logging to see library activity
logging.basicConfig(
    level=logging.INFO,  # or DEBUG for verbose output
    format='%(name)s - %(levelname)s - %(message)s'
)

# Now you'll see informative logs:
# pyz3r.alttpr - INFO - Generating new ALTTPR game
# pyz3r.alttpr - DEBUG - Settings: {...}
seed = await pyz3r.ALTTPR.generate(settings=settings)
```

Available log levels:
- `DEBUG`: Detailed information for diagnosing issues
- `INFO`: General informational messages about progress
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages for failures

### Improved Documentation
All functions now have comprehensive docstrings:

```python
# Use help() or your IDE's documentation viewer
help(ALTTPR.generate)
# Shows detailed parameter descriptions, return types, and examples
```

### Python Version Support
- **Minimum:** Python 3.8
- **Tested:** Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Dropped:** Python 3.6, 3.7 (end of life)

## Breaking Changes
**None!** All existing code continues to work without modification.

## Optional: Enable Type Checking
If you use mypy or other type checkers, you can now benefit from the library's type hints:

```bash
# Install mypy
pip install mypy

# Check your code
mypy your_script.py
```

The library includes a `py.typed` marker, so type checkers will automatically use the type information.

## Recommended Best Practices

### 1. Configure Logging in Your Application
```python
import logging

# Set up logging early in your application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pyz3r.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Use Type Hints in Your Code
```python
from typing import Optional
from pyz3r import ALTTPR, Rom

async def create_seed(hash_id: Optional[str] = None) -> ALTTPR:
    """Generate or retrieve a seed."""
    if hash_id:
        return await ALTTPR.retrieve(hash_id=hash_id)
    else:
        return await ALTTPR.generate(settings={...})
```

### 3. Handle Exceptions Explicitly
```python
from pyz3r.exceptions import AlttprFailedToGenerate, AlttprFailedToRetrieve

try:
    seed = await ALTTPR.generate(settings=settings)
except AlttprFailedToGenerate as e:
    logger.error(f"Failed to generate seed: {e}")
    # Handle error appropriately
```

## Examples

### Before (still works!)
```python
import asyncio
import pyz3r

async def main():
    seed = await pyz3r.alttpr.create(hash_id='zDvxWLLEMa')
    print(seed.url)
    print(seed.code)

asyncio.run(main())
```

### After (with new features)
```python
import asyncio
import logging
from pyz3r import ALTTPR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main() -> None:
    try:
        # Type hints improve IDE support
        seed: ALTTPR = await ALTTPR.retrieve(hash_id='zDvxWLLEMa')
        
        # Library logs show progress
        logger.info(f"Seed URL: {seed.url}")
        logger.info(f"Seed Code: {' | '.join(seed.code)}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

asyncio.run(main())
```

## Questions or Issues?
- GitHub Issues: https://github.com/tcprescott/pyz3r/issues
- Check the improved docstrings: `help(pyz3r.ALTTPR)`

## Upgrading
```bash
pip install --upgrade pyz3r
```

No code changes required! 🎉
