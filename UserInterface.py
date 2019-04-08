import unittest
import Net
import sys
import argparse
from tkinter import *
from tkinter import ttk
import math
from argparse import ArgumentParser

class Location():
    def __init__(self, x1, y1, size):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + size
        self.y2 = y1 + size

#create routers
def draw_routers(window):
    size = 100
    locs = [ Location(150, 150, size), Location(300, 300, size), Location(150, 450, size), Location(450, 150, size), Location(450, 450, size) ]

    for loc in locs:
        window.create_rectangle(loc.x1, loc.y1, loc.x2, loc.y2, fill="blue")



#create links
def draw_link(root, net):

    window.create_line()


#background
def draw_canvas():
    root = Tk()
    window = Canvas(root, width = 800, height = 800)
    window.grid()
    draw_routers(window)
    window.pack()
    root.mainloop()
    return Net.Network("canvas",settings.router)

def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='DV simualtor')
    arg_parser.add_argument('-r', '--router', dest='router', action='store',
            default=5,
            help='Number of routers')
    arg_parser.add_argument('-l', '--link', dest='link', action='store',
            default=8,
            help='Number of links')
    settings = arg_parser.parse_args()
    net = draw_canvas()


if __name__ == '__main__':
    main()
