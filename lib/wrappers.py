from typing import Callable
from functools import wraps

def debugIO(func: Callable) -> Callable:
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        result = func(*args, **kwargs)

        print(
            f"[{func.__name__}] : function took and returned these arguments:\n"
            f" - Arguments: {args},\n"
            f" - Key-arguments: {kwargs},\n"
            f" - Output: {result}"
        )
        
        return result
    
    return wrapper

def func_timing(func: Callable) -> Callable:

    @wraps(func)
    def wrapper(*args, **kwargs):

        import time

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        print(f"[{func.__name__}] : function execution time was: {end - start:.6f} seconds")
        
        return result
    
    return wrapper

# python -m venv .venv
# source .venv/Scripts/activate