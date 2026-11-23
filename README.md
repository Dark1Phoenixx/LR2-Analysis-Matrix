# Анализ матрицы — ЛР №1–3

Репозиторий продолжает учебный проект «Анализ матрицы». В ЛР №3 программа проверяет размерности, вычисляет значения `sin(i + j / 2)` для матрицы `n × m` и считает элементы, большие нуля.

## Запуск прежнего интерфейса ЛР №2

```bash
python src/main.py
```

## Запуск интеграции ЛР №3

```bash
python -m src.integration examples/request.json --output response.json
python -m unittest discover -s tests -v
```

Клиент передаёт запрос worker-процессу через JSON-файл. Протокол и mapping описаны в `docs/integration.md`; сценарии проверок — в `docs/integration_test.md`.

## CI/CD

GitHub Actions запускает Flake8, тесты и отчёт coverage при push и pull request. Для тега `v*` после успешного CI собирается ZIP-архив и создаётся GitHub Release.

## Лабораторная работа №4

Вариант 20, тестирование проекта по уровням 1–3. Команды и сценарии
описаны в [плане тестирования](docs/testing.md), показатели приведены
в [метриках](docs/testing_metrics.md). Workflow Matrix testing выполняет
Flake8, регрессионный набор и полный набор unittest с порогом покрытия 75%.
