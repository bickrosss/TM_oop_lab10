# -*- coding: utf-8 -*-
"""
Ядро приложения "Учёт питомцев".
Содержит классы данных и логику работы с коллекцией питомцев.
"""

import json
from dataclasses import dataclass, asdict, field
from typing import List, Optional
from pathlib import Path
from enum import Enum


class Species(Enum):
    """Перечисление видов животных."""
    CAT = "кот"
    DOG = "собака"
    BIRD = "птица"
    FISH = "рыба"
    RODENT = "грызун"
    OTHER = "другое"
    
    def __str__(self):
        return self.value


@dataclass
class Pet:
    """Класс для представления питомца."""
    name: str
    species: Species
    age: int
    
    def __post_init__(self):
        """Валидация данных после инициализации."""
        if not self.name.strip():
            raise ValueError("Имя питомца не может быть пустым")
        if self.age < 0:
            raise ValueError("Возраст не может быть отрицательным")
        if self.age > 100:
            raise ValueError("Возраст слишком большой")


@dataclass
class PetContainer:
    """Контейнер для управления коллекцией питомцев."""
    pets: List[Pet] = field(default_factory=list)
    
    def add_pet(self, name: str, species_str: str, age: int) -> Pet:
        """
        Добавить нового питомца.
        
        Args:
            name: Кличка питомца
            species_str: Вид животного
            age: Возраст в годах
            
        Returns:
            Pet: Созданный объект питомца
            
        Raises:
            ValueError: При некорректных данных
        """
        try:
            # Конвертируем строку в Species Enum
            species = Species[species_str.upper().replace(" ", "_")]
        except KeyError:
            # Если вид не найден в Enum, используем OTHER
            species = Species.OTHER
        
        pet = Pet(name=name, species=species, age=age)
        self.pets.append(pet)
        return pet
    
    def show_all(self) -> str:
        """
        Получить форматированное представление всех питомцев.
        
        Returns:
            str: Отформатированная строка со списком питомцев
        """
        if not self.pets:
            return "Список питомцев пуст."
        
        result = ["\nСписок всех питомцев:", "-" * 40]
        for i, pet in enumerate(self.pets, 1):
            result.append(f"{i}. {pet.name} - {pet.species}, {pet.age} лет")
        result.extend(["-" * 40, f"Всего: {len(self.pets)} питомцев"])
        return "\n".join(result)
    
    def find_by_species(self, species_str: str) -> List[Pet]:
        """
        Найти питомцев по виду.
        
        Args:
            species_str: Вид животного для поиска
            
        Returns:
            List[Pet]: Список найденных питомцев
        """
        try:
            species = Species[species_str.upper().replace(" ", "_")]
        except KeyError:
            # Если вид не найден, возвращаем пустой список
            return []
        
        return [pet for pet in self.pets if pet.species == species]
    
    def sort_by_age(self, reverse: bool = False) -> None:
        """Сортировать питомцев по возрасту."""
        self.pets.sort(key=lambda pet: pet.age, reverse=reverse)
    
    def sort_by_name(self) -> None:
        """Сортировать питомцев по имени."""
        self.pets.sort(key=lambda pet: pet.name)
    
    def save_to_file(self, filename: str) -> None:
        """
        Сохранить данные в JSON файл.
        
        Args:
            filename: Имя файла для сохранения
            
        Raises:
            IOError: При ошибке записи в файл
        """
        # Конвертируем Enum в строки для сериализации
        data = []
        for pet in self.pets:
            pet_dict = asdict(pet)
            pet_dict['species'] = pet.species.name  # Сохраняем имя Enum
            data.append(pet_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        """
        Загрузить данные из JSON файла.
        
        Args:
            filename: Имя файла для загрузки
            
        Raises:
            FileNotFoundError: Если файл не существует
            JSONDecodeError: Если файл содержит некорректный JSON
        """
        if not Path(filename).exists():
            raise FileNotFoundError(f"Файл {filename} не существует")
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.pets = []
        for pet_data in data:
            # Конвертируем строку обратно в Species Enum
            species_name = pet_data.get('species', 'OTHER')
            try:
                species = Species[species_name]
            except KeyError:
                species = Species.OTHER
            
            self.pets.append(Pet(
                name=pet_data['name'],
                species=species,
                age=pet_data['age']
            ))
    
    def get_statistics(self) -> dict:
        """
        Получить статистику по питомцам.
        
        Returns:
            dict: Статистика (общее количество, по видам, средний возраст)
        """
        if not self.pets:
            return {"total": 0}
        
        stats = {
            "total": len(self.pets),
            "by_species": {},
            "average_age": sum(pet.age for pet in self.pets) / len(self.pets)
        }
        
        for pet in self.pets:
            species_name = pet.species.name
            stats["by_species"][species_name] = stats["by_species"].get(species_name, 0) + 1
        
        return stats
