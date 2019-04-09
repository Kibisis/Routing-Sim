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
        pass
        """
import Net
n = Net.Network("Test3", 3)
A_router = n.routers[1]
B_router = n.routers[2]
aTObLink = n.connect(A_router, B_router)
n.tick()
"""
        # assertTrue(aTObLink.data)


if __name__ == '__main__':
    unittest.main()
