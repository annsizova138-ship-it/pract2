# dep-graph - граф зависимостей пакетов Ubuntu (вариант 20)

## 1. Общее описание

Инструмент командной строки для анализа и визуализации графа зависимостей
пакетов менеджера пакетов apt (Ubuntu). Готовые менеджеры пакетов и
библиотеки для получения зависимостей не используются: данные берутся из
индекса репозитория и разбираются самостоятельно.

Выполнен **этап 1 - минимальный прототип с конфигурацией**: приложение
принимает параметры командной строки, проверяет их и при запуске выводит
все заданные значения в формате «ключ: значение».

## 2. Описание всех функций и настроек

Источник настроек - только параметры командной строки.

| Параметр | Описание | По умолчанию |
|---|---|---|
| `--package ИМЯ` | имя анализируемого пакета (обязательный). В режиме `url` - как в apt: строчные латинские буквы, цифры, `+ . -`; в режиме `test` - большие латинские буквы | - |
| `--repo ПУТЬ` | URL репозитория (`http://` или `https://`) или путь к файлу тестового репозитория (обязательный) | - |
| `--repo-mode РЕЖИМ` | `url` - настоящий репозиторий, `test` - файл тестового репозитория | `url` |
| `--ascii-tree` | флаг: вывести зависимости в виде ASCII-дерева (появится на этапе 5) | выключен |
| `--max-depth N` | максимальная глубина анализа, целое число не меньше 1 (используется с этапа 3) | 3 |
| `--filter ПОДСТРОКА` | не учитывать пакеты, в имени которых есть подстрока (без пробелов) (используется с этапа 3) | не задана |

Все параметры проверяются до начала работы. Ошибки выводятся в stderr в
виде `Ошибка параметров: ...`, программа завершается с кодом 2:

- не задан `--package` или `--repo`;
- недопустимое имя пакета для выбранного режима;
- `--repo-mode` не равен `url` или `test`;
- в режиме `url` адрес не начинается с `http://` или `https://`;
- в режиме `test` файл не найден;
- `--max-depth` - не целое число или меньше 1;
- `--filter` содержит пробелы;
- неизвестная опция.

Коды завершения: `0` - успех, `1` - ошибка работы (репозиторий недоступен,
пакет не найден, граф или изображение построить не удалось), `2` - ошибка
параметров командной строки.

## 3. Команды для сборки проекта и запуска тестов

Сборка не требуется. Нужен Python 3 (разработано на версии 3.10); сторонние
библиотеки не нужны, используется только стандартная библиотека.

Запуск тестов (из корня репозитория):

```
# Windows
scripts\run_tests.bat

# Linux / macOS / Git Bash
PYTHONPATH=src python3 -m unittest discover tests
```

Запуск приложения (из корня репозитория):

```
python src/main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz
```

## 4. Примеры использования

Запуск с параметрами (все значения выводятся при старте):

```
python src/main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 5 --filter lib
```

```
package: curl
repo: http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz
repo-mode: url
ascii-tree: false
max-depth: 5
filter: lib
```

Обработка ошибок (по одному запуску для каждого параметра):

```
python src/main.py --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz
Ошибка параметров: не задано имя пакета (--package)   (код 2)

python src/main.py --package Curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz
Ошибка параметров: недопустимое имя пакета 'Curl' (нужны: строчные латинские буквы, цифры, + . -)   (код 2)

python src/main.py --package curl --repo ftp://example.org/Packages
Ошибка параметров: некорректный URL репозитория: ftp://example.org/Packages   (код 2)

python src/main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --repo-mode x
Ошибка параметров: неизвестный режим 'x', допустимо: url или test   (код 2)

python src/main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth abc
Ошибка параметров: глубина должна быть целым числом, получено 'abc'   (код 2)

python src/main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --max-depth 0
Ошибка параметров: глубина должна быть не меньше 1   (код 2)

python src/main.py --package curl --repo http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz --filter "a b"
Ошибка параметров: подстрока фильтра не должна содержать пробелов   (код 2)

python src/main.py --package A --repo no_such.txt --repo-mode test
Ошибка параметров: файл тестового репозитория не найден: no_such.txt   (код 2)
```
