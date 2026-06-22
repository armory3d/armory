import importlib
import sys
import types

# This gets cleared if this package/the __init__ module is reloaded
_module_cache: dict[str, types.ModuleType] = {}


def enable_reload(module_name: str):
    """Enable reloading for the next time the module with `module_name`
    is executed.
    """
    mod = sys.modules[module_name]
    setattr(mod, module_name.replace('.', '_') + "_DO_RELOAD_MODULE", True)


def is_reload(module_name: str) -> bool:
    """True if the module  given by `module_name` should reload the
    modules it imports. This is the case if `enable_reload()` was called
    for the module before.
    """
    mod = sys.modules[module_name]
    return hasattr(mod, module_name.replace('.', '_') + "_DO_RELOAD_MODULE")


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
