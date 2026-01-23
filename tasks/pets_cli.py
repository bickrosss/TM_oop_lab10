#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI версия приложения "Учёт питомцев".
Предоставляет интерфейсы через argparse и click.
"""

import argparse
import sys
import json
from pathlib import Path

try:
    from pets_core import PetContainer, Species
except ImportError:
    # Для совместимости, если файлы в одной директории
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from pets_core import PetContainer, Species


# ============================================================================
# argparse интерфейс
# ============================================================================

def build_argparse_parser():
    """Построить парсер для argparse."""
    parser = argparse.ArgumentParser(
        description="Учёт питомцев - CLI приложение для управления коллекцией питомцев",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s add -n Барсик -s CAT -a 3
  %(prog)s list
  %(prog)s find -s DOG
  %(prog)s save -f my_pets.json
  %(prog)s load -f my_pets.json
        """
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        title='доступные команды',
        description='выберите одну из следующих команд:',
        help='дополнительная справка по командам'
    )
    
    # Команда add
    add_parser = subparsers.add_parser(
        'add',
        help='добавить нового питомца'
    )
    add_parser.add_argument(
        '-n', '--name',
        required=True,
        help='кличка питомца'
    )
    add_parser.add_argument(
        '-s', '--species',
        required=True,
        choices=[s.name for s in Species],
        help='вид животного'
    )
    add_parser.add_argument(
        '-a', '--age',
        type=int,
        required=True,
        help='возраст питомца в годах'
    )
    add_parser.add_argument(
        '-f', '--file',
        default='pets.json',
        help='файл для сохранения (по умолчанию: pets.json)'
    )
    
    # Команда list
    list_parser = subparsers.add_parser(
        'list',
        help='показать всех питомцев'
    )
    list_parser.add_argument(
        '-f', '--file',
        default='pets.json',
        help='файл для загрузки (по умолчанию: pets.json)'
    )
    
    # Команда find
    find_parser = subparsers.add_parser(
        'find',
        help='найти питомцев по виду'
    )
    find_parser.add_argument(
        '-s', '--species',
        required=True,
        choices=[s.name for s in Species],
        help='вид животного для поиска'
    )
    find_parser.add_argument(
        '-f', '--file',
        default='pets.json',
        help='файл для загрузки (по умолчанию: pets.json)'
    )
    
    # Команда stats
    stats_parser = subparsers.add_parser(
        'stats',
        help='показать статистику по питомцам'
    )
    stats_parser.add_argument(
        '-f', '--file',
        default='pets.json',
        help='файл для загрузки (по умолчанию: pets.json)'
    )
    
    # Команда save
    save_parser = subparsers.add_parser(
        'save',
        help='сохранить данные в файл'
    )
    save_parser.add_argument(
        '-f', '--file',
        default='pets.json',
        help='имя файла (по умолчанию: pets.json)'
    )
    save_parser.add_argument(
        '-i', '--input-file',
        help='файл для загрузки перед сохранением'
    )
    
    # Команда load
    load_parser = subparsers.add_parser(
        'load',
        help='загрузить данные из файла'
    )
    load_parser.add_argument(
        '-f', '--file',
        required=True,
        help='имя файла для загрузки'
    )
    
    # Команда sort
    sort_parser = subparsers.add_parser(
        'sort',
        help='отсортировать питомцев'
    )
    sort_parser.add_argument(
        '--by',
        choices=['name', 'age', 'age-desc'],
        default='name',
        help='критерий сортировки'
    )
    sort_parser.add_argument(
        '-f', '--file',
        default='pets.json',
        help='файл для загрузки/сохранения (по умолчанию: pets.json)'
    )
    
    return parser


def run_argparse_command(args):
    """Выполнить команду argparse."""
    container = PetContainer()
    
    # Загрузка данных из файла, если указан
    if hasattr(args, 'file') and args.file:
        file_to_load = args.file
        if hasattr(args, 'input_file') and args.input_file:
            file_to_load = args.input_file
            
        if Path(file_to_load).exists():
            try:
                container.load_from_file(file_to_load)
            except Exception as e:
                print(f"✗ Ошибка при загрузке файла {file_to_load}: {e}")
                return 1
    
    if args.command == 'add':
        try:
            pet = container.add_pet(args.name, args.species, args.age)
            print(f"✓ Добавлен питомец: {pet.name} ({pet.species}, {pet.age} лет)")
            container.save_to_file(args.file)
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return 1
    
    elif args.command == 'list':
        print(container.show_all())
    
    elif args.command == 'find':
        found = container.find_by_species(args.species)
        if not found:
            print(f"✗ Питомцы вида '{args.species}' не найдены")
            return 1
        
        species_name = Species[args.species].value
        print(f"\nПитомцы вида '{species_name}':")
        print("-" * 40)
        for i, pet in enumerate(found, 1):
            print(f"{i}. {pet.name}, {pet.age} лет")
        print("-" * 40)
        print(f"Найдено: {len(found)} питомцев")
    
    elif args.command == 'stats':
        stats = container.get_statistics()
        print(f"Всего питомцев: {stats['total']}")
        if stats['total'] > 0:
            print(f"Средний возраст: {stats['average_age']:.1f} лет")
            print("\nРаспределение по видам:")
            for species, count in stats['by_species'].items():
                species_name = Species[species].value
                print(f"  {species_name}: {count}")
    
    elif args.command == 'save':
        try:
            container.save_to_file(args.file)
            print(f"✓ Данные сохранены в файл: {args.file}")
        except Exception as e:
            print(f"✗ Ошибка при сохранении файла: {e}")
            return 1
    
    elif args.command == 'load':
        try:
            container.load_from_file(args.file)
            print(f"✓ Загружено {len(container.pets)} питомцев из файла {args.file}")
            print(container.show_all())
        except Exception as e:
            print(f"✗ Ошибка при загрузке файла: {e}")
            return 1
    
    elif args.command == 'sort':
        if args.by == 'name':
            container.sort_by_name()
            print("✓ Питомцы отсортированы по имени")
        elif args.by == 'age':
            container.sort_by_age(reverse=False)
            print("✓ Питомцы отсортированы по возрасту (младшие сначала)")
        elif args.by == 'age-desc':
            container.sort_by_age(reverse=True)
            print("✓ Питомцы отсортированы по возрасту (старшие сначала)")
        
        container.save_to_file(args.file)
    
    return 0


def argparse_main():
    """Основная функция для argparse интерфейса."""
    parser = build_argparse_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        args = parser.parse_args()
        return run_argparse_command(args)
    except SystemExit:
        return 1
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return 1


# ============================================================================
# click интерфейс
# ============================================================================

def setup_click_interface():
    """Настроить click интерфейс."""
    try:
        import click
    except ImportError:
        print("Для использования click интерфейса установите пакет: pip install click")
        return None
    
    @click.group()
    @click.pass_context
    def cli(ctx):
        """Учёт питомцев - CLI приложение для управления коллекцией питомцев."""
        ctx.ensure_object(dict)
        if 'container' not in ctx.obj:
            ctx.obj['container'] = PetContainer()
    
    @cli.command()
    @click.option('--name', '-n', required=True, help='Кличка питомца')
    @click.option('--species', '-s', required=True, 
                  type=click.Choice([s.name for s in Species]), help='Вид животного')
    @click.option('--age', '-a', type=int, required=True, help='Возраст питомца')
    @click.option('--file', '-f', default='pets.json', help='Файл для сохранения')
    @click.pass_context
    def add(ctx, name, species, age, file):
        """Добавить нового питомца."""
        container = ctx.obj['container']
        try:
            pet = container.add_pet(name, species, age)
            container.save_to_file(file)
            click.echo(f"✓ Добавлен питомец: {pet.name} ({pet.species}, {pet.age} лет)")
        except Exception as e:
            click.echo(f"✗ Ошибка: {e}", err=True)
    
    @cli.command(name='list')
    @click.option('--file', '-f', default='pets.json', help='Файл для загрузки')
    @click.pass_context
    def list_pets(ctx, file):
        """Показать всех питомцев."""
        container = ctx.obj['container']
        if Path(file).exists():
            try:
                container.load_from_file(file)
            except Exception as e:
                click.echo(f"✗ Ошибка при загрузке: {e}", err=True)
        
        click.echo(container.show_all())
    
    @cli.command()
    @click.option('--species', '-s', required=True,
                  type=click.Choice([s.name for s in Species]), help='Вид животного')
    @click.option('--file', '-f', default='pets.json', help='Файл для загрузки')
    @click.pass_context
    def find(ctx, species, file):
        """Найти питомцев по виду."""
        container = ctx.obj['container']
        if Path(file).exists():
            try:
                container.load_from_file(file)
            except Exception as e:
                click.echo(f"✗ Ошибка при загрузке: {e}", err=True)
        
        found = container.find_by_species(species)
        if not found:
            click.echo(f"✗ Питомцы вида '{species}' не найдены", err=True)
            return
        
        species_name = Species[species].value
        click.echo(f"\nПитомцы вида '{species_name}':")
        click.echo("-" * 40)
        for i, pet in enumerate(found, 1):
            click.echo(f"{i}. {pet.name}, {pet.age} лет")
        click.echo("-" * 40)
        click.echo(f"Найдено: {len(found)} питомцев")
    
    @cli.command()
    @click.option('--file', '-f', default='pets.json', help='Файл для загрузки')
    @click.pass_context
    def stats(ctx, file):
        """Показать статистику по питомцам."""
        container = ctx.obj['container']
        if Path(file).exists():
            try:
                container.load_from_file(file)
            except Exception as e:
                click.echo(f"✗ Ошибка при загрузке: {e}", err=True)
        
        stats = container.get_statistics()
        click.echo(f"Всего питомцев: {stats['total']}")
        if stats['total'] > 0:
            click.echo(f"Средний возраст: {stats['average_age']:.1f} лет")
            click.echo("\nРаспределение по видам:")
            for species, count in stats['by_species'].items():
                species_name = Species[species].value
                click.echo(f"  {species_name}: {count}")
    
    @cli.command()
    @click.option('--file', '-f', default='pets.json', help='Имя файла')
    @click.pass_context
    def save(ctx, file):
        """Сохранить данные в JSON файл."""
        container = ctx.obj['container']
        try:
            container.save_to_file(file)
            click.echo(f"✓ Данные сохранены в файл: {file}")
        except Exception as e:
            click.echo(f"✗ Ошибка при сохранении файла: {e}", err=True)
    
    @cli.command()
    @click.argument('file')
    @click.pass_context
    def load(ctx, file):
        """Загрузить данные из JSON файла."""
        container = ctx.obj['container']
        try:
            container.load_from_file(file)
            click.echo(f"✓ Загружено {len(container.pets)} питомцев из файла {file}")
        except Exception as e:
            click.echo(f"✗ Ошибка при загрузке файла: {e}", err=True)
    
    @cli.command()
    @click.option('--by', type=click.Choice(['name', 'age', 'age-desc']),
                  default='name', help='Критерий сортировки')
    @click.option('--file', '-f', default='pets.json', help='Файл для загрузки/сохранения')
    @click.pass_context
    def sort(ctx, by, file):
        """Отсортировать питомцев."""
        container = ctx.obj['container']
        if Path(file).exists():
            try:
                container.load_from_file(file)
            except Exception as e:
                click.echo(f"✗ Ошибка при загрузке: {e}", err=True)
        
        if by == 'name':
            container.sort_by_name()
            click.echo("✓ Питомцы отсортированы по имени")
        elif by == 'age':
            container.sort_by_age(reverse=False)
            click.echo("✓ Питомцы отсортированы по возрасту (младшие сначала)")
        elif by == 'age-desc':
            container.sort_by_age(reverse=True)
            click.echo("✓ Питомцы отсортированы по возрасту (старшие сначала)")
        
        container.save_to_file(file)
    
    @cli.command()
    @click.pass_context
    def demo(ctx):
        """Демонстрация работы с примером данных."""
        container = ctx.obj['container']
        demo_pets = [
            ("Барсик", "CAT", 3),
            ("Шарик", "DOG", 5),
            ("Мурка", "CAT", 2),
            ("Кеша", "BIRD", 1),
            ("Рекс", "DOG", 4)
        ]
        
        for name, species, age in demo_pets:
            container.add_pet(name, species, age)
        
        click.echo("✓ Добавлено 5 демонстрационных питомцев")
        click.echo(container.show_all())
        container.save_to_file("demo_pets.json")
    
    return cli


def click_main():
    """Основная функция для click интерфейса."""
    cli = setup_click_interface()
    if cli:
        cli()
    else:
        return 1
    return 0


# ============================================================================
# Основной код
# ============================================================================

if __name__ == "__main__":
    # Определяем, какой интерфейс использовать
    if len(sys.argv) > 1 and sys.argv[1] == '--click':
        # Использовать click интерфейс
        sys.argv.pop(1)  # Удаляем --click из аргументов
        sys.exit(click_main())
    else:
        # Использовать argparse интерфейс (по умолчанию)
        sys.exit(argparse_main())