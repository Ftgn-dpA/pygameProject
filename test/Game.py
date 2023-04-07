while True:
    try:
        n = int(input())
        a = {}
        tmp = input().split()
        for i in range(n):
            a[int(tmp[i])] = 1
        m = int(input())
        b = [0] * m
        for i in range(m):
            b[i] = int(input())
        for q in b:
            if q in a.keys():
                print('YES')
            else:
                print('NO')
    except EOFError:
        break
