def foo():
    print("open")
    yield 1
    print("close")


g = foo()
# print(next(g))
# next(g)
