import dis

def test():
    x = 1
    y = 2
    return x + y

dis.dis(test)
