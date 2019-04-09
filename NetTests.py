#!/usr/bin/python3


import unittest
import Net

class NetTests(unittest.TestCase):
    def test_router_eq(self):
        r1=Net.Router(0)
        r2=Net.Router(0)
        self.assertEqual(r1,r2,"Routers with the same id are the same router")

    def test_link_eq(self):
        n = Net.Network("Name", 2)
        A = n.routers[0]
        B = n.routers[1]
        l = n.connect(A, B)
        self.assertEqual(A, n.routers[A.id], "Network contains all member routers")
        self.assertEqual(B, n.routers[B.id], "Network contains all member routers")
        self.assertIn(l, A.links, "Router A should link to Router B")
        self.assertIn(l, B.links, "Router B should link to Router A")
        self.assertEqual(A.links,B.links, "Router A and B should contain the same link")

    def test_initial_tick(self):
        n = Net.Network("Test3", 5)
        A_router = n.routers[0]
        B_router = n.routers[1]
        C_router = n.routers[2]
        D_router = n.routers[3]
        E_router = n.routers[4]
        print("A{}\nB{}\nC{}\nD{},E{}".format(A_router.id,B_router.id,C_router.id,D_router.id,E_router.id))
        aTOcLink = n.connect(A_router,C_router)
        dTOcLink = n.connect(D_router,C_router)
        bTOcLink = n.connect(B_router,C_router)
        eTOcLink = n.connect(E_router,C_router)

        for i in range(100):
            n.tick()
        # print(n)

    def test_step_by_step(self):
        print("Step by Step")
        n=Net.Network("Step Checks", 3)
        A_router=n.routers[0]
        B_router=n.routers[1]
        C_router=n.routers[2]
        ab_link = n.connect(A_router,B_router)
        bc_link = n.connect(B_router,C_router)
        #First Tick:
        n.tick()
        #Tables initially populated?
        a_table = {}
        b_table = {}
        c_table = {}

        a_table[A_router.id] = [0, None]
        b_table[B_router.id] = [0, None]
        c_table[C_router.id] = [0, None]
        self.assertEqual(a_table, A_router.routes)
        self.assertEqual(b_table, B_router.routes)
        #The initial data sent from the first table entry
        self.assertTrue(len(A_router.queue) is 1)
        self.assertTrue(len(B_router.queue) is 2)

        #Second Tick
        n.tick()
        print("First tick states: ")
        print("Router A has: {}".format(A_router.routes))
        print("Router B has: {}".format(B_router.routes))
        print("Router C has: {}".format(C_router.routes))
        print("End First tick states ")
        a_table[B_router.id] = [1, ab_link]
        b_table[A_router.id] = [1, ab_link]
        b_table[C_router.id] = [1, bc_link]
        c_table[B_router.id] = [1, bc_link]
        print("Second tick states: ")
        print("Router A has: {}".format(A_router.routes))
        print("Router B has: {}".format(B_router.routes))
        print("Router C has: {}".format(C_router.routes))
        print("End Second tick states ")


        print("Second State Links: ")
        for i in ab_link.data:
            print(i)
        for i in bc_link.data:
            print(i)
        print("End Second State links")


        #the data table should have updated with the neighbor routers
        # self.assertEqual(a_table, A_router.routes)
        # self.assertEqual(b_table, B_router.routes)
        # self.assertEqual(c_table, C_router.routes)
        #
        # #the modified tables should be on the links and not yet reached routers
        # self.assertTrue(len(A_router.queue) is 0)
        # self.assertTrue(len(B_router.queue) is 1)
        # self.assertTrue(len(C_router.queue) is 0)

        #Third Tick
        n.tick()
        print("Third tick states: ")
        print("Router A has: {}".format(A_router.routes))
        print("Router B has: {}".format(B_router.routes))
        print("Router C has: {}".format(C_router.routes))
        print("End third tick states ")

        print("Third State Links: ")
        for i in ab_link.data:
            print(i)
        for i in bc_link.data:
            print(i)
        print("End Third State links")

        n.tick()
        print("Fourth tick states: ")
        print("Router A has: {}".format(A_router.routes))
        print("Router B has: {}".format(B_router.routes))
        print("Router C has: {}".format(C_router.routes))
        print("End fourth tick states ")

        print("Fourth State Links: ")
        for i in ab_link.data:
            print(i)
        for i in bc_link.data:
            print(i)
        print("End Fourth State links")


        n.tick()
        print("Fifth tick states: ")
        print("Router A has: {}".format(A_router.routes))
        print("Router B has: {}".format(B_router.routes))
        print("Router C has: {}".format(C_router.routes))
        print("End Fifth tick states ")

        print("Fifth State Links: ")
        for i in ab_link.data:
            print(i)
        for i in bc_link.data:
            print(i)
        print("End Fifth State links")
        
        for i in range(5):
            print(n.clock)
            print("TICK")
            n.tick()
            for i in ab_link.data:
                print(i)
            for i in bc_link.data:
                print(i)

        #The routes should have remained the same
        # self.assertEqual(a_table, A_router.routes)
        # self.assertEqual(b_table, B_router.routes)
if __name__ == '__main__':
    unittest.main()
