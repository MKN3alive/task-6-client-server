# Задача №6. Клиент-сервер

**Задача**

Требуется реализовать:

1. Серверный компонент системы управления и исполнения параметрированными функциями:
    1. Система оперирует основным типом объекта - параметрированной функцией вещественных переменных $$y = f(x, \lambda)$$
    2. Объектами функции $f(\cdot, \lambda)$ можно управлять (создание, обновление, запрос, удаление) - CRUD
    3. Можно запрашивать вычисление функций на входных параметрах $x$
    4. Запрос функции позволяет получить ее имя, сигнатуру входа, сигнатуры выхода, набор параметров
    5. Система предоставляет два интерфейса:
        - асинхронный HTTP RESTful API
        - CLI
2. Примеры клиентских приложений, обращающихся к системе через API и через CLI

Мотивация: предложенная задача - прообраз MLOps системы и inference server'а, где модели МО заменены функциями, а операция обучения заменена на обновление функции.

---

## Содержимое проекта

* `server.py` — сервер FastAPI с сохранением функций в `functions.json`
* `cli.py` — клиент через консоль
* `functions.json` — файл для хранения функций (создаётся автоматически)
* `test_api.py` — пример работы через Python API

---

## Виртуальное окружение и зависимости

Все зависимости собраны в requirements.txt

```powershell
#создание виртуалного окружения
python -m venv venv

#linux
source venv/bin/activate
#windows
venv\Scripts\activate

#установка зависимостей
pip install -r requirements.txt
```

---

## Запуск сервера

```powershell
uvicorn server:app --reload
```

Сервер будет доступен по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Swagger UI для тестирования: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Работа через CLI

### Создать функцию

```powershell
python cli.py create --name linear --expr "a*x + b" --param a=2 --param b=1
python cli.py create --name quadratic --expr "a*x**2 + b*x + c" --param a=1 --param b=-2 --param c=1
python cli.py create --name sin_wave --expr "a*math.sin(b*x + c)" --param a=2 --param b=1 --param c=0
```

### Просмотреть список функций

```powershell
python cli.py list
```

### Вычислить функцию

```powershell
python cli.py compute --name linear --x 3
python cli.py compute --name quadratic --x 3
python cli.py compute --name sin_wave --x 1.57
```

### Обновить функцию

```powershell
#обновить выражение
python cli.py update --name linear --expr "a*x*x + b"

#обновить параметры
python cli.py update --name linear --param a=2 --param b=5

#обновить название
python cli.py update --name linear --name-new non_linear
```

### Удалить функцию

```powershell
python cli.py delete --name linear
```

---

## Работа через API (Python)

Пример работы напрямую с сервером через requests (файл `api_test.py`):

```python
import requests

BASE = "http://127.0.0.1:8000"

# Создание функции
data = {
    "name": "quadratic",
    "expression": "a * x**2 + b * x + c",
    "params": {"a":1, "b":-2, "c":1}
}
r = requests.post(f"{BASE}/functions", json=data)
print("Created:", r.json())

# Вычисление функции
r2 = requests.post(f"{BASE}/functions/by-name/quadratic/compute", json={"x": 3})
print("Computed:", r2.json())

# Получение списка функций
r3 = requests.get(f"{BASE}/functions")
print("List:", r3.json())
```

---

## Примечания

* Все функции сохраняются в `functions.json` и будут доступны после перезапуска сервера
* Вход функции всегда один — `x`
* Выход функции всегда один — `y`
* Можно обращаться к функциям по имени или по ID

---

## Пример структуры данных функции

```json
{
  "id": "6ee79f9e-b5c5-420c-b3ff-cd733c53ab7c",
  "name": "linear",
  "expression": "a * x + b",
  "params": {
    "a": 2,
    "b": 1
  },
  "inputs": [
    "x"
  ],
  "outputs": [
    "y"
  ]
}
```

---
