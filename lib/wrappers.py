from typing import Callable
from functools import wraps

def debugIO(func: Callable) -> Callable:
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        print(f'== DEBUG FOR {func.__name__} == \
              \n - Arguments: {args},\
              \n - Key-arguments: {kwargs}')
        
        result = func(*args, **kwargs)
        
        print(f'Output is: {result}')
        
        return result
    
    return wrapper


@debugIO
def test(num: int, word: str) -> list[str]:
    for _ in range(num):
        print(f"{word:_>20}")

    return "Finished"


def main() -> None:
    test(num=4, word='testing')


if __name__ == "__main__":
    main()