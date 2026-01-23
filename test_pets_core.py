#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import pytest
import json
from pets_core import Species, Pet, PetContainer


class TestSpecies:
    """Тесты для перечисления Species."""
    
    def test_species_values(self):
        """Проверка значений видов животных."""
        assert Species.CAT.value == "кот"
        assert Species.DOG.value == "собака"
        assert Species.BIRD.value == "птица"
        assert Species.FISH.value == "рыба"
        assert Species.RODENT.value == "грызун"
        assert Species.OTHER.value == "другое"
    
    def test_species_str(self):
        """Проверка строкового представления."""
        assert str(Species.CAT) == "кот"
        assert str(Species.DOG) == "собака"
        assert str(Species.BIRD) == "птица"
    
    def test_species_from_string_valid(self):
        """Проверка конвертации строки в Species (валидные значения)."""
        assert Species.from_string("cat") == Species.CAT
        assert Species.from_string("DOG") == Species.DOG
        assert Species.from_string("Bird") == Species.BIRD
    
    def test_species_from_string_invalid(self):
        """Проверка конвертации строки в Species (невалидные значения)."""
        with pytest.raises(ValueError):
            Species.from_string("invalid_species")
        with pytest.raises(ValueError):
            Species.from_string("")


class TestPet:
    """Тесты для класса Pet."""
    
    def test_pet_creation(self):
        """Создание объекта Pet с валидными данными."""
        pet = Pet(name="Барсик", species=Species.CAT, age=3)
        assert pet.name == "Барсик"
        assert pet.species == Species.CAT
        assert pet.age == 3
    
    def test_pet_creation_with_spaces(self):
        """Создание Pet с пробелами в имени."""
        pet = Pet(name="  Барсик  ", species=Species.DOG, age=5)
        assert pet.name == "  Барсик  "
    
    def test_pet_invalid_name(self):
        """Создание Pet с пустым именем."""
        with pytest.raises(ValueError):
            Pet(name="", species=Species.CAT, age=3)
        with pytest.raises(ValueError):
            Pet(name="   ", species=Species.CAT, age=3)
    
    def test_pet_invalid_age_negative(self):
        """Создание Pet с отрицательным возрастом."""
        with pytest.raises(ValueError):
            Pet(name="Барсик", species=Species.CAT, age=-1)
    
    def test_pet_invalid_age_too_large(self):
        """Создание Pet со слишком большим возрастом."""
        with pytest.raises(ValueError):
            Pet(name="Барсик", species=Species.CAT, age=150)
    
    def test_pet_age_boundary(self):
        """Проверка граничных значений возраста."""
        # Минимальный возраст
        pet1 = Pet(name="Малыш", species=Species.CAT, age=0)
        assert pet1.age == 0
        
        # Максимальный возраст
        pet2 = Pet(name="Старик", species=Species.DOG, age=100)
        assert pet2.age == 100
    
    def test_pet_equality(self):
        """Проверка равенства объектов Pet."""
        pet1 = Pet(name="Барсик", species=Species.CAT, age=3)
        pet2 = Pet(name="Барсик", species=Species.CAT, age=3)
        pet3 = Pet(name="Мурка", species=Species.CAT, age=3)
        
        # Два одинаковых питомца
        assert pet1 == pet2
        
        # Разные питомцы
        assert pet1 != pet3


class TestPetContainer:
    """Тесты для класса PetContainer."""
    
    def test_empty_creation(self):
        """Создание пустого контейнера."""
        container = PetContainer()
        assert len(container.pets) == 0
        assert container.pets == []
    
    def test_creation_with_pets(self):
        """Создание контейнера с начальным списком питомцев."""
        pets = [
            Pet(name="Барсик", species=Species.CAT, age=3),
            Pet(name="Шарик", species=Species.DOG, age=5)
        ]
        container = PetContainer(pets=pets)
        assert len(container.pets) == 2
    
    def test_add_pet_valid(self):
        """Добавление питомца с валидными данными."""
        container = PetContainer()
        pet = container.add_pet("Барсик", "CAT", 3)
        
        assert len(container.pets) == 1
        assert pet.name == "Барсик"
        assert pet.species == Species.CAT
        assert pet.age == 3
        assert container.pets[0] == pet
    
    def test_add_pet_case_insensitive(self):
        """Добавление питомца с разным регистром."""
        container = PetContainer()
        
        # Разные варианты написания
        container.add_pet("Барсик", "cat", 3)
        container.add_pet("Шарик", "Dog", 5)
        container.add_pet("Кеша", "BIRD", 2)
        
        assert len(container.pets) == 3
        assert container.pets[0].species == Species.CAT
        assert container.pets[1].species == Species.DOG
        assert container.pets[2].species == Species.BIRD
    
    def test_add_pet_unknown_species(self):
        """Добавление питомца с неизвестным видом."""
        container = PetContainer()
        pet = container.add_pet("Экзотик", "unknown_species", 2)
        
        assert pet.species == Species.OTHER
        assert len(container.pets) == 1
    
    def test_add_multiple_pets(self):
        """Добавление нескольких питомцев."""
        container = PetContainer()
        
        container.add_pet("Барсик", "CAT", 3)
        container.add_pet("Шарик", "DOG", 5)
        container.add_pet("Мурка", "CAT", 2)
        
        assert len(container.pets) == 3
        assert container.pets[0].name == "Барсик"
        assert container.pets[1].name == "Шарик"
        assert container.pets[2].name == "Мурка"
    
    def test_show_all_empty(self):
        """Показ пустого списка питомцев."""
        container = PetContainer()
        result = container.show_all()
        
        assert result == "Список питомцев пуст."
        assert "Список питомцев пуст" in result
    
    def test_show_all_with_pets(self):
        """Показ списка с питомцами."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        container.add_pet("Шарик", "DOG", 5)
        
        result = container.show_all()
        
        assert "Список всех питомцев" in result
        assert "Барсик" in result
        assert "Шарик" in result
        assert "Всего: 2 питомцев" in result
    
    def test_find_by_species_found(self):
        """Поиск питомцев по виду (найдены)."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        container.add_pet("Мурка", "CAT", 2)
        container.add_pet("Шарик", "DOG", 5)
        
        found = container.find_by_species("CAT")
        
        assert len(found) == 2
        assert all(pet.species == Species.CAT for pet in found)
        assert found[0].name == "Барсик"
        assert found[1].name == "Мурка"
    
    def test_find_by_species_not_found(self):
        """Поиск питомцев по виду (не найдены)."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        
        found = container.find_by_species("DOG")
        
        assert len(found) == 0
        assert found == []
    
    def test_find_by_species_case_insensitive(self):
        """Поиск питомцев с разным регистром."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        
        # Разные варианты поиска
        found1 = container.find_by_species("cat")
        found2 = container.find_by_species("Cat")
        found3 = container.find_by_species("CAT")
        
        assert len(found1) == 1
        assert len(found2) == 1
        assert len(found3) == 1
        assert found1[0].name == "Барсик"
    
    def test_find_by_species_unknown(self):
        """Поиск питомцев по неизвестному виду."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        
        found = container.find_by_species("UNKNOWN")
        
        assert len(found) == 0
    
    def test_sort_by_age_ascending(self):
        """Сортировка питомцев по возрасту (по возрастанию)."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 5)
        container.add_pet("Шарик", "DOG", 3)
        container.add_pet("Мурка", "CAT", 7)
        
        container.sort_by_age(reverse=False)
        
        assert container.pets[0].age == 3
        assert container.pets[1].age == 5
        assert container.pets[2].age == 7
        assert container.pets[0].name == "Шарик"
    
    def test_sort_by_age_descending(self):
        """Сортировка питомцев по возрасту (по убыванию)."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 5)
        container.add_pet("Шарик", "DOG", 3)
        container.add_pet("Мурка", "CAT", 7)
        
        container.sort_by_age(reverse=True)
        
        assert container.pets[0].age == 7
        assert container.pets[1].age == 5
        assert container.pets[2].age == 3
        assert container.pets[0].name == "Мурка"
    
    def test_sort_by_name(self):
        """Сортировка питомцев по имени."""
        container = PetContainer()
        container.add_pet("Шарик", "DOG", 5)
        container.add_pet("Барсик", "CAT", 3)
        container.add_pet("Альфа", "DOG", 7)
        
        container.sort_by_name()
        
        assert container.pets[0].name == "Альфа"
        assert container.pets[1].name == "Барсик"
        assert container.pets[2].name == "Шарик"
    
    def test_save_and_load_empty(self):
        """Сохранение и загрузка пустого контейнера."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "pets.json")
            
            container1 = PetContainer()
            container1.save_to_file(filename)
            
            # Проверка, что файл создан
            assert os.path.exists(filename)
            
            # Проверка содержимого файла
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data == []
            
            # Загрузка из файла
            container2 = PetContainer()
            container2.load_from_file(filename)
            
            assert len(container2.pets) == 0
    
    def test_save_and_load_with_pets(self):
        """Сохранение и загрузка контейнера с питомцами."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "pets.json")
            
            # Создание и сохранение
            container1 = PetContainer()
            container1.add_pet("Барсик", "CAT", 3)
            container1.add_pet("Шарик", "DOG", 5)
            container1.save_to_file(filename)
            
            # Проверка файла
            assert os.path.exists(filename)
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert len(data) == 2
                assert data[0]['name'] == "Барсик"
                assert data[0]['species'] == "CAT"
                assert data[0]['age'] == 3
            
            # Загрузка и проверка
            container2 = PetContainer()
            container2.load_from_file(filename)
            
            assert len(container2.pets) == 2
            assert container2.pets[0].name == "Барсик"
            assert container2.pets[0].species == Species.CAT
            assert container2.pets[0].age == 3
            assert container2.pets[1].name == "Шарик"
            assert container2.pets[1].species == Species.DOG
    
    def test_save_creates_file(self):
        """Проверка, что сохранение создает файл."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test.json")
            container = PetContainer()
            container.add_pet("Тест", "CAT", 1)
            container.save_to_file(filename)
            
            assert os.path.exists(filename)
            assert os.path.getsize(filename) > 0
    
    def test_load_nonexistent_file(self):
        """Загрузка из несуществующего файла."""
        container = PetContainer()
        with pytest.raises(FileNotFoundError):
            container.load_from_file("nonexistent.json")
    
    def test_load_invalid_json(self):
        """Загрузка из файла с некорректным JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "invalid.json")
            
            # Создаем файл с некорректным JSON
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Это не JSON")
            
            container = PetContainer()
            with pytest.raises(json.JSONDecodeError):
                container.load_from_file(filename)
    
    def test_get_statistics_empty(self):
        """Получение статистики для пустого контейнера."""
        container = PetContainer()
        stats = container.get_statistics()
        
        assert stats['total'] == 0
        assert 'average_age' not in stats
        assert 'by_species' not in stats
    
    def test_get_statistics_with_pets(self):
        """Получение статистики для контейнера с питомцами."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        container.add_pet("Мурка", "CAT", 5)
        container.add_pet("Шарик", "DOG", 4)
        container.add_pet("Рекс", "DOG", 6)
        
        stats = container.get_statistics()
        
        assert stats['total'] == 4
        assert stats['average_age'] == (3 + 5 + 4 + 6) / 4
        assert stats['by_species']['CAT'] == 2
        assert stats['by_species']['DOG'] == 2
    
    def test_workflow_complete(self):
        """Полный рабочий процесс."""
        container = PetContainer()
        
        # Добавление питомцев
        container.add_pet("Барсик", "CAT", 3)
        container.add_pet("Шарик", "DOG", 5)
        container.add_pet("Мурка", "CAT", 2)
        container.add_pet("Кеша", "BIRD", 1)
        
        # Проверка добавления
        assert len(container.pets) == 4
        
        # Поиск по виду
        cats = container.find_by_species("CAT")
        assert len(cats) == 2
        
        dogs = container.find_by_species("DOG")
        assert len(dogs) == 1
        
        # Сортировка
        container.sort_by_age()
        assert container.pets[0].age == 1
        assert container.pets[-1].age == 5
        
        # Статистика
        stats = container.get_statistics()
        assert stats['total'] == 4
        assert stats['by_species']['CAT'] == 2
        assert stats['by_species']['DOG'] == 1
        assert stats['by_species']['BIRD'] == 1
        
        # Сохранение и загрузка
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "workflow.json")
            container.save_to_file(filename)
            
            new_container = PetContainer()
            new_container.load_from_file(filename)
            
            assert len(new_container.pets) == 4
            assert new_container.pets[0].name == "Кеша"  # После сортировки
    
    def test_show_all_format(self):
        """Проверка формата вывода show_all."""
        container = PetContainer()
        container.add_pet("Барсик", "CAT", 3)
        
        result = container.show_all()
        lines = result.split('\n')
        
        assert "Список всех питомцев" in lines[0]
        assert "-" * 40 in lines[1]
        assert "1. Барсик - кот, 3 лет" in lines[2]
        assert "-" * 40 in lines[3]
        assert "Всего: 1 питомцев" in lines[4]
    
    def test_add_pet_invalid_age_through_container(self):
        """Попытка добавить питомца с невалидным возрастом через контейнер."""
        container = PetContainer()
        
        # Отрицательный возраст
        with pytest.raises(ValueError):
            container.add_pet("Барсик", "CAT", -1)
        
        # Слишком большой возраст
        with pytest.raises(ValueError):
            container.add_pet("Барсик", "CAT", 150)
        
        # Проверка, что питомцы не добавлены
        assert len(container.pets) == 0