import pandas as pd
import numpy as np

np.random.seed(42)

n = 50000

combos = [
    "Combo Clásico",
    "Combo BBQ",
    "Combo Doble",
    "Combo Veggie",
    "Combo Perro Sencillo",
    "Combo Perro Especial",
    "Combo Familiar",
    "Combo Infantil",
    "Combo Wrap Pollo",
    "Combo Crispy"
]

categorias = {
    "Combo Clásico":       "Hamburguesa",
    "Combo BBQ":           "Hamburguesa",
    "Combo Doble":         "Hamburguesa",
    "Combo Veggie":        "Hamburguesa",
    "Combo Perro Sencillo":"Perro Caliente",
    "Combo Perro Especial":"Perro Caliente",
    "Combo Familiar":      "Hamburguesa",
    "Combo Infantil":      "Hamburguesa",
    "Combo Wrap Pollo":    "Wrap",
    "Combo Crispy":        "Hamburguesa"
}

precios_base = {
    "Combo Clásico":        16000,
    "Combo BBQ":            18500,
    "Combo Doble":          22000,
    "Combo Veggie":         15000,
    "Combo Perro Sencillo": 12000,
    "Combo Perro Especial": 16500,
    "Combo Familiar":       45000,
    "Combo Infantil":       13000,
    "Combo Wrap Pollo":     17000,
    "Combo Crispy":         19000
}

bebidas    = ["Gaseosa", "Jugo Natural", "Agua", "Limonada", "Té Frío"]
salsas     = ["BBQ", "Mostaza", "Rosada", "Pico de Gallo", "Sin Salsa"]
tamaños    = ["Pequeñas", "Medianas", "Grandes"]
metodos    = ["Efectivo", "Tarjeta", "App"]
sucursales = ["Norte", "Sur", "Centro", "El Lago", "Portal"]
extras     = ["Doble Carne", "Extra Queso", "Sin Cebolla", "Sin Tomate", "Ninguno"]
empleados  = [f"EMP-{str(i).zfill(2)}" for i in range(1, 16)]

fechas = pd.date_range(start="2023-01-01", end="2024-12-31", periods=n)

nombres_combos = np.random.choice(combos, n)

data = {
    "order_id":               np.arange(10001, 10001 + n),
    "fecha":                  fechas.date,
    "hora":                   [f"{np.random.randint(10, 22):02d}:{np.random.choice([0,15,30,45]):02d}" for _ in range(n)],
    "dia_semana":             [pd.Timestamp(f).day_name() for f in fechas],
    "sucursal":               np.random.choice(sucursales, n),
    "combo_id":               [combos.index(c) + 1 for c in nombres_combos],
    "nombre_combo":           nombres_combos,
    "categoria":              [categorias[c] for c in nombres_combos],
    "precio_base":            [precios_base[c] for c in nombres_combos],
    "personalizado":          np.random.choice([True, False], n, p=[0.35, 0.65]),
    "ingrediente_extra":      np.random.choice(extras, n),
    "bebida":                 np.random.choice(bebidas, n),
    "salsa":                  np.random.choice(salsas, n),
    "tamaño_papas":           np.random.choice(tamaños, n, p=[0.2, 0.5, 0.3]),
    "cantidad":               np.random.randint(1, 5, n),
    "metodo_pago":            np.random.choice(metodos, n, p=[0.4, 0.4, 0.2]),
    "tiempo_preparacion_min": np.random.randint(5, 30, n),
    "calificacion":           np.round(np.random.uniform(2.5, 5.0, n), 1),
    "empleado_id":            np.random.choice(empleados, n),
}

df = pd.DataFrame(data)

df["precio_total"] = (
    df["precio_base"] +
    df["personalizado"].astype(int) * np.random.randint(1000, 4000, n)
) * df["cantidad"]

df.to_csv("dataset_restaurante_50k.csv", index=False)

print(f"Dataset generado: {len(df)} filas, {len(df.columns)} columnas")
print(df.head())
print("\nEstadisticas basicas:")
print(df.describe())
