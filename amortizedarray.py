#!/usr/bin/env python

"""
AmortizedArray()

The AmortizedArray() class, a dynamic array with
amortized-constant-time O(1) append.

>>> AmortizedArray()
AmortizedArray()

>>> AmortizedArray((0, 1, 2, 3))
AmortizedArray((0, 1, 2, 3))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.append(4)
>>> sa
AmortizedArray((0, 1, 2, 3, 4))
>>> sa.append(5)
>>> sa
AmortizedArray((0, 1, 2, 3, 4, 5))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.extend((4, 5, 6, 7, 8, 9))
>>> sa
AmortizedArray((0, 1, 2, 3, 4, 5, 6, 7, 8, 9))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.insert(2, '+1')
>>> sa
AmortizedArray((0, 1, '+1', 2, 3))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.remove(2)
>>> sa
AmortizedArray((0, 1, 3))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.pop()
3
>>> sa
AmortizedArray((0, 1, 2))
>>> sa.pop(0)
0
>>> sa
AmortizedArray((1, 2))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.clear()
>>> sa
AmortizedArray()

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.index(2)
2

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.count(2)
1

>>> sa = AmortizedArray((3, 0, 1, 2))
>>> sa.sort(reverse=True)
>>> sa
AmortizedArray((0, 1, 2, 3))

>>> sa = AmortizedArray((0, 1, 2, 3))
>>> sa.reverse()
>>> sa
AmortizedArray((3, 2, 1, 0))

>>> sa1 = AmortizedArray((0, 1, 2, 3))
>>> sa2 = sa1.copy()
>>> sa2[1] = 999
>>> sa1
AmortizedArray((0, 1, 2, 3))
>>> sa2
AmortizedArray((0, 999, 2, 3))
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

class AmortizedArray(MutableSequence):
    """Dynamic array with amortized-constant-time O(1) append."""

    def __init__(self, seq=None):
        self._capacity = 0    # array memory allocated
        self._size = 0        # array memory in use (len)
        self._data = None
        if seq is not None:
            for s in seq:
                self.append(s)
        # NOTE: _data is initialized to None to save space for empty arrays

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

            return self._data[i]
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

            self._data[i] = item
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
        elif isinstance(i, slice):
            raise RuntimeError('slice notation is unimplemented')
        else:
            raise TypeError('indices must be integers or slices')

    def append(self, item):
        # Initialize the array memory if this is the first append.
        if self._capacity == 0:
            self._capacity = 1
            self._data = (self._capacity*ctypes.py_object)()

        # Double the array capacity if the array is full.
        elif self._size == self._capacity:
            old_data = self._data
            old_capacity = self._capacity
            self._capacity *= 2
            self._data = (self._capacity*ctypes.py_object)()
            for i in range(old_capacity):
                self._data[i] = old_data[i]

        # Append the new item to the new array.
        self._data[self._size] = item
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
        if self._data is not None:
            c._data = (len(self._data)*ctypes.py_object)()
            for i in range(self._size):
                c._data[i] = self._data[i]
        else:
            c._data = None
        return c

    if sys.version_info.major < 3:
        def clear(self):
            self.__init__()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

