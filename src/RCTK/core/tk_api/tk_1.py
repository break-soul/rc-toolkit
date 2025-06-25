import builtins
import importlib


def tk_100000(key: str, value: object) -> None:
    """Hook buildin"""
    builtins.__dict__[key] = value


def tk_100001(key: str) -> object:
    """Hook buildin"""
    return builtins.__dict__.get(key)


if not builtins.__dict__.get("_tk_core_api_store", False):
    tk_100000("_tk_core_api_store", dict())

_tk_core_api_store: dict


# region import
# class _tk_107830:
#     def __init__(self, **kw):
#         self.__dict__["kw"] = kw

#     def __getattr__(self, name: str):
#         kw = self.__dict__["kw"]
#         n = kw["name"]
#         _py_bf_import = _tk_core_api_store.get("_py_bf_import", None)
#         self = importlib.__import__(**kw)
#         rt = self.__getattribute__(name)
#         return rt

#     def __call__(self):
#         kw = _tk_core_api_store["_tk_api_imp_lazy_store"].get(str(self))
#         self = importlib.__import__(*args, *kw)
#         return self

#     # def __repr__(self):


# def tk_107830(name, globals=None, locals=None, fromlist=list(), level=0):
#     return _tk_107830(
#         name=name, globals=globals, locals=locals, fromlist=fromlist, level=level
#     )


def tk_107831(name, globals=None, locals=None, fromlist=list(), level=0):
    """Fake import not call"""
    try:
        rt = importlib.__import__(
            name=name, globals=globals, locals=locals, fromlist=fromlist, level=level
        )
        return rt
    except ImportError:
        if not _tk_core_api_store.get("_tk_api_imp_ign_error", False):
            raise


def tk_107832():
    _tk_core_api_store["_tk_api_imp_able"] = True
    _tk_core_api_store["_tk_api_imp_ign_error"] = False
    _tk_core_api_store["_tk_api_imp_lazy"] = False
    tk_100000("__import__", tk_107831)


def tk_107833(op_tp: bool):
    _tk_core_api_store["_tk_api_imp_ign_error"] = bool(op_tp)


# def tk_107834(op_tp: bool):
#     _tk_core_api_store["_tk_api_imp_lazy_store"] = dict()
#     _tk_core_api_store["_tk_api_imp_lazy"] = bool(op_tp)
#     tk_100000("lazy_import", _tk_107830)


# endregion
