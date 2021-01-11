"""
Some functions that are useful like 
map
reduce
zip
filter
...

These probalby exist but it's easier for me to do them here
"""


def map(func, arr):
    new_arr = []
    for item in arr:
        new_arr.append(func(item))

    return new_arr