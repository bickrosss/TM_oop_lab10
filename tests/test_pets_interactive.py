#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import pytest
from unittest.mock import patch, Mock, MagicMock
from io import StringIO
from tasks.pets_interactive import InteractivePetCLI


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
            mock_print.assert_called()
    
    @patch('builtins.input', side_effect=['8', 'n'])
    @patch('builtins.print')
    def test_run_exit_immediately(self, mock_print, mock_input):
        """Запуск и немедленный выход."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            # Запускаем, пользователь сразу выбирает выход (8) и не сохранять (n)
            cli.run()
            
            # Проверяем, что выведено прощание
            assert any("До свидания" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['9', '8', 'n'])  # неверный выбор, потом выход
    @patch('builtins.print')
    def test_run_invalid_choice(self, mock_print, mock_input):
        """Неверный выбор в меню."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем, что выведено сообщение об ошибке
            assert any("Неверный выбор" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['1', 'Барсик', 'cat', '3', '8', 'n'])
    @patch('builtins.print')
    def test_run_add_pet_command(self, mock_print, mock_input):
        """Добавление питомца через меню."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем, что питомец добавлен
            assert len(cli.container.pets) == 1
            assert cli.container.pets[0].name == "Барсик"
            
            # Проверяем вывод
            assert any("Добавлен питомец" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['2', '8', 'n'])
    @patch('builtins.print')
    def test_run_list_command(self, mock_print, mock_input):
        """Команда показа списка."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            # Мокаем show_all для контроля вывода
            with patch.object(cli.container, 'show_all', return_value="Тестовый вывод"):
                cli.run()
                
                # Проверяем, что show_all был вызван
                assert any("Тестовый вывод" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['3', 'cat', '8', 'n'])
    @patch('builtins.print')
    def test_run_find_command(self, mock_print, mock_input):
        """Команда поиска питомцев."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем, что поиск выполнен
            assert any("Барсик" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['4', '1', '8', 'n'])  # сортировка по имени
    @patch('builtins.print')
    def test_run_sort_command(self, mock_print, mock_input):
        """Команда сортировки."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Шарик", "DOG", 5)
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем сообщение о сортировке
            assert any("отсортированы" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['5', '8', 'n'])
    @patch('builtins.print')
    def test_run_stats_command(self, mock_print, mock_input):
        """Команда статистики."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем вывод статистики
            assert any("Всего питомцев" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['6', '', '8', 'n'])  # сохранение с именем по умолчанию
    @patch('builtins.print')
    def test_run_save_command(self, mock_print, mock_input):
        """Команда сохранения."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            with patch.object(cli.container, 'save_to_file') as mock_save:
                cli.run()
                
                # Проверяем, что сохранение вызвано
                mock_save.assert_called_once_with("pets.json")
                assert any("сохранены" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', side_effect=['7', 'pets.json', '8', 'n'])
    @patch('builtins.print')
    def test_run_load_command(self, mock_print, mock_input):
        """Команда загрузки."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            with patch.object(cli.container, 'load_from_file') as mock_load:
                # Мокаем существование файла
                with patch('os.path.exists', return_value=True):
                    cli.run()
                    
                    # Проверяем, что загрузка вызвана
                    mock_load.assert_called_once_with("pets.json")
                    assert any("Загружено" in str(call) for call in mock_print.call_args_list)
    
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
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_run_keyboard_interrupt(self, mock_print, mock_input):
        """Прерывание программы пользователем."""
        cli = InteractivePetCLI()
        
        with patch.object(cli, 'load_default_file'):
            cli.run()
            
            # Проверяем сообщение о прерывании
            assert any("прервана" in str(call) for call in mock_print.call_args_list)
    
    def test_print_menu_format(self):
        """Проверка формата меню."""
        cli = InteractivePetCLI()
        
        # Захватываем вывод
        with patch('builtins.print') as mock_print:
            cli.print_menu()
            
            # Получаем все вызовы print
            calls = [str(call[0][0]) for call in mock_print.call_args_list if call[0]]
            
            # Проверяем ключевые элементы меню
            assert any("СИСТЕМА УЧЁТА ПИТОМЦЕВ" in call for call in calls)
            assert any("Добавить питомца" in call for call in calls)
            assert any("Выйти" in call for call in calls)
    
    @patch('builtins.input')
    def test_add_pet_interactive_valid(self, mock_input):
        """Интерактивное добавление валидного питомца."""
        # Симулируем ввод пользователя
        mock_input.side_effect = ['Барсик', 'cat', '3']
        
        cli = InteractivePetCLI()
        
        # Проверяем, что питомец добавляется
        assert len(cli.container.pets) == 0
        cli.add_pet_interactive()
        assert len(cli.container.pets) == 1
        assert cli.container.pets[0].name == "Барсик"
    
    @patch('builtins.input', side_effect=['', 'cat', '3'])
    @patch('builtins.print')
    def test_add_pet_interactive_empty_name(self, mock_print, mock_input):
        """Попытка добавить питомца с пустым именем."""
        cli = InteractivePetCLI()
        cli.add_pet_interactive()
        
        # Питомец не должен быть добавлен
        assert len(cli.container.pets) == 0
        
        # Должно быть сообщение об ошибке
        mock_print.assert_called()
    
    @patch('builtins.input', side_effect=['Барсик', 'cat', 'не число'])
    @patch('builtins.print')
    def test_add_pet_interactive_invalid_age(self, mock_print, mock_input):
        """Попытка добавить питомца с нечисловым возрастом."""
        cli = InteractivePetCLI()
        cli.add_pet_interactive()
        
        # Питомец не должен быть добавлен
        assert len(cli.container.pets) == 0
        
        # Должно быть сообщение об ошибке
        mock_print.assert_called()
    
    @patch('builtins.input', return_value='cat')
    @patch('builtins.print')
    def test_find_pets_interactive_found(self, mock_print, mock_input):
        """Интерактивный поиск найденных питомцев."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        cli.container.add_pet("Мурка", "CAT", 2)
        
        cli.find_pets_interactive()
        
        # Проверяем вывод
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
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_sort_pets_interactive_by_name(self, mock_print, mock_input):
        """Интерактивная сортировка по имени."""
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
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_save_data_interactive_default(self, mock_print, mock_input):
        """Сохранение данных с именем файла по умолчанию."""
        cli = InteractivePetCLI()
        cli.container.add_pet("Барсик", "CAT", 3)
        
        with patch.object(cli.container, 'save_to_file') as mock_save:
            cli.save_data_interactive()
            
            # Должен быть вызван с файлом по умолчанию
            mock_save.assert_called_once_with("pets.json")
            
            # Проверяем сообщение
            assert any("сохранены" in str(call) for call in mock_print.call_args_list)
    
    @patch('builtins.input', return_value='my_pets.json')
    @patch('builtins.print')
    def test_save_data_interactive_error(self, mock_print, mock_input):
        """Ошибка при сохранении данных."""
        cli = InteractivePetCLI()
        
        with patch.object(cli.container, 'save_to_file', 
                         side_effect=Exception("Ошибка записи")):
            cli.save_data_interactive()
            
            # Должно быть сообщение об ошибке
            assert any("Ошибка" in str(call) for call in mock_print.call_args_list)