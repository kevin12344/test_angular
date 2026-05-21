from decimal import Decimal, ROUND_HALF_UP

def round_v3(num, decimal):
    str_deci = 1
    for _ in range(decimal):
        str_deci = str_deci / 10
    str_deci = str(str_deci)
    result = Decimal(str(num)).quantize(Decimal(str_deci), rounding=ROUND_HALF_UP)
    return result

if __name__ == '__main__':
    print(round_v3(float(9142.52222), 3))