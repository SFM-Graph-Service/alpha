# This is the __init__.py file for the SFM-Graph-Service core package.
# It initializes the package and makes its modules importable.

__version__ = "1.0.0"

# Import key modules for convenience
from . import sfm_models  # type: ignore
from . import sfm_enums  # type: ignore
from . import sfm_query  # type: ignore
