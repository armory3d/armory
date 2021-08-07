import importlib
import types

# This gets cleared if this package/the __init__ module is reloaded
_module_cache: dict[str, types.ModuleType] = {}


def reload_module(module: types.ModuleType) -> types.ModuleType:
    """Wrapper around importlib.reload() to make sure no module is
    reloaded twice.

    Make sure to call this function in the same order in which the
    modules are imported to make sure that the reloading respects the
    module dependencies. Otherwise modules could depend on other modules
    that are not yet reloaded.

    If you import classes or functions from a module, make sure to
    re-import them after the module is reloaded.
    """
    mod = _module_cache.get(module.__name__, None)

    if mod is None:
        mod = importlib.reload(module)
        _module_cache[module.__name__] = mod

    return mod
