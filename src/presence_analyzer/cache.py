"""
Caching back-end classes.
"""
import cPickle
import threading

from datetime import datetime, timedelta


class Cache(object):
    """
    Base class for all caching back-ends.
    """
    def get(self, function, *args, **kwargs):
        """
        Method to get result of function from cache.
        :param function: cached function
        :param args: function args
        :param kwargs: function kwargs
        :return: cached result or None
        """
        raise NotImplementedError

    def set_expire(self, function, time, *args, **kwargs):
        """
        Method to set with expiration result of function in cache.
        :param function: cached function
        :param time: time of expiration since now (seconds)
        :param args: function args
        :param kwargs: function kwargs
        :return: result of function
        """
        raise NotImplementedError

    def get_or_set(self, function, time, *args, **kwargs):
        """
        If available, returns result from cache. Else, calls set_expire method
        and returns result of function.
        :param function: cached function
        :param time: time of expiration since now (seconds)
        :param args: function args
        :param kwargs: function kwargs
        :return: result of function
        """
        cached = self.get(function, *args, **kwargs)
        if not cached:
            cached = self.set_expire(function, time, *args, **kwargs)
        return cached


class MemoryCache(Cache):
    """
    Cache implemented as a dictionary.
    """
    def __init__(self):
        self.cache = {}
        self.thread_lock = threading.Lock()

    @staticmethod
    def hash_args_kwargs(function, *args, **kwargs):
        """
        Creates unique identifier of function call with arguments.
        :param function:
        :param args: function args
        :param kwargs: function kwargs
        :return: String, identifier of function call (function name, args and
        kwargs.
        """
        return cPickle.dumps((function.__name__, args, kwargs))

    def clean(self):
        """
        Cleans cache dictionary.
        """
        self.cache = {}

    def get(self, function, *args, **kwargs):
        """
        Gets result of function from cache if entry has not expired yet.
        :param function:
        :return: result from cache
        """
        now = datetime.now()
        function_hash = self.hash_args_kwargs(function, args, kwargs)
        in_cache_valid = (
            function_hash in self.cache and
            self.cache[function_hash].get('expire_time') > now
        )

        if in_cache_valid:
            result = self.cache[function_hash].get('result')
            return result

    def set_expire(self, function, time, *args, **kwargs):
        """
        Saves result of function in cache, sets cache time.
        :param function: cached function
        :param time: time of result expiry
        :return: result of function
        """
        function_hash = self.hash_args_kwargs(function, args, kwargs)
        with self.thread_lock:
            result = function(*args, **kwargs)
            self.cache[function_hash] = {
                'result': result,
                'expire_time': datetime.now() + timedelta(seconds=time),
            }
        return result
