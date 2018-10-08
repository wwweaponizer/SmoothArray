#!/usr/bin/env python

"""
SmoothArray()

The SmoothArray() class, a dynamic array with constant-time (not
amortized) O(1) append.

Some doctests:

>>> SmoothArray()
SmoothArray()

>>> SmoothArray((0, 1, 2, 3))
SmoothArray((0, 1, 2, 3))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.append(4)
>>> sa
SmoothArray((0, 1, 2, 3, 4))
>>> sa.append(5)
>>> sa
SmoothArray((0, 1, 2, 3, 4, 5))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.extend((4, 5, 6, 7, 8, 9))
>>> sa
SmoothArray((0, 1, 2, 3, 4, 5, 6, 7, 8, 9))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.insert(2, '+1')
>>> sa
SmoothArray((0, 1, '+1', 2, 3))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.remove(2)
>>> sa
SmoothArray((0, 1, 3))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.pop()
3
>>> sa
SmoothArray((0, 1, 2))
>>> sa.pop(0)
0
>>> sa
SmoothArray((1, 2))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.clear()
>>> sa
SmoothArray()

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.index(2)
2

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.count(2)
1

>>> sa = SmoothArray((3, 0, 1, 2))
>>> sa.sort(reverse=True)
>>> sa
SmoothArray((0, 1, 2, 3))

>>> sa = SmoothArray((0, 1, 2, 3))
>>> sa.reverse()
>>> sa
SmoothArray((3, 2, 1, 0))

>>> sa1 = SmoothArray((0, 1, 2, 3))
>>> sa2 = sa1.copy()
>>> sa2[1] = 999
>>> sa1
SmoothArray((0, 1, 2, 3))
>>> sa2
SmoothArray((0, 999, 2, 3))
"""

import ctypes
from datetime import datetime, timedelta
from numbers import Integral
import sys

if (sys.version_info.major == 3 and sys.version_info.minor >= 3) \
   or sys.version_info.major > 3:
    from collections.abc import MutableSequence    # Python 3+
else:
    from collections import MutableSequence        # Python 2

class SmoothArray(MutableSequence):
    """Dynamic array with constant (not amortized) O(1) time append."""

    def __init__(self, seq=None):
        self._capacity = 0    # array memory allocated
        self._size = 0        # array memory in use (len)
        self._data1 = None    # old array
        self._data2 = None    # new array
        self._move = 0        # start of old array range
        self._stop = 0        # end+1 of old array range
        if seq is not None:
            for s in seq:
                self.append(s)
        # NOTE: _data1 and _data2 are initialized to None to save space for empty arrays

    def __repr__(self):
        if self._size > 0:
            return type(self).__name__+'(('+', '.join([repr(item) for item in self])+'))'
        else:
            return type(self).__name__+'()'

    def __len__(self):
        return self._size

    def __getitem__(self, i):
        # TODO: support slice indexes
        if isinstance(i, Integral):
            if i < 0:
                i = self._size+i
            if not (0 <= i < self._size):
                raise IndexError('index out of range')

            if self._move <= i < self._stop:
                return self._data1[i]
            else:
                return self._data2[i]
        elif isinstance(i, slice):
            raise RuntimeError('slice notation is unimplemented')
        else:
            raise TypeError('indices must be integers or slices')

    def __setitem__(self, i, item):
        if isinstance(i, Integral):
            if i < 0:
                i = self._size+i
            if not (0 <= i < self._size):
                raise IndexError('index out of range')

            if self._move <= i < self._stop:
                self._data1[i] = item
            else:
                self._data2[i] = item
        elif isinstance(i, slice):
            raise RuntimeError('slice notation is unimplemented')
        else:
            raise TypeError('indices must be integers or slices')

    def __delitem__(self, i):
        if isinstance(i, Integral):
            if i < 0:
                i = self._size+i
            if not (0 <= i < self._size):
                raise IndexError('index out of range')

            for j in range(i+1, self._size):
                self[j-1] = self[j]
            self._size -= 1
            if i <= self._move:
                self._move -= 1
            if i < self._stop:
                self._stop -= 1
        elif isinstance(i, slice):
            raise RuntimeError('slice notation is unimplemented')
        else:
            raise TypeError('indices must be integers or slices')

    def append(self, item):
        # Initialize the array memory if this is the first append.
        if self._capacity == 0:
            self._capacity = 1
            self._data2 = (self._capacity*ctypes.py_object)()

        # Double the array capacity if the array is full.
        elif self._size == self._capacity:
            self._move = 0
            self._stop = self._capacity
            self._capacity *= 2
            self._data1 = self._data2
            self._data2 = (self._capacity*ctypes.py_object)()

        # Move an item from the old array to the new array.
        # This is how the SmoothArray can have O(1) append(),
        # because append() always moves zero or one items, never
        # the full array or a proportion of the full array size.
        if self._move < self._stop:
            self._data2[self._move] = self._data1[self._move]
            self._move += 1

        # Append the new item to the new array.
        self._data2[self._size] = item
        self._size += 1

    def insert(self, i, item):
        j = self._size
        self.append(None)
        while j > i:
            self[j] = self[j-1]
            j -= 1
        self[i] = item

    def sort(self, key=None, reverse=False):
        s = sorted(self)
        for i in range(self._size):
            self[i] = s[i]
        # TODO: optimize by doing an in-place sort

    def copy(self):
        c = type(self)()
        c._capacity = self._capacity
        c._size = self._size
        c._data1 = (len(self._data1)*ctypes.py_object)() if self._data1 is not None else None
        c._data2 = (len(self._data2)*ctypes.py_object)() if self._data2 is not None else None
        for i in range(self._size):
            if self._move <= i < self._stop and self._data1 is not None:
                c._data1[i] = self._data1[i]
            elif self._data2 is not None:
                c._data2[i] = self._data2[i]
        c._move = self._move
        c._stop = self._stop
        return c

    if sys.version_info.major < 3:
        def clear(self):
            self.__init__()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

