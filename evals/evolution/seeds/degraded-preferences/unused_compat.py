"""Obsolete internal adapter; removal is explicitly authorized by the fixture owner."""
from cli_store import load

def read_old_value():
    return load()
