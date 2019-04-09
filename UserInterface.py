import unittest
import Net
import sys
import argparse
from tkinter import *
from tkinter import ttk
import math
from argparse import ArgumentParser
import random
from itertools import combinations
from tkintertable import TableCanvas, TableModel

class Router():
    def __init__(self, x1, y1, size, name, neighbors=[]):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + size
        self.y2 = y1 + size
        self.x_mid = (x1 + x1 + size)/2
        self.y_mid = (y1 + y1 + size)/2
        self.name = name
        self.neighbors = []

    def add_neighbors(self, routers):
        for r in routers:
            self.neighbors.append(r)

    def print_neighbors(self):
        print("Router: " + str(self.name) + " has neighbors: ", end = '')
        for router in self.neighbors:
            print(str(router.name) + " ", end = '')

#create routers
def draw_routers(window, neighbor_array):
    size = 100
    r0 = Router(150, 150, size, "r0")
    r1 = Router(50, 300, size, "r1")
    r2 = Router(150, 450, size, "r2")
    r3 = Router(450, 225, size, "r3")
    r4 = Router(450, 375, size, "r4")
    routers = [r0, r1, r2, r3, r4]

    for i in range(len(routers)):
        for j in range(len(neighbor_array[i])):
            neighbor_array[i][j] = routers[neighbor_array[i][j]]
        routers[i].add_neighbors(neighbor_array[i])

    # test to see if routers have neighbors
    for router in routers:
        router.print_neighbors()
        print()

    #r1.add_neighbors([r2, r3])
    #r2.add_neighbors([r1, r3, r4, r5])
    #r3.add_neighbors([r1, r2])
    #r4.add_neighbors([r2, r5])
    #r5.add_neighbors([r2, r4])

    for r in routers:
        window.create_oval(r.x1, r.y1, r.x2, r.y2, fill="blue")
        window.create_text(r.x_mid, r.y_mid, fill="white", text=r.name)

    # create table values

    table_values = {'row0':{'r0_':'Dest','r0__':'Dist',' r0___':'Next','r1_':'Dest','r1__':'Dist',' r1___':'Next'}}
                    #'row1':{}}
    return (routers, table_values)


#create links
def draw_link(window, routers):
    for router in routers:
        for neighbor in router.neighbors:
            window.create_line(router.x_mid, router.y_mid, neighbor.x_mid, neighbor.y_mid)

def create_links(routers, links):
    pairs = combinations(range(routers), 2)
    total_pairs = int(math.factorial(routers)/(2*math.factorial(routers - 2)))
    indexes = random.sample(range(total_pairs), links)
    neighbor_array = []
    for i in range(routers):
        neighbor_array.append([])
    index_counter = 0
    for pair in pairs:
        if index_counter in indexes:
            print(pair)
            neighbor_array[pair[0]].append(pair[1])
            neighbor_array[pair[1]].append(pair[0])
        index_counter += 1
    return neighbor_array
    #for array in neighbor_array:
        #print(array)
    #print(indexes)


def draw_tables(table_values):
    print("showing tables")
    root = Tk()
    window = Canvas(root, width = 400, height = 100)
    table = TableCanvas(window, data=table_values, cellwidth=15)
    table.createTableFrame()
    table.show()
    window.pack()
    root.mainloop()
    return

def start_communication(source, dest):
    window.create_line(source.x_mid, source.y_mid, dest.x_mid, dest.y_mid, fill="green")

def stop_communication(source, dest):
    window.create_line(source.x_mid, source.y_mid, dest.x_mid, dest.y_mid, fill="black")

#background
def draw_canvas(neighbor_array):
    root = Tk()
    window = Canvas(root, width = 800, height = 800)
    window.grid()
    routers,table_values = draw_routers(window, neighbor_array)
    draw_link(window, routers)
    draw_tables(table_values)
    window.pack()
    root.mainloop()
    return Net.Network("canvas",settings.router)

## handling moving shapes
def handle_press():
    None


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
    neighbor_array = create_links(settings.router, settings.link)
    draw_canvas(neighbor_array)


if __name__ == '__main__':
    main()
