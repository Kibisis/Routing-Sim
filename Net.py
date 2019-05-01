#!/usr/bin/python3

import copy
import queue

class Network:

    def __init__(self, name="Network", router_count=0):
        self.clock = 0
        self.name=name # memorable way to differentiate them
        self.routers = {} # dict of all network routers {id: router}
        self.links=set()
        self.router_id = 0
        self.past_networks = {}
        for i in range(router_count):
            self.add_router()

    def add_router(self):
        r = Router(self.router_id)
        self.routers[self.router_id] = r
        self.router_id+=1

    def tick(self):
        if self.clock is 0:
            for id,router in self.routers.items(): #add initial positioning to all routers
                if len(router.routes) is 0:
                    d=Data(0, router, router, {id:[-1,None]}, None)
                    router.receive(d)

        self.clock+=1
        if self.clock in self.past_networks:
          return self.past_networks[self.clock]
        else:
            self.past_networks[self.clock] = copy.deepcopy(self)

        for id, router in self.routers.items(): #routers process data already present
            router.process()
        for link in self.links: #pumps data forward
            link.tick(self.clock)
        print("BEGIN PRINT")
        for router_id, router in self.routers.items():
            print("Router ID is: {}".format(router.id))
        #     # print("The following ids are in the router: ")
            for key, val in router.routes.items():
                print(key)
        #     # print("Finished printing ids now.")
        #     for link in router.links:
        #         print("Router has a Link from {} to {}".format(link.ends[0].id,link.ends[1].id))
        #     # for datum in router.queue:
        #     #     print(datum.source)
        # # print()
        # # print("-"*30, "\n", self, "\n", "-"*30)
        # # print()
        print("END PRINT")
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
        for i in l_router.links:
            if r_router in i.ends and l_router in i.ends:
                return None
        for i in r_router.links:
            if r_router in i.ends and l_router in i.ends:
                return None
        link = Link(l_router,r_router,link_speed,link_length,capacity)
        self.links.add(link)
        l_router.links.add(link)
        r_router.links.add(link)
        return link

    # def run(self):
    #     if self.clock in past_networks:
    #         yield past_networks[self.clock]
    #         self.clock += 1
    #     else:
    #         past_networks[self.clock] = copy.deepcopy(net)
    #         print(past_networks, "in run")
    #         yield net.tick()

    def back(self):
        self.clock -= 1
        print(self.clock, self.past_networks)
        return self.past_networks[self.clock]



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
    def __init__(self, pointA, pointB, length=1, speed=1,
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
        # routers_reached = set()
        while i < len(self.data):
            # print("LINK TICK")
            if self.data[i].time <= clock:  # data has arrived at it's destination
                # print("LINK REMOVE?!")
                # routers_reached.add(data[i][2])

                self.data[i].destination.queue.append(self.data[i])
                # print("LENGTH AFTER {}".format(len(self.data)))
                self.data.pop(i)
                # print("LENGTH AFTER: {}".format(len(self.data)))
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
        if self is None or lhs is None:
            return self is lhs
        return ((lhs.ends[0] is self.ends[1]) and (lhs.ends[1] is self.ends[0])) or (
                    (lhs.ends[0] is self.ends[0]) and (lhs.ends[1] is self.ends[1]))

    def __hash__(self):
        return id(self)

    def __str__(self):
        str = "Router {} is connected to Router {}-----length: {}".format(self.ends[0].id, self.ends[1].id,self.length)
        contents = "\nContains: {}".format(self.data)
        return str+contents


class Router:
    #indexes into routing info list
    DISTANCE = 0
    LINK = 1

    def __init__(self, id, links=None):
        self.id = id
        self.links = links or set() #{links attached}
        self.routes = {} #dest_id: [distance,link]
        self.queue = [] #Data objects in the order of arrival

    def found_shorter_path(self, cur_dist, new_dist):
        return new_dist + 1 < cur_dist

    def update_shortest_path(self, router_id, link, new_dist):
        self.routes[router_id][Router.DISTANCE] = new_dist
        self.routes[router_id][Router.LINK] = link

    def add_new_router(self, router_id, distance, link):
        self.routes[router_id] = [distance, link]

    def update(self,packet):#packet is a data object
                         #assume data in format of (arrival time, source router, table)
                         #assume the table is a router ID => [Distance, Link]
                         #Queue simulates buildup of data, bottlenecks, etc
        print("Router {} is processing a packet".format(self.id))
        print("Starting table is {}".format(self.routes))
        print("The packet has : {}".format(packet.contents))
        link = packet.link
        modified = False
        for router_id, routing_info in packet.contents.items(): #router_id: str, routing_info: [dist, link]
            if router_id in self.routes:
                if self.found_shorter_path(self.routes[router_id][Router.DISTANCE], routing_info[Router.DISTANCE]):
                    self.update_shortest_path(router_id, link, routing_info[Router.DISTANCE] + 1)
                    modified = True
            else:
                self.add_new_router(router_id, routing_info[Router.DISTANCE] + 1, link)
                modified = True
        # print("The route was modified? {}".format(modified))
        # if modified:
            # print("The new routes table is {}".format(self.routes))
        return modified

    def process(self): #check the next batch of routes in the queue
        if len(self.queue) > 0:
            modified = self.update(self.queue.pop(0))
            if modified:
                # print("Time to broadcast!")
                self.broadcast()

    def broadcast(self): #send <dest, distance> out along all links
        #print("broadcasting, length of links:", len(self.links))
        for link in self.links:
            # print("Broadcasting on link from {} to {}".format(link.ends[0].id,link.ends[1].id))
            pack = Data(Network.clock, self, None, copy.copy(self.routes), link)
            link.send(pack)
            #print("broadcasting from:", self, link)

    def receive(self, packet):
        self.queue.append(packet)

    def __str__(self):
        connected_routers = []
        for i in self.links:
            connected_routers.append(i.ends[0].id if i.ends[1].id is self.id else i.ends[1].id)
        prnt_str = "Router {} is linked to {} \n Table: {}".format(self.id,connected_routers,self.routes)
        return prnt_str

    def __eq__(self, other):
        if self is None or other is None:
            return self is other
        return self.id is other.id


class Data:
    def __init__(self, time, source, dest, contents, link, type='Routes'):
        self.type = type
        self.time = time
        self.destination = dest
        self.source = source
        self.contents = contents
        self.link = link

    def __str__(self):
        return ("Type: {} Time: {} From {} To {} Containing:{}".format(self.type, self.time, self.source.id, self.destination.id ,self.contents))

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
