#!/usr/bin/python
import os.path
import sys
import random

def uniform_integer(min, max):
    print(random.randint(int(min), int(max)))

def uniform_real(min, max):
    print(random.uniform(float(min), float(max)))


commands = {
    'uniform_integer': uniform_integer,
    'uniform_real': uniform_real
}

if __name__ == '__main__':
    command = os.path.basename(sys.argv[1])
    if command in commands:
        commands[command](*sys.argv[2:])
