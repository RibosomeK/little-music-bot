from typing import Callable, Dict, Any, Iterable


def try_if_no_exceptions(
    target: Callable,
    kwargs: Dict[str, Any],
    exceptions: Iterable[Any],
    attempt: int = 3,
):
    """keep trying to run target if any exception is raised in exceptions for attempt times"""
    for _ in range(attempt):
        try:
            return target(**kwargs)
        except Exception as e:
            if e in exceptions:
                pass
            else:
                raise e
    raise ExceedTryAttemptError()


class UnknownPlatformError(Exception):
    """unknown platform"""
    
    
class ExceedTryAttemptError(Exception):
    """failed after too many tries"""
