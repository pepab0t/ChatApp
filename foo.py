from application.auth.token import token_valid
import inspect

args = inspect.getargspec(token_valid)
print(args)
