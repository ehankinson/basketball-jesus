def intToRoman(num: int) -> str:
    return_string = ""
    check_num(num, return_string, "M", 1000)
    check_num(num, return_string, "D", 500)
    check_num(num, return_string, "C", 500)
    check_num(num, return_string, "L", 500)
    check_num(num, return_string, "X", 500)
    check_num(num, return_string, "V", 500)
    check_num(num, return_string, "I", 500)
    return return_string
                

def check_num(num: int, number_string: str, letter: str, amount_to_check: int):
    if num % amount_to_check == 0:
        for _ in range(num / amount_to_check):
            number_string += letter
    elif num > amount_to_check:
        for _ in range(int(num / amount_to_check)):
            number_string += letter
            num -= amount_to_check

num = 3729
