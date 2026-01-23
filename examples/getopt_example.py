import getopt
import sys

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]

short_options = "ho:v"
long_options = ["help", "output=", "verbose"]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in ("-v", "--verbose"):
        print("Enabling verbose mode")
    elif current_argument in ("-h", "--help"):
        print("Displaying help")
    elif current_argument in ("-o", "--output"):
        print(f"Enabling special output mode ({current_value})")
