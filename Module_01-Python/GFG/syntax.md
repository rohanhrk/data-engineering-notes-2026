Absolutely. Since you’re practicing **DSA in Python**, here’s a consolidated **Python DSA syntax cheat sheet** covering the common syntax I’ve provided earlier and the patterns you’ll repeatedly use in coding problems.

# Python DSA Syntax Cheat Sheet

## 1. Basic Input / Output

```python
# Single input
n = int(input())

# Multiple integers
a, b, c = map(int, input().split())

# List of integers
arr = list(map(int, input().split()))

# String input
s = input()

# Print
print(n)

# Multiple values
print(a, b, c)

# Print without newline
print(n, end=" ")
```

---

# 2. Variables & Data Types

```python
x = 10              # int
x = 10.5            # float
s = "hello"         # string
flag = True         # boolean
arr = [1, 2, 3]     # list
t = (1, 2, 3)       # tuple
st = {1, 2, 3}      # set
d = {"a": 1}        # dictionary
```

Check type:

```python
type(x)
```

---

# 3. Operators

### Arithmetic

```python
a + b
a - b
a * b
a / b       # float division
a // b      # integer/floor division
a % b       # remainder
a ** b      # power
```

### Comparison

```python
a == b
a != b
a > b
a < b
a >= b
a <= b
```

### Logical

```python
a and b
a or b
not a
```

### Membership

```python
x in arr
x not in arr
```

---

# 4. If / Else

```python
if condition:
    pass
elif condition:
    pass
else:
    pass
```

Example:

```python
if n % 2 == 0:
    print("Even")
else:
    print("Odd")
```

---

# 5. Loops

## For Loop

```python
for i in range(n):
    print(i)
```

```python
for i in range(1, n + 1):
    print(i)
```

```python
for i in range(n - 1, -1, -1):
    print(i)
```

### Step

```python
for i in range(0, n, 2):
    print(i)
```

---

## While Loop

```python
while condition:
    # code
```

Example:

```python
i = 0

while i < n:
    print(i)
    i += 1
```

---

# 6. Break / Continue

```python
for i in range(10):

    if i == 5:
        break
```

```python
for i in range(10):

    if i % 2 == 0:
        continue

    print(i)
```

---

# 7. Lists / Arrays

```python
arr = [10, 20, 30, 40]
```

### Access

```python
arr[0]
arr[-1]
```

### Modify

```python
arr[0] = 100
```

### Add

```python
arr.append(50)
```

### Insert

```python
arr.insert(1, 99)
```

### Remove

```python
arr.remove(20)
```

```python
arr.pop()
```

```python
arr.pop(2)
```

### Length

```python
len(arr)
```

### Check existence

```python
if x in arr:
    print("Found")
```

---

# 8. List Slicing

```python
arr[start:end]
```

Example:

```python
arr[1:4]
```

Reverse:

```python
arr[::-1]
```

Copy:

```python
new_arr = arr[:]
```

---

# 9. Iterating Through Arrays

### Values

```python
for x in arr:
    print(x)
```

### Index

```python
for i in range(len(arr)):
    print(i, arr[i])
```

### Index + Value

Very useful in DSA:

```python
for i, x in enumerate(arr):
    print(i, x)
```

Start index:

```python
for i, x in enumerate(arr, start=1):
    print(i, x)
```

---

# 10. List Comprehension

```python
arr = [x for x in range(10)]
```

With condition:

```python
even = [x for x in arr if x % 2 == 0]
```

Transformation:

```python
squares = [x * x for x in arr]
```

---

# 11. Sorting

### Ascending

```python
arr.sort()
```

### Descending

```python
arr.sort(reverse=True)
```

### Create new sorted list

```python
new_arr = sorted(arr)
```

```python
new_arr = sorted(arr, reverse=True)
```

---

# 12. Sorting With Key

Very important for DSA.

```python
arr.sort(key=lambda x: x[1])
```

Example:

```python
arr = [(1, 5), (2, 3), (3, 8)]

arr.sort(key=lambda x: x[1])
```

Sort descending based on second element:

```python
arr.sort(key=lambda x: x[1], reverse=True)
```

---

# 13. Lambda Function

```python
lambda x: x * 2
```

Example:

```python
square = lambda x: x * x
```

With sorting:

```python
arr.sort(key=lambda x: x[0])
```

---

# 14. Strings

```python
s = "hello"
```

Access:

```python
s[0]
s[-1]
```

Length:

```python
len(s)
```

Slicing:

```python
s[1:4]
```

Reverse:

```python
s[::-1]
```

---

# 15. Useful String Methods

```python
s.lower()
s.upper()
s.strip()
s.split()
s.replace("a", "b")
s.startswith("a")
s.endswith("z")
```

Check:

```python
s.isalpha()
s.isdigit()
s.isalnum()
```

---

# 16. String ↔ List

String to list:

```python
arr = list(s)
```

String split:

```python
words = s.split()
```

List to string:

```python
s = "".join(arr)
```

With spaces:

```python
s = " ".join(words)
```

---

# 17. Tuple

```python
t = (1, 2, 3)
```

Access:

```python
t[0]
```

Unpacking:

```python
a, b = (10, 20)
```

---

# 18. Set

Useful for **unique elements and O(1) average lookup**.

```python
s = set()
```

Add:

```python
s.add(x)
```

Remove:

```python
s.remove(x)
```

Safer removal:

```python
s.discard(x)
```

Check:

```python
if x in s:
    print("Found")
```

---

# 19. Dictionary / HashMap

```python
freq = {}
```

Add/update:

```python
freq[x] = freq.get(x, 0) + 1
```

Check:

```python
if x in freq:
    print("Found")
```

Get:

```python
freq.get(x, 0)
```

Delete:

```python
del freq[x]
```

---

# 20. Dictionary Iteration

Keys:

```python
for key in freq:
    print(key)
```

Values:

```python
for value in freq.values():
    print(value)
```

Key + Value:

```python
for key, value in freq.items():
    print(key, value)
```

---

# 21. Counter

Extremely useful for frequency problems.

```python
from collections import Counter

freq = Counter(arr)
```

Example:

```python
arr = [1, 2, 2, 3, 3, 3]

freq = Counter(arr)

print(freq)
```

Get frequency:

```python
freq[3]
```

Most common:

```python
freq.most_common()
```

---

# 22. defaultdict

Useful when building groups/lists.

```python
from collections import defaultdict

d = defaultdict(list)

d[key].append(value)
```

For integer frequency:

```python
d = defaultdict(int)

d[x] += 1
```

---

# 23. Stack

Python list can work as a stack.

```python
stack = []
```

Push:

```python
stack.append(x)
```

Pop:

```python
x = stack.pop()
```

Top:

```python
stack[-1]
```

Empty:

```python
if not stack:
    print("Empty")
```

---

# 24. Queue

Use `deque`.

```python
from collections import deque

q = deque()
```

Add:

```python
q.append(x)
```

Remove:

```python
x = q.popleft()
```

Front:

```python
q[0]
```

---

# 25. Deque

Can add/remove from both sides.

```python
from collections import deque

dq = deque()

dq.append(10)
dq.appendleft(20)

dq.pop()
dq.popleft()
```

---

# 26. Heap / Priority Queue

Python provides a **min heap**.

```python
import heapq

heap = []
```

Push:

```python
heapq.heappush(heap, x)
```

Pop minimum:

```python
x = heapq.heappop(heap)
```

Minimum:

```python
heap[0]
```

---

# 27. Max Heap

Python doesn't directly provide a max heap.

Use negative values:

```python
heap = []

heapq.heappush(heap, -x)

max_value = -heapq.heappop(heap)
```

---

# 28. Heap With Tuples

Very useful for Dijkstra, scheduling, etc.

```python
heapq.heappush(heap, (distance, node))
```

Pop:

```python
distance, node = heapq.heappop(heap)
```

Python compares the first element first.

---

# 29. Functions

```python
def function_name():
    pass
```

With parameters:

```python
def add(a, b):
    return a + b
```

Call:

```python
result = add(10, 20)
```

---

# 30. Recursion

Basic:

```python
def solve(n):

    if n == 0:
        return

    solve(n - 1)
```

Return recursion:

```python
def factorial(n):

    if n == 0:
        return 1

    return n * factorial(n - 1)
```

---

# 31. Multiple Return Values

```python
def get_values():
    return 10, 20
```

```python
a, b = get_values()
```

---

# 32. Two Pointer

Common pattern:

```python
left = 0
right = len(arr) - 1

while left < right:

    if condition:
        left += 1

    elif condition:
        right -= 1

    else:
        left += 1
        right -= 1
```

---

# 33. Sliding Window

Basic:

```python
left = 0

for right in range(len(arr)):

    # Add arr[right]

    while condition:

        # Remove arr[left]
        left += 1
```

Fixed-size window:

```python
window_sum = 0

for i in range(len(arr)):

    window_sum += arr[i]

    if i >= k:
        window_sum -= arr[i - k]
```

---

# 34. Prefix Sum

```python
prefix = [0] * (len(arr) + 1)

for i in range(len(arr)):
    prefix[i + 1] = prefix[i] + arr[i]
```

Range sum `[l, r]`:

```python
range_sum = prefix[r + 1] - prefix[l]
```

---

# 35. Binary Search

Basic:

```python
left = 0
right = len(arr) - 1

while left <= right:

    mid = (left + right) // 2

    if arr[mid] == target:
        return mid

    elif arr[mid] < target:
        left = mid + 1

    else:
        right = mid - 1

return -1
```

---

# 36. Python Built-in Binary Search

```python
import bisect
```

First position `>= target`:

```python
idx = bisect.bisect_left(arr, target)
```

First position `> target`:

```python
idx = bisect.bisect_right(arr, target)
```

---

# 37. Matrix / 2D Array

Create:

```python
matrix = [[0] * cols for _ in range(rows)]
```

⚠️ Avoid:

```python
matrix = [[0] * cols] * rows
```

because rows reference the same list.

Access:

```python
matrix[i][j]
```

Traverse:

```python
for i in range(rows):
    for j in range(cols):
        print(matrix[i][j])
```

---

# 38. Matrix Directions

Very important for grid problems:

```python
directions = [
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1)
]
```

Use:

```python
for dr, dc in directions:

    nr = r + dr
    nc = c + dc
```

Boundary:

```python
if 0 <= nr < rows and 0 <= nc < cols:
    pass
```

---

# 39. BFS

```python
from collections import deque

q = deque([start])
visited = set()

visited.add(start)

while q:

    node = q.popleft()

    for neighbor in graph[node]:

        if neighbor not in visited:

            visited.add(neighbor)
            q.append(neighbor)
```

---

# 40. DFS — Recursive

```python
def dfs(node):

    visited.add(node)

    for neighbor in graph[node]:

        if neighbor not in visited:
            dfs(neighbor)
```

---

# 41. DFS — Iterative

```python
stack = [start]
visited = set()

while stack:

    node = stack.pop()

    if node in visited:
        continue

    visited.add(node)

    for neighbor in graph[node]:
        stack.append(neighbor)
```

---

# 42. Graph Representation

### Adjacency List

```python
graph = [[] for _ in range(n)]
```

Add edge:

```python
graph[u].append(v)
graph[v].append(u)
```

For directed graph:

```python
graph[u].append(v)
```

---

# 43. Weighted Graph

```python
graph = [[] for _ in range(n)]

graph[u].append((v, weight))
```

Traverse:

```python
for neighbor, weight in graph[node]:
    print(neighbor, weight)
```

---

# 44. Dijkstra

Core syntax:

```python
import heapq

dist = [float("inf")] * n
dist[source] = 0

heap = [(0, source)]

while heap:

    distance, node = heapq.heappop(heap)

    if distance > dist[node]:
        continue

    for neighbor, weight in graph[node]:

        new_distance = distance + weight

        if new_distance < dist[neighbor]:

            dist[neighbor] = new_distance

            heapq.heappush(
                heap,
                (new_distance, neighbor)
            )
```

---

# 45. Backtracking

General pattern:

```python
def backtrack(path):

    if condition:
        result.append(path[:])
        return

    for choice in choices:

        # Choose
        path.append(choice)

        # Explore
        backtrack(path)

        # Undo
        path.pop()
```

This pattern is extremely important for:

* Subsets
* Permutations
* Combination Sum
* N-Queens
* Maze problems

---

# 46. Generate Subsets

```python
result = []

def backtrack(index, path):

    if index == len(arr):
        result.append(path[:])
        return

    # Don't take
    backtrack(index + 1, path)

    # Take
    path.append(arr[index])
    backtrack(index + 1, path)
    path.pop()
```

---

# 47. Swap in Array

```python
arr[i], arr[j] = arr[j], arr[i]
```

Very useful in:

* Two pointers
* Sorting
* Permutations
* Partition algorithms

---

# 48. Min / Max

```python
min(arr)
max(arr)
```

Index:

```python
arr.index(min(arr))
```

But remember: `min()` / `max()` takes **O(n)**.

---

# 49. Infinity

```python
float("inf")
```

Negative infinity:

```python
float("-inf")
```

Common in:

```python
minimum = float("inf")
maximum = float("-inf")
```

---

# 50. Any / All

```python
any(condition for x in arr)
```

Example:

```python
if any(x < 0 for x in arr):
    print("Negative exists")
```

All:

```python
if all(x > 0 for x in arr):
    print("All positive")
```

---

# 51. Zip

Combine arrays:

```python
for a, b in zip(arr1, arr2):
    print(a, b)
```

Example:

```python
names = ["A", "B", "C"]
marks = [90, 80, 70]

for name, mark in zip(names, marks):
    print(name, mark)
```

---

# 52. Enumerate

```python
for i, value in enumerate(arr):
    print(i, value)
```

This is preferable to:

```python
for i in range(len(arr)):
    print(i, arr[i])
```

when you need both index and value.

---

# 53. String Character Frequency

```python
from collections import Counter

freq = Counter(s)

for char, count in freq.items():
    print(char, count)
```

---

# 54. Sorting Characters

```python
sorted(s)
```

Returns a list.

Convert back:

```python
"".join(sorted(s))
```

---

# 55. ASCII

```python
ord('a')
```

```python
chr(97)
```

Useful for:

```python
index = ord(char) - ord('a')
```

For lowercase English letters:

```python
freq = [0] * 26

for char in s:
    freq[ord(char) - ord('a')] += 1
```

---

# 56. Fast Input

For very large input:

```python
import sys

input = sys.stdin.readline
```

Then:

```python
n = int(input())
arr = list(map(int, input().split()))
```

---

# 57. Common DSA Template

This is a good template to start most problems:

```python
import sys
from collections import defaultdict, Counter, deque
import heapq
import bisect

input = sys.stdin.readline


def solve():

    n = int(input())
    arr = list(map(int, input().split()))

    # Logic here


if __name__ == "__main__":
    solve()
```

---

# 58. Most Important Patterns to Memorize

For your DSA preparation, **don't try to memorize every syntax equally**. Focus heavily on these:

| Pattern               | Python syntax              |
| --------------------- | -------------------------- |
| Array traversal       | `for x in arr`             |
| Index traversal       | `for i in range(len(arr))` |
| Index + value         | `enumerate(arr)`           |
| HashMap               | `dict`                     |
| Frequency             | `Counter`                  |
| Stack                 | `list + append/pop`        |
| Queue                 | `deque + popleft`          |
| Heap                  | `heapq`                    |
| Two Pointer           | `left/right`               |
| Sliding Window        | `left/right`               |
| Binary Search         | `left/right/mid`           |
| Prefix Sum            | `prefix[i+1]`              |
| BFS                   | `deque`                    |
| DFS                   | recursion/stack            |
| Grid                  | `directions`               |
| Backtracking          | `append → recurse → pop`   |
| Sorting               | `.sort()` / `sorted()`     |
| Binary search library | `bisect`                   |

### ⭐ Your highest-priority syntax

If you're currently building your Python DSA foundation, I'd memorize these first:

```python
for i in range(len(arr)):
```

```python
for i, x in enumerate(arr):
```

```python
arr.append(x)
arr.pop()
```

```python
freq[x] = freq.get(x, 0) + 1
```

```python
from collections import Counter, defaultdict, deque
```

```python
from heapq import heappush, heappop
```

```python
left = 0
right = len(arr) - 1

while left <= right:
    mid = (left + right) // 2
```

```python
while left <= right:
    ...
    left += 1
    right -= 1
```

```python
while right < len(arr):
    ...
    right += 1
```

```python
for dr, dc in directions:
    nr = r + dr
    nc = c + dc
```

```python
path.append(x)
backtrack(...)
path.pop()
```

These patterns cover a **large portion of beginner-to-intermediate DSA problems in Python**.
