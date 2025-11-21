def simple_function():
    print("Hello World")

def explicit_split_function():
    x = 1
    y = 2
    # SPLIT
    z = x + y
    print(z)

def long_complex_function():
    results = []
    for i in range(100):
        if i % 2 == 0:
            results.append(i)
        else:
            results.append(i * 2)
            
    # Let's add some filler to make it longer for heuristics
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    
    return sum(results) + a + b
