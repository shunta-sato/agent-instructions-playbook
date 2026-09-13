# External integrations import this function; absence of local callers does not
# make it dead code. Keep this published boundary while changing internal storage.
from cli_store import load as read_value
