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

network = Net.Network(name="Simulator", router_count=5)
global_tree = None 

class Router():
    def __init__(self, x1, y1, size, name, rno, neighbors=[]):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + size
        self.y2 = y1 + size
        self.x_mid = (x1 + x1 + size)/2
        self.y_mid = (y1 + y1 + size)/2
        self.name = name
        self.neighbors = []
        self.neighbors_found = []
        self.rno = rno

    def add_neighbors(self, routers):
        for r in routers:
            self.neighbors.append(r)

    def add_neighbors_found(self, routers):
        for r in routers:
            self.neighbors_found.append(r)

    def print_neighbors(self):
        print("Router: " + str(self.name) + " has neighbors: ", end = '')
        for router in self.neighbors:
            print(str(router.name) + " ", end = '')

    def print_neighbors_found(self):
        print("Router: " + str(self.name) + " has found neighbors: ", end = '')
        for router in self.neighbors_found:
            print(str(router.name) + " ", end = '')


#create routers
def draw_routers(window, neighbor_array):
    size = 100
    r0 = Router(150, 150, size, "r0", 0)
    r1 = Router(50, 300, size, "r1", 1)
    r2 = Router(150, 450, size, "r2", 2)
    r3 = Router(450, 225, size, "r3", 3)
    r4 = Router(450, 375, size, "r4", 4)
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

    table_values = {'row0':{'r0':'Dest','r0 ':'Dist','r0  ':'Next','r1':'Dest','r1 ':'Dist',' r1  ':'Next',
                            'r2':'Dest','r2 ':'Dist','r2  ':'Next','r3':'Dest','r3 ':'Dist',' r3  ':'Next',
                            'r4':'Dest','r4 ':'Dist','r4  ':'Next'}}
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

def create_network(frontend_routers):
    print("creating_network")
    global network
    backend_routers = network.routers
    for f_router in frontend_routers:
        for f_neighbor in f_router.neighbors:
            idx1 = f_router.rno
            idx2 = f_neighbor.rno
            b_router1 = backend_routers[idx1]
            b_router2 = backend_routers[idx2]
            network.connect(b_router1, b_router2)


def draw_tables(root, table_values):
    print("showing tables")
    #data = [[]]
    #for i in range(len(routers)):
    #    data.append([])

    #for j in range(len(routers)):
        #data[0][0].append(routers[i].name)
    data = [ ["Dest", "Dist", "Next", "Dest", "Dist", "Next", "Dest", "Dist", "Next"], ]


    frame = Frame(root, width=800, height=200)
    frame.pack()

    tree = ttk.Treeview(frame, columns = (1,2,3,4,5,6,7,8,9,10), height = 5, show = "headings")
    tree.grid (row = 0, column = 1, columnspan = 3)

    tree.heading(2, text="Router 0")
    tree.heading(5, text="Router 1")
    tree.heading(8, text="Router 2")

    tree.column(1, width = 100)
    tree.column(2, width = 100)
    tree.column(3, width = 100)
    tree.column(4, width = 100)
    tree.column(5, width = 100)
    tree.column(6, width = 100)
    tree.column(7, width = 100)
    tree.column(8, width = 100)
    tree.column(9, width = 100)


    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scroll.pack(side = 'right', fill = 'y')

    tree.configure(yscrollcommand=scroll.set)

    for val in data:
        #for input in val:
        tree.insert('', 'end', values = (val) )
    tree.pack(side = 'left')

    global global_tree
    global_tree = tree 

    return tree

def start_communication(source, dest):
    window.create_line(source.x_mid, source.y_mid, dest.x_mid, dest.y_mid, fill="green")

def stop_communication(source, dest):
    window.create_line(source.x_mid, source.y_mid, dest.x_mid, dest.y_mid, fill="black")

#background
def draw_canvas(neighbor_array):
    root = Tk()
    window = Canvas(root, width = 800, height = 800)
    window.grid()
    routers, table_values = draw_routers(window, neighbor_array)
    draw_link(window, routers)
    tree = draw_tables(root, table_values)
    create_network(routers)
    #table.insert('', 'end', values = ("a", "b", "c"))
    window.bind("<Left>", leftKey)
    window.bind("<Right>", rightKey)
    window.focus_set()
    window.pack()
    root.mainloop()
    return tree

def update_table(new_state):
    global global_tree
    index = 0
    found_data = True

    # for i in global_tree.get_children():
    #     print(i)
    #     if int(i[-1]) > 1:
    #         print("deleting")
    #         global_tree.delete(i)

    while found_data:
        found_data = False
        row = []
        for idd, router in new_state.routers.items():
            #print(len(router.routes), router.routes)
            if index < len(router.routes):
                destinations = list(router.routes.keys())
                routes = list(router.routes.values())
                #print(destinations, routes)
                dest = destinations[index]
                dist = routes[index][0]
                link = routes[index][1]
                if link == None:
                    #print(dest, dist, link)
                    row.extend([dest, dist, link])
                else:
                    #print(dest, dist, link.pointB.id)
                    row.extend([dest, dist, link.pointB.id])
                found_data = True
            else:
                row.extend(['', '', ''])
        print(row)
        global_tree.insert('', 'end', values=row)
        index += 1


## handling ticks
def handle_press(event):
    print("pressed", repr(event.char))

def leftKey(event):
    print("Left key pressed")

def rightKey(event):
    print("Right key pressed")
    global network
    new_state = network.tick()
    for idd,router in new_state.routers.items():
        print(idd, router.routes)

    update_table(new_state)



def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='DV simualtor')
    arg_parser.add_argument('-r', '--router', dest='router', action='store',
            default=5,
            help='Number of routers')
    arg_parser.add_argument('-l', '--link', dest='link', action='store',
            default=5,
            help='Number of links')
    settings = arg_parser.parse_args()
    neighbor_array = create_links(settings.router, settings.link)
    tree = draw_canvas(neighbor_array)

    # while True:
    #     handle_press()


if __name__ == '__main__':
    main()
