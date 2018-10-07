# SmoothArray: A Dynamic Array With (Non-Amoritzed) Constant-Time Append


Coders love [dynamic arrays](https://en.wikipedia.org/wiki/Dynamic_array).
I do too, but I never felt the urge to publish one before now.

There are many dynamic arrays already out there, including the
always-popular:
- Python _list_
- JavaScript _Array_
- Java _ArrayList_
- C++ _std::vector_

Those popular arrays work so well that there's almost never any need to
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

Dynamic arrays hide that manual workaround work from us.

When pushing or appending new values to the end of a dynamic array, the
array itself keeps track of the size and capacity of whatever underlying
data structure is being used, maybe a C array for example, but we don't
care. The data gets copied silently and automatically whenever the memory
needs to be reallocated.

In Python, the code for appending (including the possible implicit resize
operation) looks like this:

```
myarray.append(5)
```

## Speed

The append function for dynamic arrays in Python and the equivalent
functions in every language I can think of all run in [amortized constant time](https://en.wikipedia.org/wiki/Amortized_analysis#Dynamic_Array), a.k.a. amortized O(1) time,
which is as fast as you can get. Or is it?

Usually, myarray isn't full, so appending a value is as simple as copying
the one value to the empty spot just past the end of the array.

Occasionally, though, the array's capacity fills up, and the _.append_
function must do more work. New, bigger, memory resources must be
allocated. All values that were already stored in the old memory must be
copied into the new memory.

That copying activity runs in linear time, a.k.a. O(n) time, because all
_n_ items in the array must each be copied, which is much slower than the
usual O(1) run time where only one item is copied. But the linear copy
only happens very rarely, meaning the _.append_ function calls are usually
O(1).

In fact, it turms out there are about _n_ O(1) calls for every O(n) call.
We can go ahead and divide O(n) by n\*O(1) giving us the amortized constant
time O(1) append that all the popular dynamic arrays feature.

## Amortized

I recently started thinking about that word "amortized", for fun. What
would it mean if a dynamic array could actually append in O(1) time,
non-amortized? Would that even make sense?

A dynamic array with true-O(1) append wouldn't ever be able to copy _n_
items into reallocated memory during the append call, because that call
would run in O(n) time, and O(n) is obviously not O(1).

Instead of copying _n_ memory items, what if we copied nothing? One
"solution" would be to never copy the array. We could allocate all the
memory in the system into one Gigantic array. That huge array would never
need to be reallocated. Appending would work great, resizing the array by
+1 for each call, in O(1) time, all the way up until hitting the system's
out of memory error.

The Gigantic design would be great for the performance of the
dynamic array, but at the cost of being terribly wasteful of memory
resources. We coders demand efficiency _and_ convienence.

## Optimization Technique

Optimization work usually requires understanding what trade-offs are
being made between different resources, such as between time and memory.
Most optimizations don't come for free.

The hypothetical Gigantic dynamic array design trades away memory, tons
of memory, in exchange for slightly more speed. Obviously, this trade off
isn't worth it for most use cases, but the Gigantic design is educational
in that it shows us a boundary. To avoid copying, the Gigantic array never,
ever reallocates its memory. You can't reallocate less often than never.

If I was gonna think of a successful O(1) design for a dynamic array, I
knew I wasn't willing to reallocate "never", because the Gigantic example
is too wasteful of memory for a general-purpose dynamic array. (But some
very demanding applications do use the technique of allocating way too much
memory up front, so as to never have to worry about reallocating it later.)

What about the other direction? Instead of reallocating never, what if
we reallocated always? What if the size and the capacity of our dynamic
array were always equal, meaning that every single call to append would
need to reallocate the underlying memory to add room for one more item?

Nope. Reallocating "always" also implies an O(n) copy "always". It doesn't
help us at all to make append be O(n).

## System Memory

Thinking about reallocating "always" did make me wonder if reallocating and
copying necessarily had to happen at the same time.

System memory allocation can often be O(1), or if slower, perhaps O(log x)
or O(x). And, we can often assume that _x_ is not related to our _n_, the
size of our array. For the purposes of this discussion the system's memory
allocator will be considered not part of the design. On some systems it
is [guaranteed to be O(1)](https://stackoverflow.com/questions/282926/time-complexity-of-memory-allocation).

Dynamic arrays typically double their capacity every time they reallocate.
A true-O(1) append function can't copy _n_ items, but what I realized does
work is for the dynamic array to copy _1_ item, every call.

## A Smoother Dynamic Array: SmoothArray

This is the technique used by SmoothArray.

When a SmoothArray fills up, it allocates a new memory space that is double
the capacity of the previous memory. Exactly one old item is then copied
from the old memory into the new. Then the new item is appended.

Because the memory capacity was just doubled, if appends keep coming, then
the new, bigger array will fill up at exactly the same time that the last
item of the old, half-size memory space is copied into the new space. The
old memory can then be discarded and the new memory becomes the old memory.

The O(1) SmoothArray design was first written in Python as a simple
proof-of-concept. A similar class, AmortizedArray, was also written to
allow comparison to the traditional amortized-O(1)-append method.
SmoothArray and AmortizedArray are intended to be identical in every
way except for the copying.

Here's how the timings of the two append techniques compare:

| size    | AmortizedArray | SmoothArray    |
| ------- | -------------- | -------------- |
|    2048 |   0 ms         |   0 ms         |
|    4096 |   1 ms         |   0 ms         |
|    8192 |   1 ms         |   0 ms         |
|   16384 |   2 ms         |   0 ms         |
|   32768 |   4 ms         |   0 ms         |
|   65536 |   8 ms         |   0 ms         |
|  131072 |  16 ms         |   0 ms         |
|  262144 |  33 ms         |   0 ms         |
|  524288 |  68 ms         |   1 ms         |
| 1048576 | 144 ms         |   2 ms         |

