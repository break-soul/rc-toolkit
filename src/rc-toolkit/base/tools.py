

class LazyLoad:
    """
    LazyLoad is a utility that defers the execution of a given function until it is actually called.
    It stores the result of the function after the first call, so subsequent calls do not re-run
    the function.
    Attributes:
        func (callable): The function to be executed lazily.
        result (Any): The cached result from the function call, set after the first execution.
        has_run (bool): A flag indicating whether the function has been executed.
        args (tuple): Positional arguments to pass to the function when executed.
        kwargs (dict): Keyword arguments to pass to the function when executed.
    Methods:
        __call__():
            Executes the function if it has not been run before, and caches the result.
            Returns the cached result on all subsequent calls.
        __getattr__(name):
            Allows attribute access on the cached result. If the function has not been executed yet,
            it is called before retrieving the attribute.
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.result = None
        self.has_run = False
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        if not self.has_run:
            self.result = self.func(*self.args, **self.kwargs)
            self.has_run = True
        return self.result

    def __getattr__(self, name):
        obj = self.__call__()
        return getattr(obj, name)


def lazy_load(func, *args, **kwargs):
    return LazyLoad(func, *args, **kwargs)
