'''
Mason Adsero
lab3.py
10/24/2022
'''
import sys
import socket
import datetime
import fxp_bytes_subscriber
import bellman_ford
import math

BUF_SZ = 4096

class subsriber:
    def __init__(self, sub, pub):
        '''
        Initialization function
        :param sub: address info for subscriber
        :param pub: address info for publisher
            self.addr: address for sub
            self.servAddr: address for pub
            self.graph: hold bellgraph object which creates graphs, and is responsible for finding arbitrage
        '''
        self.addr = sub
        self.servAddr = pub
        self.graph = bellman_ford.bellGraph()

    def run(self):
        '''
        runs the subscribers loop. binds to subsriber addr, sends subscription message and receives quotes.
        Call functions for unmarshaling data and adding quotes to graph. Also calls functions for finding arbitrage
        and removing stale quotes
        '''
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(self.addr)
            self.subscribe(sock)
            currTime = datetime.datetime(1969, 1, 1)
            while True:
                data = sock.recv(BUF_SZ)
                for i in range(0, len(data), 32):
                    quote = fxp_bytes_subscriber.unmarshal(data[i:i+32])
                    print(*quote)
                    if self.inOrder(currTime, quote[0]):
                        self.graph.addToGraph(*quote)
                        currTime = quote[0]
                    else:
                        print("ignoring out of sequence message")
                path = self.arbitrage()
                if path is not None:
                    self.printArb(path)
                self.graph.deleteStaleQuotes()

    #Consuled Justin for how to reconvert logarithms to exchange rate
    def printArb(self, path):
        '''
        prints the found arbitration path. Assumes we aways start with 100 currency of whichever market we start with.
        converts logarithm currency back to original exchange rate
        :param path: holds the path of currency to take to get arbitrage.
        '''
        tmpGraph = self.graph.retGraph()
        total = 100.0
        print("Start with " + str(path[0]) + " 100")
        for i in range(len(path)-1):
            rate = 10**abs(tmpGraph[path[i]][path[i+1]][0])
            rate = rate if tmpGraph[path[i]][path[i+1]][0] < 0 else 1/rate
            total *= rate
            print("exchange " + path[i] + " for " + path[i+1] + " at "+ str(rate) + " --> " + path[i+1] + " " + str(total))

    def arbitrage(self):
        '''
        This function calles the bellgraph functions for finding an arbitrage. This will return only the 
        first found arbitrage in the graph whatever it may be. returns none if no arbitrage present.
            path: The currency names in the order needed to be taken to get arbitrage.
        '''
        tmpGraph = self.graph.retGraph()
        for node in tmpGraph:
            path = self.graph.shortest_paths(node, 0.00000001)
            if path is not None:
                return path
        return None
    
    def subscribe(self, sock):
        '''
        Sends the subscription message to the publisher server.
        :param sock: holds the socket for subscriber
        '''
        addr = fxp_bytes_subscriber.serialize_addr(self.addr, sock.getsockname())
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as pub:
            pub.sendto(addr, self.servAddr)

    @staticmethod
    def inOrder(currTime, quoteTime):
        return (quoteTime - currTime).total_seconds() >= 0                       

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage subscriber: hostname, port, publisherHostname, publisherPort")
    exch = subsriber((sys.argv[1], int(sys.argv[2])), (sys.argv[3], int(sys.argv[4])))
    exch.run()