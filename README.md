# SmoothArray: A Dynamic Array With (Non-Amortized) Constant-Time Append


Coders love [dynamic arrays](https://en.wikipedia.org/wiki/Dynamic_array).
I love them too, but I never felt the urge to publish one before now.

There are many dynamic arrays out there, including the popular:
- Python _list_
- JavaScript _Array_
- Java _ArrayList_
- C++ _std::vector_

Those popular arrays work so well that there's almost never any need to
write your own. Experts have carefully reviewed the popular tools and
they come to us highly-optimized.

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
numbers to the end of myarray, but no more than two:

```
myarray[3] = 3;
myarray[4] = 4;
```

The array is now full. Appending a 6th number to the static array with a
capacity of only 5 is impossible. Static arrays don't change capacity.

## The Workaround

As a workaround, we could create a new static array, myarray2, then
manually copy the 5 numbers from myarray into myarray2, and finally add a
6th to the end:

```
int myarray2[6];
for(int i = 0; i < 5; ++i)
    myarray2[i] = myarray[i];
myarray2[5] = 5;
```

That works, but it's a pain to keep track of the capacity of the static
array, then notice when that array is full, and finally copy the old array
into a new array, when all we really wanted to do is append one more
number to the end of the original array.

## The Solution

Dynamic arrays hide that manual copying work from us.

In Python, the code for appending, including the possible implicit
reallocation and copy operations, looks like this:

```
myarray.append(5)
```

When pushing/appending new values to the end of a dynamic array, the
array itself keeps track of the size and capacity of whatever underlying
data structure is being used, maybe a C array for example, but we don't
care too much about those details. The data gets copied silently and
automatically when needed without us making any effort.

## Speed

The append function for dynamic arrays in Python and the equivalent
functions in every language I can think of all run in [amortized constant time](https://en.wikipedia.org/wiki/Amortized_analysis#Dynamic_Array), a.k.a. amortized O(1) time,
which is as fast as you can get with algorithmic optimizations. Or is it?

Usually when appending, an array isn't full, so appending the value is as
simple as copying the one value to the empty spot just past the end of the
array.

Occasionally, though, the array's capacity fills up, and then the append
function must do more work. A new, bigger, memory space must be allocated.
All values that were already stored in the old memory must be copied into
the new memory.

That copying activity runs in linear time, a.k.a. O(n) time, because all
_n_ items in the array must each be copied, which is much slower than the
usual O(1) run time where only one item is copied. But the linear copy
only happens very rarely, meaning almost all of the append function calls
are O(1).

In fact, it turns out there are about _n_ O(1) calls for each O(n) call.
We can go ahead and divide O(n) by n\*O(1) in our heads right now, giving
us the amortized constant time O(1) append that all the popular dynamic
arrays feature.

## Amortized

I recently started thinking about that word "amortized", for fun. What
would it mean if a dynamic array could actually append in O(1) time,
non-amortized? Would that even make sense?

A dynamic array with true-O(1) append wouldn't ever be able to copy _n_
items into reallocated memory during the append call, because that would
mean the call ran in O(n) time, and O(n) is obviously not O(1).

If we can't copy _n_ items, what can we do?

Instead of copying _n_ memory items, maybe we could copy nothing? One
"solution" could be to allocate all the memory in the system into one
gigantic array. That huge array would never need to be reallocated.
Appending would work great, with each call resizing the array by +1, in
O(1) time, all the way up until hitting the system's out of memory error.

The gigantic design would be great for the performance of the
dynamic array, but at the cost of being terribly wasteful of memory
resources, not to mention inconvienent when other parts of the system
started hitting out of memory errors.

We the coders demand more: we want the convienence of dynamic arrays,
and we want them with both time and memory efficiency.

## Optimization Technique

Optimization usually requires understanding what trade-offs are being
made between different resources, such as between time and memory.
Optimizations never come for free if you look closely enough.

The hypothetical gigantic dynamic array design trades away memory, tons
of memory, in exchange for slightly more speed.

Obviously, that trade off isn't worth it for most use cases, but the
gigantic design is educational in that it shows us a limit. To avoid
O(n) copying, the gigantic array never, ever reallocates its memory.
And we can't reallocate less often than never. That's one limit.

If I was gonna think of a successful O(1) design for a dynamic array, I
knew I wasn't willing to reallocate "never", because the gigantic example
is too wasteful of memory for a general-purpose dynamic array. Some very
demanding applications do use the technique of allocating way too much
memory up front, intentionally, so as to never have to worry about
reallocating it later, but general-purpose tools can't be so reckless.

What about the other direction? Instead of reallocating never, what if
we reallocated always?

What if the size and the capacity of our dynamic array were always equal,
meaning that every single call to append would need to reallocate the
underlying memory to add room for one more item?

Nope. Reallocating "always" also implies an O(n) copy "always". This is
another limit: reallocating as much as possible implies an O(n) append
function.

If a true-O(1) append function is possible, the correct technique must
lie somewhere between allocating "never" and allocating "always".

## System Memory

Thinking about reallocating "never" and "always" did make me wonder if
reallocating and copying necessarily had to happen at the same time.

System memory allocation can be O(1), or if slower, will likely be O(log x)
or O(x). And, _x_ might not even be related to our _n_, the size of our
array. For the purposes of this discussion the system's memory
allocator will be considered not part of the design. On some systems it
is [guaranteed to be O(1)](https://stackoverflow.com/questions/282926/time-complexity-of-memory-allocation).

The system memory reallocation had to occur every time the array filled up,
but maybe the copying didn't.

## A Smoother Dynamic Array: SmoothArray

Dynamic arrays typically double their capacity every time they reallocate,
meaning that reallocations become much less frequent the more the array
grows in size. And we know a true-O(1) append function can't copy _n_
items, but what about copying fewer than _n_ items?

Append conceivably might copy half of _n_ during the same call that
reallocates the memory, then set a flag to remember to copy the second half
of _n_ on the following call to append, whenever that comes. In the
meantime, any reads into the array could check the same flag to know where
to look for data, either the old memory or the new.

This felt interesting. Copying half of something is faster than copying
everything at once, but when analyzing an algorithm, the constant factors
drop out. O(n/2) is still O(n) time. And we can see that dividing by two
was quite arbitrary. Maybe the copy could be divided by three or seven or
1024, if desired.

What was the limit the copying logic could be divided by? Well, once I
thought to ask that question, the answer was obvious: divide by _n_.

What does work is for the copy logic to copy _1_ item, every call.

This is the technique used by SmoothArray.

SmoothArray's append only ever copies zero or one items, usually one.

When a SmoothArray fills up, it allocates a new memory space that is double
the capacity of the previous memory. Exactly one old item is then copied
from the old memory into the new. Finally, the new item is appended.

One item was copied from old memory to new, and one new item was copied
from the caller into the new memory. So the bottom half of the new memory
is filling up 1 item at a time, at the same rate that the top half of the
new memory is filling up with newly-appended items.

If appends keep coming, then the new, bigger array will be completely
filled at exactly the same time that the last item of the old, half-size
memory space is copied into the new space. The old memory can then be
discarded and the new memory can become the old memory as seen by future
calls to append.

## Testing

The O(1) SmoothArray design was first written in Python as a simple
proof-of-concept. A similar class, AmortizedArray, was also written to
allow comparison to the traditional amortized-O(1)-append method.
SmoothArray and AmortizedArray are intended to be identical in every
way, except for the copying logic.

Here's how the timings of the two copying techniques compare on my system:

| capacity | AmortizedArray | SmoothArray    |
| -------  | -------------- | -------------- |
|    1024  |   0 ms         |   0 ms         |
|    2048  |   0 ms         |   0 ms         |
|    4096  |   1 ms         |   0 ms         |
|    8192  |   1 ms         |   0 ms         |
|   16384  |   2 ms         |   0 ms         |
|   32768  |   4 ms         |   0 ms         |
|   65536  |   8 ms         |   0 ms         |
|  131072  |  16 ms         |   0 ms         |
|  262144  |  33 ms         |   0 ms         |
|  524288  |  68 ms         |   1 ms         |
| 1048576  | 144 ms         |   2 ms         |

This test adds about one million items to an array. When the last item
is added, SmoothArray's append runs 72 times faster than AmortizedArray's.

## Trade-Offs

Seventy-two times faster sounds great! Where's the trade off? Optimization
choices always have trade-offs.

The trade-off that SmoothArray makes is that all appends that **don't**
trigger a memory reallocation are 1-2 microseconds (us) slower than
AmortizedArray's appends. A couple of _us_ in this case, while still very
fast, is technically around 10%-50% slower per call.

That slowness during regular appends is due to overhead from the more
complicated logic required for SmoothArray to manage the copying over time.

So wait: which is better, AmortizedArray or SmoothArray? The answer, as
always, depends on the use case. For most applications, AmortizedArray
is probably faster over time. But imagine an application that wanted to
append an item to an array every time that a request arrived, while
answering each request in less than, say, 10 milliseconds (ms) per request.

AmortizedArray would do fine until the array filled up to about 100,000
items. In fact, it would be slightly faster than SmoothArray. Then it would
tragically start failing requests every time the array grew.

SmoothArray would be nearly as fast as AmortizedArray, but it would
never cause requests to fail due to growing the array. So smoooooth.

