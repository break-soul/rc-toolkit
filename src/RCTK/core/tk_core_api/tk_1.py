

import builtins
import importlib

def tk_100000(key: str, value: object):
    """Hook build"""
    builtins.__dict__[key] = value

def tk_100001(key: str) -> object:
    """Hook build"""
    return builtins.__dict__.get(key)

if not builtins.__dict__.get("_tk_core_api_store",False):
    tk_100000("_tk_core_api_store", dict())

_tk_core_api_store:dict

#region import

def tk_107831(name, globals=None, locals=None, fromlist=list(), level=0):
    """Fake import not call"""
    try:
        return importlib.__import__(name=name,globals=globals,locals=locals,fromlist=fromlist,level=level)
    except ImportError:
        if not _tk_core_api_store.get("_tk_api_imp_ign_error",False): raise
        

def tk_107832():
    _tk_core_api_store["_tk_api_imp_able"] = True
    _tk_core_api_store["_tk_api_imp_ign_error"] = False
    _tk_core_api_store["_tk_api_imp_lazy"] = False
    tk_100000("__import__",tk_107831)

def tk_107833(op_tp: bool):
    _tk_core_api_store["_tk_api_imp_ign_error"] = bool(op_tp)

#endregion
