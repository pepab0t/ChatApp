def decorator(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


@decorator
def foo(**kwargs):
    print(kwargs)


foo()
