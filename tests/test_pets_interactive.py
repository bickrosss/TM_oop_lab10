#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import pytest
from unittest.mock import patch, Mock
from io import StringIO
from pets_interactive import InteractivePetCLI


class TestInteractivePetCLI:
    """Тесты для интерактивного интерфейса."""
    
    def test_init(self):
        """Инициализация CLI."""
        cli = InteractivePetCLI()
        assert cli.default_file == "pets.json"
        assert len(cli.container.pets) == 0
    
    @patch('os.path.exists')
    def test_load_default_file_exists(self, mock_exists):
        """Загрузка файла по умолчанию, если он существует."""
        mock_exists.return_value = True
        
        cli = InteractivePetCLI()
        
        # Мокаем метод load_from_file
        with patch.object(cli.container, 'load_from_file') as mock_load:
            cli.load_default_file()
            
            mock_load.assert_called_once_with("pets.json")
    
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_load_default_file_not_exists(self, mock_print, mock_exists):
        """Загрузка файла по умолчанию, если он не существует."""
        mock_exists.return_value = False
        
        cli = InteractivePetCLI()
        
        # Мокаем метод load_from_file
        with patch.object(cli.container, 'load_from_file') as mock_load:
            cli.load_default_file()
            
            # Метод не должен быть вызван
            mock_load.assert_not_called()
    
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_load_default_file_error(self, mock_print, mock_exists):
        """Ошибка при загрузке файла по умолчанию."""
        mock_exists.return_value = True
        
        cli = InteractivePetCLI()
        
        # Мокаем метод load_from_file для вызова исключения
        with patch.object(cli.container, 'load_from_file', 
                         side_effect=Exception("Ошибка загрузки")):
            cli.load_default_file()
            
            # Проверяем, что ошибка была обработана
            assert mock_print.called
    
    @patch('builtins.input', side_effect=['1', '8'])
    @patch('builtins.print')
    def test_run_exit_immediately(self, mock_print, mock_input):
        """Запуск и немедленный выход."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            # Запускаем, пользователь сразу выбирает выход (8)
            cli.run()
            
            # Проверяем, что выведено прощание
            assert any("До свидания" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['invalid', '8'])
    @patch('builtins.print')
    def test_run_invalid_choice(self, mock_print, mock_input):
        """Неверный выбор в меню."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем, что выведено сообщение об ошибке
            assert any("Неверный выбор" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_add_pet_interactive_valid(self, mock_print, mock_input):
        """Интерактивное добавление валидного питомца."""
        # Симулируем ввод пользователя
        mock_input.side_effect = ['Барсик', 'cat', '3']
        
        cli = InteractivePetCLI()
        
        # Проверяем, что питомец добавляется
        assert len(cli.container.pets) == 0
        cli.add_pet_interactive()
        assert len(cli.container.pets) == 1
        
        # Проверяем вывод
        assert any("Добавлен питомец" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['', 'cat', '3'])
    @patch('builtins.print')
    def test_add_pet_interactive_empty_name(self, mock_print, mock_input):
        """Попытка добавить питомца с пустым именем."""
        cli = InteractivePetCLI()
        cli.add_pet_interactive()
        
        # Питомец не должен быть добавлен
        assert len(cli.container.pets) == 0
        
        # Должно быть сообщение об ошибке
        assert any("не может быть пустой" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['Барсик', 'cat', 'не число'])
    @patch('builtins.print')
    def test_add_pet_interactive_invalid_age(self, mock_print, mock_input):
        """Попытка добавить питомца с нечисловым возрастом."""
        cli = InteractivePetCLI()
        cli.add_pet_interactive()
        
        # Питомец не должен быть добавлен
        assert len(cli.container.pets) == 0
        
        # Должно быть сообщение об ошибке
        assert any("должен быть числом" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_find_pets_interactive_found(self, mock_print, mock_input):
        """Интерактивный поиск найденных питомцев."""
        # Сначала добавляем питомцев
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        cli.container.add_pet("Мурка", "CAT", 2)
        cli.container.add_pet("Шарик", "DOG", 5)
        
        # Симулируем поиск котов
        mock_input.return_value = 'cat'
        
        cli.find_pets_interactive()
        
        # Проверяем вывод
        assert any("Найдено 2 питомцев" in str(call) for call in mock_print.call_args_list)
        assert any("Барсик" in str(call) for call in mock_print.call_args_list)
        assert any("Мурка" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', return_value='dog')
    @patch('builtins.print')
    def test_find_pets_interactive_not_found(self, mock_print, mock_input):
        """Интерактивный поиск не найденных питомцев."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        cli.find_pets_interactive()
        
        # Должно быть сообщение, что не найдены
        assert any("не найдены" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_sort_pets_interactive_by_name(self, mock_print, mock_input):
        """Интерактивная сортировка по имени."""
        mock_input.return_value = '1'
        
        cli = InteractivePetCLI()
        cli.container.add_pet("Шарик", "DOG", 5)
        cli.container.add_pet("Барсик", "CAT", 3)
        
        cli.sort_pets_interactive()
        
        # Проверяем сортировку
        assert cli.container.pets[0].name == "Барсик"
        assert cli.container.pets[1].name == "Шарик"
        
        # Проверяем сообщение
        assert any("отсортированы по имени" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_sort_pets_interactive_invalid(self, mock_print, mock_input):
        """Неверный выбор при сортировке."""
        cli = InteractivePetCLI()
        cli.sort_pets_interactive()
        
        # Должно быть сообщение об ошибке
        assert any("Неверный выбор" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_show_statistics_empty(self, mock_print):
        """Показ статистики для пустого контейнера."""
        cli = InteractivePetCLI()
        cli.show_statistics()
        
        assert any("Всего питомцев: 0" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    def test_show_statistics_with_pets(self, mock_print):
        """Показ статистики для контейнера с питомцами."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        cli.container.add_pet("Мурка", "CAT", 5)
        cli.container.add_pet("Шарик", "DOG", 4)
        
        cli.show_statistics()
        
        # Проверяем вывод статистики
        output_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Всего питомцев: 3" in call for call in output_calls)
        assert any("Средний возраст:" in call for call in output_calls)
        assert any("кот: 2" in call for call in output_calls)
        assert any("собака: 1" in call for call in output_calls)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_save_data_interactive_default(self, mock_print, mock_input):
        """Сохранение данных с именем файла по умолчанию."""
        mock_input.return_value = ''  # Пустой ввод - использовать по умолчанию
        
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli.container, 'save_to_file') as mock_save:
            cli.save_data_interactive()
            
            # Должен быть вызван с файлом по умолчанию
            mock_save.assert_called_once_with("pets.json")
            
            # Проверяем сообщение
            assert any("сохранены" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_save_data_interactive_custom(self, mock_print, mock_input):
        """Сохранение данных с пользовательским именем файла."""
        mock_input.return_value = 'my_pets.json'
        
        cli = InteractivePetCLI()
        
        with patch.object(cli.container, 'save_to_file') as mock_save:
            cli.save_data_interactive()
            
            # Должен быть вызван с пользовательским именем
            mock_save.assert_called_once_with("my_pets.json")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_save_data_interactive_error(self, mock_print, mock_input):
        """Ошибка при сохранении данных."""
        mock_input.return_value = 'test.json'
        
        cli = InteractivePetCLI()
        
        with patch.object(cli.container, 'save_to_file', 
                         side_effect=Exception("Ошибка записи")):
            cli.save_data_interactive()
            
            # Должно быть сообщение об ошибке
            assert any("Ошибка" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_load_data_interactive_success(self, mock_print, mock_input):
        """Успешная загрузка данных."""
        mock_input.return_value = 'pets.json'
        
        cli = InteractivePetCLI()
        
        with patch.object(cli.container, 'load_from_file') as mock_load:
            cli.load_data_interactive()
            
            mock_load.assert_called_once_with("pets.json")
            assert any("Загружено" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_load_data_interactive_file_not_found(self, mock_print, mock_input):
        """Загрузка из несуществующего файла."""
        mock_input.return_value = 'nonexistent.json'
        
        cli = InteractivePetCLI()
        
        with patch.object(cli.container, 'load_from_file', 
                         side_effect=FileNotFoundError("Файл не найден")):
            cli.load_data_interactive()
            
            # Должно быть сообщение об ошибке
            assert any("не существует" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['8', 'n'])
    @patch('builtins.print')
    def test_run_exit_without_save(self, mock_print, mock_input):
        """Выход без сохранения."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем, что было предложение сохранить
            assert any("Сохранить данные" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['8', 'y'])
    @patch('builtins.print')
    def test_run_exit_with_save(self, mock_print, mock_input):
        """Выход с сохранением."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            with patch.object(cli.container, 'save_to_file') as mock_save:
                cli.run()
                
                # Проверяем, что сохранение было вызвано
                mock_save.assert_called_once_with("pets.json")
                assert any("сохранены" in str(call) for call in mock_print.call_args_list)
    
    def test_print_menu_format(self):
        """Проверка формата меню."""
        cli = InteractivePetCLI()
        
        with patch('builtins.print') as mock_print:
            cli.print_menu()
            
            # Получаем все вызовы print
            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            
            # Проверяем ключевые элементы меню
            assert any("СИСТЕМА УЧЁТА ПИТОМЦЕВ" in call for call in calls)
            assert any("Добавить питомца" in call for call in calls)
            assert any("Показать всех питомцев" in call for call in calls)
            assert any("Найти питомцев по виду" in call for call in calls)
            assert any("Отсортировать питомцев" in call for call in calls)
            assert any("Показать статистику" in call for call in calls)
            assert any("Сохранить данные" in call for call in calls)
            assert any("Загрузить данные" in call for call in calls)
            assert any("Выйти" in call for call in calls)
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        """Прерывание программы пользователем."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем сообщение о прерывании
            assert any("прервана" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['2', '8'])
    @patch('builtins.print')
    def test_run_list_command(self, mock_print, mock_input):
        """Выбор команды показа списка."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            # Мокаем show_all для контроля вывода
            with patch.object(cli.container, 'show_all', return_value="Тестовый вывод"):
                cli.run()
                
                # Проверяем, что show_all был вызван
                assert any("Тестовый вывод" in str(call) for call in mock_print.call_args_list)