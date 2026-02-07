from logging import config, Logger, getLogger
from typing import Any
from collections.abc import Mapping
from .lazy_do import lazy_do
from ..io_ import file


@lazy_do
def get_log(logger_name: str | None = None) -> Logger:

    if logger_name is None:
        logger_name = "Main"
    return getLogger(logger_name)


log_print = get_log("Print")


def hook_print(*objects, sep=" ", end="\n", file=None, flush=False):
    return log_print.debug((sep.join(map(str, objects)) + end).replace("\n", " "))


# region trans


def dump_format(format_name: str = "default", **kw) -> dict[str, dict[str, str]]:

    back_format = {}
    back_format["format"], back_format["datefmt"] = (
        ("<%(asctime)s>[%(levelname)s]%(name)s:%(message)s", "%Y-%m-%d %H:%M:%S")
        if format_name == "default"
        else (kw["format"], kw["datefmt"])
    )
    return back_format


def dump_handler(
    handler_class: str, formatter: str = "default", level: str | None = None, **kw
) -> dict[str, str | None]:
    back_handler = {}

    # region trans handlers
    if handler_class == "Console":
        handler_class, back_handler["stream"] = (
            "logging.StreamHandler",
            "ext://sys.stdout",
        )
    if handler_class == "File":
        handler_class = "logging.handlers.RotatingFileHandler"
    # endregion

    # region dump handlers
    back_handler["class"] = handler_class
    if handler_class == "logging.NullHandler":
        return back_handler

    back_handler["formatter"] = formatter
    if level is not None:
        back_handler["level"] = level

    if (back_handler["class"]) == "logging.handlers.RotatingFileHandler":
        if (filename := kw.get("filename")) is not None:
            back_handler["filename"] = filename
            file.mkdir(filename)

        back_handler["maxBytes"] = kw.get("maxBytes", 1048576)
        back_handler["backupCount"] = kw.get("backupCount", 3)
        back_handler["encoding"] = kw.get("encoding", "utf8")
    # endregion

    return back_handler


def trans_config(
    handlers: list, formats: list | None = None, exist_loggers: bool = True, **kw
) -> dict[str, Any]:

    # init config
    config: dict[str, Any] = {"version": 1, "formatters": {}, "handlers": {}}
    config["loggers"] = {"": {"handlers": [], "level": kw.get("root_level", "INFO")}}

    # exist loggers
    config["disable_existing_loggers"] = "False" if exist_loggers is True else "True"

    # default formats
    if formats is None:
        formats = ["default"]

    # formatters
    for format_name in formats:
        format_kw = (
            {"format": format_, "datefmt": datefmt}
            if (format_ := kw.get(f"{format_name}_format")) is not None
            and ((datefmt := kw.get(f"{format_name}_datefmt"))) is not None
            else {}
        )
        config["formatters"][format_name] = dump_format(format_name, **format_kw)

    # handlers
    for handler_name in handlers:
        dump_handler_kwargs = {
            "handler_class": kw.get(f"{handler_name}_class", "Console")
        }
        for key in kw.keys():
            if key.startswith(f"{handler_name}_"):
                dump_handler_kwargs[key.replace(f"{handler_name}_", "")] = kw[key]

        config["handlers"][handler_name] = dump_handler(**dump_handler_kwargs)
        config["loggers"][""]["handlers"].append(handler_name)

    return config


# endregion


def set_log(config_dict, *, builtin: bool = False, print_: bool = False) -> None:
    try:
        config.dictConfig(trans_config(**config_dict))

        if builtin or print_:
            from ..runtime.py_env import set_global

            if builtin:
                set_global("get_log", get_log)
            if print_:
                set_global("print", hook_print)

    except Exception as e:
        logger = get_log("RCTK.Log")
        logger.error(
            "Failed to set logging config: {e}\nData: {data}".format(
                e=e, data=str(config_dict)
            )
        )
        from .env import is_debug

        if is_debug():
            raise
