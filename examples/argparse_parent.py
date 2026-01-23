import argparse

parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('--user', action='store')
parent_parser.add_argument('--password', action='store')

child_parser = argparse.ArgumentParser(parents=[parent_parser])
child_parser.add_argument('--show_all', action='store_true')

args = child_parser.parse_args()
print(args)