import math


def count_positive_elements(n, m):
    count = 0
    for i in range(n):
        for j in range(m):
            value = math.sin(i + j / 2)
            if value > 0:
                count += 1
    return count


try:
    n = int(input("Введите количество строк n: "))
    m = int(input("Введите количество столбцов m: "))

    if n > 0 and m > 0:
        result = count_positive_elements(n, m)
        print("Количество положительных элементов:", result)
    else:
        print("Размеры матрицы должны быть положительными")
except ValueError:
    print("Ошибка: необходимо вводить целые числа")
