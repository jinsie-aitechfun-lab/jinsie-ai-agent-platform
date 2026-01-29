"""
Thin wrapper to expose stable imports for system repos.

DO NOT implement business logic here.
"""

# TODO: replace the import path below with the real runner entry in your platform.
# For now, we only provide a placeholder to make the package importable.

def workflow_runner(*args, **kwargs):
    raise NotImplementedError("workflow_runner is not wired yet. Please map to platform runner entry.")
