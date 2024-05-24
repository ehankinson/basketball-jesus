# mod = 5

# top = 4
# bot = 3
# top_m = 1
# bot_m = 2
# add_or_sub = False
# if add_or_sub:
#     answer = ((bot_m * bot) % mod) + ((top_m * top) % mod)
# else:
#     answer = ((bot_m * bot) % mod) - ((top_m * top) % mod)
# print(answer)




def convert_number(numbers: list[int], multiplier: int, mod: int):
    new_row = []
    for number in numbers:
        if number == 0:
            continue
        mul =  1 / number
        break
    for number in numbers:
        if mod == None:
            new_row.append(number * mul)
        else:
            new_row.append((number * multiplier) % mod)
    return new_row

def sub_rows(rows1: list[int], rows2: list[int], row1_mul: int, row2_mul: int, mod: int):
    new_row = []
    for a, b in zip(rows1, rows2):
        if mod == None:
            new_row.append((row2_mul * b) - (row1_mul * a))
        else:
            new_row.append(((row2_mul * b) - (row1_mul * a)) % mod)
    return new_row

def add_row(rows1: list[int], rows2: list[int], row1_mul: int, row2_mul: int, mod: int):
    new_row = []
    for a, b in zip(rows1, rows2):
        if mod == None:
            new_row.append((row2_mul * b) + (row1_mul * a))
        else:
            new_row.append(((row2_mul * b) + (row1_mul * a)) % mod)
    return new_row


# mod = None
# row = [-6, 0, 5, 7]
# top_m = 11
# print(convert_number(row, top_m, mod))

mod = None
row1 = [0, 4, 10, 86]
row2 = [0, 4, 5, 17]
row1_mul = 1
row2_mul = 1
print(sub_rows(row1, row2, row1_mul, row2_mul, mod))
print(add_row(row1, row2, row1_mul, row2_mul, mod))