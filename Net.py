#!/usr/bin/python3

import copy
import Queue

class Network:
    clock = 0
    def __init__(self, name="Network", router_count=0):
        self.name=name # memorable way to differentiate them
        self.routers = {} # dict of all network routers {id: router}
        self.links=set()
        self.router_id = 0
        for i in range(router_count):
            self.add_router()

    def add_router(self):
        r = Router(self.router_id)
        self.routers[self.router_id] = r
        self.router_id+=1

    def tick(self):
        if self.clock is 0:
            print("Clock was 0, routers populating")
            for id,router in self.routers.items(): #add initial positioning to all routers
                if len(router.routes) is 0:
                    d=Data(0, router, router, None, {id:0})
                    router.receive(d)
        self.clock+=1
        for id, router in self.routers.items(): #routers process data already present
            router.process()
        for link in self.links: #pumps data forward
            link.tick(self.clock)
        return self

    def batch_connect(self,source_list, dest_list, link_speeds, link_lengths):
        #Ideally can be used to eat a text file and create a network from it
        #Think: for line in text:
        #           batch_connect(line)
        #Wouldnt work with current implementation though.
        #Also need to set up routers first
        if len(link_speeds) is 1 and len(link_lengths) is 1:
            for (s, d) in zip(source_list, dest_list):
                self.connect(s,d,link_speeds,link_lengths)
        elif len(link_speeds) is 1 and len(link_lengths) > 1:
            for (s, d, ll) in zip(source_list, dest_list, link_lengths):
                self.connect(s,d,link_speeds,ll)
        elif len(link_speeds) > 1 and len(link_lengths) is 1:
            for (s, d, l) in zip(source_list, dest_list, link_speeds):
                self.connect(s,d,l,link_lengths)
        else:
            for (s, d, l, ll) in zip(source_list, dest_list, link_speeds):
                self.connect(s,d,l,ll)

    def connect(self, l_router, r_router, link_speed=1, link_length=1, capacity=None):
        link = Link(l_router,r_router,link_speed,link_length,capacity)
        self.links.add(link)
        l_router.links.add(link)
        r_router.links.add(link)
        return link

    @staticmethod
    def run(net):
        yield net.tick()

    def __str__(self):
        router_str = ""
        link_str = ""
        net_str = "Network {}: \n".format(self.name) + "-"*20
        for id, router in self.routers.items():
            router_str += "\nRouter {}: \t {}".format(id, router.__str__())
        for link in self.links:
            link_str += "\n{}".format(link.__str__())
        return net_str + router_str + link_str


class Link:
    def __init__(self, pointA, pointB, speed=1, length=1,
                 capacity=None):  # point A and B are Router or Network objects
        self.speed = speed  # allows for duplicate links higher throughput
        self.length = length
        self.capacity = capacity
        self.data = []  # queue of Data objects
        self.ends = [pointA, pointB]
        # check to make sure that links don't already exist, prevents duplicates
        if not self in self.ends[0].links:
            self.ends[0].links.add(self)
        if not self in self.ends[1].links:
            self.ends[1].links.add(self)

    def tick(self, clock):  # pump data forward
        i = 0
        data = self.data
        # routers_reached = set()
        while i < len(data):
            if data[i].time >= clock:  # data has arrived at it's destination
                # routers_reached.add(data[i][2])
                data[i].destination.queue.append(data[i])
                data.pop(i)
                continue #keeps index the same so nothing is skipped
            i += 1
        # return routers_reached

    def send(self, packet):
        travel_time = self.length
        if packet.source is self.ends[0]:
            packet.destination = self.ends[1]
        else:
            packet.destination = self.ends[0]
        packet.time = travel_time + Network.clock
        self.data.append(packet)

    def __eq__(self, lhs):
        return ((lhs.pointA is self.ends[1]) and (lhs.pointB is self.ends[0])) or (
                    (lhs.pointA is self.ends[0]) and (lhs.pointB is self.ends[1]))

    def __hash__(self):
        return id(self)

    def __str__(self):
        str = "Router {} is connected to Router {}-----length: {}".format(self.ends[0].id, self.ends[1].id,self.length)
        contents = "\nContains: {}".format(self.data)
        return str+contents


class Router:
    def __init__(self, id, links=None):
        self.id = id
        self.links = links or set() #{links attached}
        self.routes = {} #dest_id: distance,link
        self.queue = [] #Data objects in the order of arrival

    def update(self,packet):#packet is a data object
                         #assume data in format of (arrival time, source router, table)
                         #assume the table is a router ID => [Distance, Link]
                         #Queue simulates buildup of data, bottlenecks, etc
        link = packet.link
        modified = False
        for key,val in packet.contents.items():
            if key in self.routes.keySet():
                if val + 1 < self.routes[key][0]:
                    self.routes[key][0] = val+1
                    self.routes[key][1] = link
                    modified = True
            else:
                self.routes[key] =[val + 1, link]
                modified = True
        return modified

    def process(self): #check the next batch of routes in the queue
        if len(self.queue) > 0:
            modified = self.update(self.queue.pop(0))
            if modified:
                self.broadcast()

    def broadcast(self): #send <dest, distance> out along all links
        for link in self.links:
            pack = Data(clock, self, None, link, self.routes)
            link.send(self.routes.deepcopy(), self) #TODO may need to change this to a Data object

    def receive(self, packet):
        self.queue.append(packet)

    def __str__(self):
        connected_routers = []
        for i in self.links:
            connected_routers.append(i.ends[0].id if i.ends[1].id is self.id else i.ends[1].id)
        prnt_str = "Router {} is linked to {} \n Table: {}".format(self.id,connected_routers,self.routes)
        return prnt_str

    def __eq__(self, other):
        for i, j in zip(self.links,other.links):
            if i != j:
                return False
        for i, j in zip(self.queue, other.queue):
            if i != j:
                return False
        return True


class Data:
    def __init__(self, time, source, dest, contents, link, type='Routes'):
        self.type = type
        self.time = time
        self.destination = dest
        self.source = source
        self.contents = contents
        self.size = size
        self.link = link


def build_from_file(fname):
    with open(fname,'r') as f:
        name = f.readline().strip('\n')
        r_c = int(f.readline().strip('\n'))
        n = Network(name, r_c)
        for line in f:
            arr = line.split(',')
            n.connect(n.routers[arr[0]], n.routers[arr[1]], int(arr[2]), int(arr[3]))
    return n


def find_shortest(start, dest, web): #Requires distance vector to be completed
                                     #Find the shortest path from one Router to another
    path_list = [start]
    cur = start
    while True:
        if cur is dest:
            yield path_list
        if dest in cur.routes.keySet():
            link = cur.routes[dest][1]
            path_list.append(cur)
            if link.ends[0] is cur:
                cur = link.ends[1]
            else:
                cur = link.ends[0]
            yield path_list
        else:
            raise Exception
