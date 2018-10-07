# SmoothArray: A Dynamic Array With (Non-Amoritzed) Constant-Time Append


Coders love [dynamic arrays](https://en.wikipedia.org/wiki/Dynamic_array).
I do. But I never felt the need to publish one before.

There are many dynamic arrays in the world, including the always-popular:
-Python _list_
-JavaScript _Array_
-Java _ArrayList_
-C++ _std::vector_

Those popular arrays work so well that there is almost never a need to
write your own. Experts have carefully-reviewed the popular tools and
those tools come to us already highly-optimized.

## The Problem

A dynamic array, of course, is a resizable array that manages its own
memory. In contrast, a non-dynamic (static) array has a fixed size, like
this array in C code:

```
int myarray[5] = {0, 1, 2};
```

The myarray array has 5 memory locations allocated for it, but only
3 of those locations contain anything. In the usual terminology, this array
has a **size** of 3, but a **capacity** of 5. We could easily append two more
numbers to the end of myarray, but only two:

```
myarray[3] = 3;
myarray[4] = 4;
```

The array is now full. Appending a 6th number to the static array with a
capacity of only 5 is impossible. Static arrays don't change capacity.

## The Workaround

As a workaround, we could create a new static array, myarray2[6], then
manually copy the 5 numbers from myarray into myarray2, and finally add a
6th to the end:

```
myarray2[5] = 5;
```

That works, but it's a pain to keep track of the capacity of the static
array, then notice when that array is full, and finally copy the old array
into a new array, when all we really wanted to do is append one more
number to the end of the original array.

## The Solution

Dynamic arrays hide that manual work for us.

When pushing or appending new values to the end of a dynamic array, the
array irself keeps track of the size and capacity of whatever underlying
data structure is being used, maybe a C array but we don't care, and the
data gets copied silently and automatically whenever the memory needs to
be reallocated.

In Python, the code to append (including the possible implicit resize
operation) looks like this:

```
myarray.append(5)
```

# Speed

The append function for dynamic arrays in Python or the equivalent
functions in every language I can think of all run in [amortized constant time](https://en.wikipedia.org/wiki/Amortized_analysis#Dynamic_Array), a.k.a. amortized O(1) time,
which is as fast as you can get. Or is it?

Usually, myarray isn't full, so appending a value is as simple as copying
the one value to the empty spot just past the end of the array.

Occasionally, though, the array's capacity fills up, and the _.append_
function must do more work. New, bigger, memory resources must be
allocated. All values that were already stored in the old memory must be
copied into the new memory.

That copying activity runs in linear time, a.k.a. O(n) time, which is
much slower than O(1). But the linear copy only happens very rarely,
meaning the _.append_ function calls are usually O(1).

In fact, there are about _n_ O(1) calls for every O(n) call. We can go
ahead and divide O(n) by n\*O(1) giving us the amortized constant time
_.append_ that all the popular dynamic arrays feature.

I recently started thinking about that word "amortized", for fun. What
would it mean if a dynamic array **actually** could append in O(1) time?

