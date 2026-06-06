"""
Импорт справочника кодов из Excel в базу данных.
"""

import pandas as pd
import sqlite3
import os

# Путь к файлу Excel
excel_path = "Справочник.xlsx"
db_path = "backend/data/ship_load.db"

# Проверяем, существует ли файл
if not os.path.exists(excel_path):
    print(f"Файл {excel_path} не найден!")
    exit(1)

# Читаем Excel
print(f"Чтение файла {excel_path}...")
df = pd.read_excel(excel_path, sheet_name="Справочник")

# Выводим информацию о данных
print(f"Найдено строк: {len(df)}")
print(f"Колонки: {df.columns.tolist()}")

# Подключаемся к БД
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Очищаем таблицу code_directory (опционально)
cursor.execute("DELETE FROM code_directory")
print("Таблица code_directory очищена")

# Вставляем данные
count = 0
for _, row in df.iterrows():
    code = str(row['Код']).strip()
    name = str(row['Наименование']).strip()
    level = int(row['Уровень']) if pd.notna(row['Уровень']) else 0

    # Определяем parent_code (первые 8, 6, 4, 2 знака в зависимости от уровня)
    if level == 1:
        parent_code = None
    elif level == 2:
        parent_code = code[:2] + "00000000"
    elif level == 3:
        parent_code = code[:4] + "000000"
    elif level == 4:
        parent_code = code[:6] + "0000"
    elif level == 5:
        parent_code = code[:8] + "00"
    else:
        parent_code = None

    cursor.execute('''
        INSERT OR REPLACE INTO code_directory (code, name, level, parent_code)
        VALUES (?, ?, ?, ?)
    ''', (code, name, level, parent_code))
    count += 1

conn.commit()
print(f"Импортировано {count} записей")

# Проверка
cursor.execute("SELECT COUNT(*) FROM code_directory")
total = cursor.fetchone()[0]
print(f"Всего записей в БД: {total}")

# Показываем первые 10 записей
cursor.execute(
    "SELECT code, name, level, parent_code FROM code_directory LIMIT 10")
print("\nПервые 10 записей:")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]} | ур.{row[2]} | parent: {row[3]}")

conn.close()
print("Готово!")
