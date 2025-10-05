# manual_test_no_db.py
class Category:
    def __init__(self, name):
        self.name = name

class Item:
    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category

# Создаём данные
food = Category("food")
tech = Category("tech")

items = [
    Item("Apple", 100, food),
    Item("Banana", 50, food),
    Item("Laptop", 1000, tech),
]

# Фильтр
food_items = [i for i in items if i.category.name == "food"]
print("=== Фильтр category=food ===")
for i in food_items:
    print(i.name, i.price, i.category.name)

# Сортировка
print("\n=== Сортировка price ascending ===")
for i in sorted(items, key=lambda x: x.price):
    print(i.name, i.price, i.category.name)
