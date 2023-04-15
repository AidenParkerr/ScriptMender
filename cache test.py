from functools import lru_cache

@lru_cache
def cache_test(a, b):
    print(f"sum of a: {a} and b: {b}")
    return a + b


print(cache_test(8, 2))
print(cache_test(8, 2))
print(cache_test(8, 2))
print(cache_test(8, 2))
print(cache_test(8, 2))
print(cache_test(8, 2))
print(cache_test(8, 2))