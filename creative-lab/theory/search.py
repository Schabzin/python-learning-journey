def linear_search(items, target):
    steps = 0
    for position, item in enumerate(items):
        steps += 1
        if item == target:
            return position, steps
    return -1, steps


def binary_search(items, target):
    low = 0
    high = len(items) - 1
    steps = 0
    while low <= high:
        steps += 1
        middle = (low + high) // 2
        if items[middle] == target:
            return middle, steps
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1, steps


def worst_case(n):
    items = list(range(0, n * 2, 2))
    target = n * 2
    _, linear_steps = linear_search(items, target)
    _, binary_steps = binary_search(items, target)
    return linear_steps, binary_steps


if __name__ == "__main__":
    items = list(range(0, 2000, 2))
    for position, value in enumerate(items):
        assert binary_search(items, value)[0] == position
    assert binary_search(items, 7)[0] == -1
    print("binary_search agrees with every position")

    for n in (10, 1_000, 1_000_000):
        linear_steps, binary_steps = worst_case(n)
        print(f"{n:>9,} items: linear {linear_steps:>9,} looks, binary {binary_steps:>2} looks")