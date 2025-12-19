import requests

BASE = "http://127.0.0.1:8000"

# --- Создание функции ---
data = {
    "name": "quadratic",
    "expression": "a * x**2 + b * x + c",
    "params": {"a":1, "b":-2, "c":1}
}
r = requests.post(f"{BASE}/functions", json=data)
print("Created:", r.json())

# --- Вычисление функции ---
r2 = requests.post(f"{BASE}/functions/by-name/quadratic/compute", json={"x": 3})
print("Computed:", r2.json())

# --- Получение списка функций ---
r3 = requests.get(f"{BASE}/functions")
print("List:", r3.json())
