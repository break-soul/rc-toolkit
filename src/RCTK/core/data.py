"""
Common base class for all data
"""

import os,json

from typing import Any, Union, List, overload

from .enums import MISSING
from .io.file import mkdir
def load(path: str) -> dict:
    """
    Load data from a file.

    Args:
        path (str): file path

    Returns:
        dict: data
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def sync(data: dict, path: str):
    """
    Sync data to a file.
    """
    if not os.path.exists(path):
        mkdir(path)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)

class _Field:
    """
    A class representing a field.
    Attributes:
        default (Any): The default value of the field.
        type (Any): The type of the field.
        data (Any): The current data of the field.
        name (str): The name of the field.
    Methods:
        __init__(self, default: Any = MISSING, default_type: Any = MISSING) -> None:
            Initializes a new instance of the _Field class.
        check_type(self, value: Any = MISSING, type_: type = MISSING) -> bool:
            Checks if the given value matches the type of the field.
        __repr__(self) -> str:
            Returns a string representation of the _Field object.
        set_name(self, name: str) -> None:
            Sets the name of the field.
        set_data(self, data: Any) -> None:
            Sets the data of the field.
        __set_name__(self, owner, name):
            Sets the name of the field using the __set_name__ method of the default value.
    """

    __slots__ = ("default", "type", "data", "name")

    _FIELD = "Field"

    def __init__(
        self,
        default: Any = MISSING,
        default_type: Any = MISSING,
    ) -> None:
        if default is MISSING and default_type is MISSING:
            raise ValueError("default or default_type must be provided")
        if default is not MISSING and default_type is not MISSING:
            if self.check_type(default, default_type):
                self.default = default
                self.type = default_type
            else:
                raise ValueError("default value does not match the type")
        else:
            if default is not MISSING:
                self.type = type(default)
            else:
                self.type = default_type
            self.default = default
        self.data = default

    # region check_type
    @overload
    def check_type(self) -> bool: ...
    @overload
    def check_type(self, value: Any) -> bool: ...
    @overload
    def check_type(self, value: Any, type_: "type") -> bool: ...
    def check_type(self, value: Any = MISSING, type_: "type" = MISSING) -> bool: # type: ignore
        if value is MISSING:
            return isinstance(self.data, self.type)
        if type_ is MISSING:
            return isinstance(value, self.type)
        return isinstance(value, type_)

    # endregion

    def __repr__(self) -> str:
        """
        Return a string representation of the object.

        Returns:
            str: The string representation of the object.
        """
        return f"{self._FIELD}(default={self.default}, type={self.type})"

    def set_name(self, name: str) -> None:
        """
        Set the name of the object.

        Parameters:
        - name (str): The name to be set.

        Returns:
        - None
        """
        self.name = name

    def set_data(self, data: Any) -> None:
        """
        Set the data for the object.

        Parameters:
            data (Any): The data to be set.

        Raises:
            ValueError: If the data does not match the type.

        Returns:
            None
        """
        if self.check_type(data):
            self.data = data
        else:
            raise ValueError("data does not match the type")

    def __set_name__(self, owner, name):
        func = getattr(type(self.default), "__set_name__", None)
        if func:
            func(self.default, owner, name)


def Field(default: Any = MISSING, default_type: Any = MISSING) -> Any:
    """
    Create a field with optional default value and default type.

    Args:
        default (Any, optional): The default value for the field. Defaults to MISSING.
        default_type (Any, optional): The default type for the field. Defaults to MISSING.

    Returns:
        Any: The created field.
    """
    return _Field(default, default_type)



class BaseData:
    """
        Attributes:
            path (Union[str, None], optional): path to the data file. Defaults to None.

        priority of data, higher priority will overwrite lower priority, -1 to disable
            init_p (int, optional): priority of init data. Defaults to 4.
            env_p (int, optional): priority of env data. Defaults to 3.
            file_p (int, optional): priority of file data. Defaults to 2.
            default_p (int, optional): priority of default data. Defaults to 1.

    Methods:
        _dump_config(self) -> None: Dump the configuration settings.
        _load_data(self) -> None: Load the data using the priority functions.
        _load_fields(self, source: dict) -> None: Load the fields from the given source.
        _load_init(self): Load the initial data.
        _load_file(self): Load the data from a file.
        _load_default(self): Placeholder method.
        __dir__(self) -> List[str]: Return a list of attribute names.
    ...
    """

    def __new__(cls) -> "BaseData":
        fields = dict()
        for _name, _field in cls.__dict__.items():
            if getattr(_field, "_FIELD", None) is not None:
                _field.set_name(_name)
                fields[_name] = _field
        obj = super().__new__(cls)
        obj._fields = fields # type: ignore
        return obj

    def __init__(
        self,
        /,
        path: Union[str, None] = None,
        init_p: int = 4,
        file_p: int = 2,
        default_p: int = 1,
        **kw,
    ) -> None:
        self._path = path
        self._p = {
            init_p: self._load_init,
            file_p: self._load_file,
            default_p: self._load_default,
        }
        self._kw = kw
        self._load_data()

    def _load_data(self) -> None:
        """
        Load data into the object.

        This method is responsible for loading data into the object. It performs the following steps:
        1. Removes the last element from the list '_p'.
        2. Iterates over the keys in '_p' in sorted order and calls the corresponding value as a function.
        3. Sets the attributes of the object based on the data stored in the fields.

        Returns:
            None
        """
        self._p.pop(-1, None)
        for p in sorted(self._p.keys()):
            self._p[p]()
        for field in self._fields.values(): # type: ignore
            setattr(self, field.name, field.data)

    def _load_fields(self, source: dict) -> None:
        """
        Load the fields of the object from the given source dictionary.

        Parameters:
            source (dict): The dictionary containing the field data.

        Returns:
            None
        """
        for field in self._fields.values(): # type: ignore
            try:
                if field.name in source:
                    field.set_data(source[field.name])
            except:
                ...

    def _load_init(self):
        """
        Load the initial data for the object.

        This method is responsible for loading the initial data for the object.
        It calls the `_load_fields` method with the keyword arguments provided
        during initialization.
        """
        self._load_fields(self._kw)

    def _load_file(self):
        """
        Loads data from a file specified by the `_path` attribute.
        If `_path` is not None, it loads the data using the `load` function,
        and then calls the `_load_fields` method to populate the fields with the loaded data.
        """
        if self._path is not None:
            try:
                data = load(self._path)
            except FileNotFoundError:
                sync({}, self._path)
                data = {}
            self._load_fields(data)

    def _load_default(self):
        """Useless, used only as a placeholder"""
        ...

    def __dir__(self) -> List[str]:
        """
        Return a list of attribute names for the fields.

        Returns:
            List[str]: A list of attribute names.
        """
        return list(self._fields.keys())     # type: ignore
