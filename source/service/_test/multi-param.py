

def add(*num):
    sum = 0
    for n in num:
        sum += n

    return sum

print(add(1,2,3,4,5,6,7,8,9))

def join(*str):
    str = '-'.join(str)
    print(str)

join('1','2','3')