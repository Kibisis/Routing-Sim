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
        self.router_id+=1
        r = Router(self.router_id)
        self.routers[self.router_id] = r

    def tick(self):
        if self.clock is 0:
            for router in self.routers: #add initial positioning to all routers
                router.update([[self.clock, router.id, {router.id:0}], None])
        self.clock+=1
        for router in self.routers: #routers process data already present
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
        str = "Network {self.name}: \n Routers: \t {self.routers}"
        return str


class Link:
    def __init__(self, pointA, pointB, speed=1, length=1,
                 capacity=None):  # point A and B are Router or Network objects
        self.speed = speed  # allows for duplicate links higher throughput
        self.length = length
        self.capacity = capacity
        self.data = []  # format - [arrival_time, dest, data]
        self.ends = [pointA, pointB]
        # check to make sure that links don't already exist, prevents duplicates
        if not self in self.ends[0].links:
            self.ends[0].links.add(self)
        if not self in self.ends[1].links:
            self.ends[1].links.add(self)

    def tick(self, clock):  # pump data forward
        i = 0
        data = self.data
        routers_reached = set()
        while i < len(data):
            if data[i][0] >= clock:  # data has arrived at it's destination
                routers_reached.add(data[i][2])
                data[i][2].queue.put(data, self)
                data.remove(i)
            i += 1
        return routers_reached

    def send(self, route_table, source):
        travel_time = self.length
        if source is self.ends[0]:
            dest = self.ends[1]
        else:
            dest = self.ends[0]
        self.data += [Network.clock + travel_time, dest, route_table]

    def __eq__(self, lhs):
        return ((lhs.pointA is self.ends[1]) and (lhs.pointB is self.ends[0])) or (
                    (lhs.pointA is self.ends[0]) and (lhs.pointB is self.ends[1]))

    def __hash__(self):
        return id(self)

    def __str__(self):
        str = "{self.end[0].id} is connected to {self.end[1].id} \nlength: {self.length}\nspeed:{self.speed}\n"
        return str


class Router:
    def __init__(self, id, links=None):
        self.id = id
        self.links = links or set() #{links attached}
        self.routes = {} #dest: distance,link
        self.queue = [] #other <dest, [dist, link]> dictionaries in the order of arrival

    def update(self,arr):#Arr is [data, link transmitting]
                         #assume data in format of (arrival time, source router, table)
                         #assume the table is a router ID => [Distance, Link]
                         #Queue simulates buildup of data, bottlenecks, etc
        data = arr[0]
        link = arr[1]
        modified = False
        for key,val in data[3]:
            if key in self.routes:
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
            modified = self.update(self.queue.get())
            if modified:
                self.broadcast()

    def broadcast(self): #send <dest, distance> out along all links
        for link in self.links:
            link.send(self.routes, self)

    def receive(self, data):
        self.queue.put(data)

    def __str__(self):
        connected_routers = []
        for i in self.links:
            connected_routers.append(i.end[1].id if i.end[2].id is self else i.end[2].id)
        prnt_str = "Router {self.id} is linked to {connected_routers} \n"
        return prnt_str

    # class Data:
    #     def __init__(self, dest, contents, size=1, type='Routes'):
    #         self.type = type
    #         self.destination = dest
    #         self.contents = contents
    #         self.size = size


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
