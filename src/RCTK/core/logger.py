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


# region trans


def dump_format(
    format_name: str = "default", **kw: Mapping[str, str | None]
) -> dict[str, dict[str, str]]:

    back_format = {}
    back_format["format"], back_format["datefmt"] = (
        ("<%(asctime)s>[%(levelname)s]%(name)s:%(message)s", "%Y-%m-%d %H:%M:%S")
        if format_name == "default"
        else (kw["format"], kw["datefmt"])
    )
    return back_format


def dump_handler(
    handler_class: str,
    formatter: str = "default",
    level: str | None = None,
    **kw: Mapping[str, str | None],
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

    if (file_name := back_handler["class"]) == "logging.handlers.RotatingFileHandler":
        if kw["filename"] is not None:
            back_handler["filename"] = kw["filename"]
            file.mkdir(file_name)

        back_handler["maxBytes"] = kw["maxBytes"]
        back_handler["backupCount"] = kw["backupCount"]
        back_handler["encoding"] = kw["encoding"]
        back_handler["encoding"] = "utf8"
    # endregion

    return back_handler


def trans_config(
    handlers: list,
    formats: list | None = None,
    exist_loggers: bool = True,
    **kw,
) -> dict[str, Any]:

    # init config
    config = {}
    config["version"] = 1
    config["formatters"] = {}
    config["handlers"] = {}
    config["loggers"] = {}
    config["loggers"][""] = {}
    config["loggers"][""]["handlers"] = []
    config["loggers"][""]["level"] = kw.get("root_level", "INFO")

    # exist loggers
    config["disable_existing_loggers"] = "False" if exist_loggers is True else "True"

    # default formats
    if formats is None:
        formats = ["default"]

    # formatters
    for format_name in formats:
        format_kw = {}
        if (format_ := kw.get(f"{format_name}_format")) is not None and (
            (datefmt := kw.get(f"{format_name}_datefmt"))
        ) is not None:
            format_kw = {
                "format": format_,
                "datefmt": datefmt,
            }
        config["formatters"][format_name] = dump_format(
            format_name=format_name, **format_kw
        )

    # handlers
    for handler_name in handlers:
        config["handlers"][handler_name] = dump_handler(
            handler_class=kw.get(f"{handler_name}_class", "Console"),
            formatter=kw.get(f"{handler_name}_formatter", "default"),
            level=kw.get(f"{handler_name}_level", "INFO"),
            filename=kw.get(f"{handler_name}_filename", "log.log"),
            maxBytes=kw.get(f"{handler_name}_maxBytes", 1048576),
            backupCount=kw.get(f"{handler_name}_backupCount", 3),
            encoding=kw.get(f"{handler_name}_encoding", "utf8"),
        )
        config["loggers"][""]["handlers"].append(handler_name)

    return config


# endregion

log_print = get_log("Print")


def hook_print(*objects, sep=" ", end="\n", file=None, flush=False):
    return log_print.debug((sep.join(map(str, objects)) + end).replace("\n", " "))


def set_log(config_dict, *, builtin: bool = False, print_: bool = False) -> None:
    try:
        config.dictConfig(trans_config(**config_dict))

        if builtin:
            from ..runtime.py_env import set_global
            set_global("get_log", get_log)
            if print_:
                set_global("print", hook_print)

    except Exception as e:
        logger = get_log("RCTK.Log")
        logger.error("Failed to set logging config: {error}\nData: {data}".format(error=e,data=str(config_dict)))
        from .env import is_debug
        if is_debug():
            raise
