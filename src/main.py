"""Interactive entry point for the matrix analysis project."""

if __package__:
    from .processing_module import count_positive_elements
else:
    from processing_module import count_positive_elements


def main() -> None:
    try:
        n = int(input("Введите количество строк n: "))
        m = int(input("Введите количество столбцов m: "))
    except ValueError:
        print("Ошибка: необходимо вводить целые числа")
        return
    if n > 0 and m > 0:
        result = count_positive_elements(n, m)
        print("Количество положительных элементов:", result)
    else:
        print("Размеры матрицы должны быть положительными")


if __name__ == "__main__":
    main()
