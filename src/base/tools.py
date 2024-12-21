

def lazy_load(func, *args, **kwargs):

    class LazyLoad:
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

    return LazyLoad(func, *args, **kwargs)
