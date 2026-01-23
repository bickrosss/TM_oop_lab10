#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивная версия приложения "Учёт питомцев".
Предоставляет меню для взаимодействия с пользователем.
"""

import os
import sys
from pets_core import PetContainer, Species


class InteractivePetCLI:
    """Интерактивный интерфейс для управления питомцами."""
    
    def __init__(self):
        self.container = PetContainer()
        self.default_file = "pets.json"
    
    def load_default_file(self):
        """Загрузить данные из файла по умолчанию, если он существует."""
        if os.path.exists(self.default_file):
            try:
                self.container.load_from_file(self.default_file)
                print(f"✓ Загружено {len(self.container.pets)} питомцев из {self.default_file}")
            except Exception as e:
                print(f"✗ Ошибка при загрузке: {e}")
    
    def print_menu(self):
        """Вывести меню команд."""
        print("\n" + "=" * 50)
        print("СИСТЕМА УЧЁТА ПИТОМЦЕВ")
        print("=" * 50)
        print("1. Добавить питомца")
        print("2. Показать всех питомцев")
        print("3. Найти питомцев по виду")
        print("4. Отсортировать питомцев")
        print("5. Показать статистику")
        print("6. Сохранить данные")
        print("7. Загрузить данные")
        print("8. Выйти")
        print("=" * 50)
    
    def add_pet_interactive(self):
        """Интерактивное добавление питомца."""
        print("\n--- Добавление питомца ---")
        
        name = input("Кличка питомца: ").strip()
        if not name:
            print("✗ Кличка не может быть пустой")
            return
        
        print("Доступные виды:", ", ".join([s.name.lower() for s in Species]))
        species_input = input("Вид животного: ").strip().upper()
        
        try:
            age = int(input("Возраст (лет): "))
        except ValueError:
            print("✗ Возраст должен быть числом")
            return
        
        try:
            pet = self.container.add_pet(name, species_input, age)
            print(f"✓ Добавлен питомец: {pet.name} ({pet.species}, {pet.age} лет)")
        except Exception as e:
            print(f"✗ Ошибка: {e}")
    
    def find_pets_interactive(self):
        """Интерактивный поиск питомцев по виду."""
        print("\n--- Поиск питомцев ---")
        print("Доступные виды:", ", ".join([s.name.lower() for s in Species]))
        
        species_input = input("Введите вид для поиска: ").strip().upper()
        found = self.container.find_by_species(species_input)
        
        if not found:
            print(f"✗ Питомцы вида '{species_input.lower()}' не найдены")
            return
        
        print(f"\nНайдено {len(found)} питомцев:")
        print("-" * 40)
        for i, pet in enumerate(found, 1):
            print(f"{i}. {pet.name}, {pet.age} лет")
        print("-" * 40)
    
    def sort_pets_interactive(self):
        """Интерактивная сортировка питомцев."""
        print("\n--- Сортировка питомцев ---")
        print("1. По имени (А-Я)")
        print("2. По возрасту (младшие сначала)")
        print("3. По возрасту (старшие сначала)")
        
        choice = input("Выберите вариант сортировки: ").strip()
        
        if choice == "1":
            self.container.sort_by_name()
            print("✓ Питомцы отсортированы по имени")
        elif choice == "2":
            self.container.sort_by_age(reverse=False)
            print("✓ Питомцы отсортированы по возрасту (младшие сначала)")
        elif choice == "3":
            self.container.sort_by_age(reverse=True)
            print("✓ Питомцы отсортированы по возрасту (старшие сначала)")
        else:
            print("✗ Неверный выбор")
    
    def show_statistics(self):
        """Показать статистику по питомцам."""
        stats = self.container.get_statistics()
        
        print("\n--- Статистика ---")
        print(f"Всего питомцев: {stats['total']}")
        
        if stats['total'] > 0:
            print(f"Средний возраст: {stats['average_age']:.1f} лет")
            print("\nРаспределение по видам:")
            for species, count in stats['by_species'].items():
                species_name = Species[species].value
                print(f"  {species_name}: {count}")
    
    def save_data_interactive(self):
        """Интерактивное сохранение данных."""
        filename = input(f"Имя файла [{self.default_file}]: ").strip() or self.default_file
        
        try:
            self.container.save_to_file(filename)
            print(f"✓ Данные сохранены в {filename}")
        except Exception as e:
            print(f"✗ Ошибка при сохранении: {e}")
    
    def load_data_interactive(self):
        """Интерактивная загрузка данных."""
        filename = input(f"Имя файла [{self.default_file}]: ").strip() or self.default_file
        
        try:
            self.container.load_from_file(filename)
            print(f"✓ Загружено {len(self.container.pets)} питомцев из {filename}")
        except FileNotFoundError:
            print(f"✗ Файл {filename} не существует")
        except Exception as e:
            print(f"✗ Ошибка при загрузке: {e}")
    
    def run(self):
        """Запустить интерактивный интерфейс."""
        self.load_default_file()
        
        while True:
            self.print_menu()
            
            try:
                choice = input("\nВыберите действие (1-8): ").strip()
                
                if choice == "1":
                    self.add_pet_interactive()
                elif choice == "2":
                    print(self.container.show_all())
                elif choice == "3":
                    self.find_pets_interactive()
                elif choice == "4":
                    self.sort_pets_interactive()
                elif choice == "5":
                    self.show_statistics()
                elif choice == "6":
                    self.save_data_interactive()
                elif choice == "7":
                    self.load_data_interactive()
                elif choice == "8":
                    # Автосохранение перед выходом
                    if self.container.pets:
                        save_choice = input("Сохранить данные перед выходом? (y/n): ").lower()
                        if save_choice == 'y':
                            self.container.save_to_file(self.default_file)
                            print(f"✓ Данные сохранены в {self.default_file}")
                    print("До свидания!")
                    break
                else:
                    print("✗ Неверный выбор. Введите число от 1 до 8.")
            
            except KeyboardInterrupt:
                print("\n\nПрограмма прервана пользователем.")
                break
            except Exception as e:
                print(f"✗ Неожиданная ошибка: {e}")


def main():
    """Основная функция запуска интерактивной версии."""
    cli = InteractivePetCLI()
    cli.run()


if __name__ == "__main__":
    main()