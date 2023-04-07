def fibonacci(n: int) -> int:
    f = [1, 1]
    while n > 2:
        f[n % 2 - 1] = sum(f)
        n -= 1

    return f[n % 2]


i = int(input())
print(fibonacci(i - 1) * fibonacci(i + 1) - fibonacci(i) * fibonacci(i))
