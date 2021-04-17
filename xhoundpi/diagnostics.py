"""
Diagnostics module
"""

import os
import sys
import re

def env_vars() -> str:
    """
    Serializes the environment variables for
    diagnostics and visualization
    """
    pattern = r"(?!\B'[^']*),(?![^']*'\B)" # find commas not between single quotes
    body = f"{os.linesep}    ".join(
        [p.strip() for p in re.split(pattern, str(dict(os.environ))[1:-1])])
    return f"{{{os.linesep}    {body}{os.linesep}}}"

def describe_environment() -> str:
    """
    Returns a set of properties of the environment
    useful for diagnostics and debugging
    (e.g., the current working directory, env vars, etc)
    """
    nl = os.linesep # pylint: disable=invalid-name
    return (f"'CWD': '{os.getcwd()}'{nl}"
            f"'ENV': {env_vars()}{nl}"
            f"'PYTHONPATH': {sys.path}{nl}")
