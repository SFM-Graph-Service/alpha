# This is the __init__.py file for the SFM-Graph-Service core package.
# It provides backward compatibility by importing from the new module structure.

__version__ = "1.0.0"

# Import key modules for backward compatibility
from . import sfm_models # type: ignore - compatibility layer
# Note: sfm_enums and sfm_query have moved to models/ and graph/ respectively
# but are still accessible through the sfm_models compatibility layer
