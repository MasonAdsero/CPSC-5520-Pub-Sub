'''
Mason Adsero
bellman_ford.py
10 24 2022
'''
import math
import datetime

STALENESS = 1.5

#For functions bellman_ford, weights, getPath consulted wikipedia professor provided
class bellGraph:
    def __init__(self):
        '''
        Initializes our graph which is implemented through a dictionary
        '''
        self.graph = {}

    def retGraph(self):
        '''
        Returns a copy of our graph for traversal purposes in lab3.py
            self.graph: a graph of our nodes(currencies) and our edges(exchange rate)
        '''
        return self.graph

    def addToGraph(self, time, currOne, currTwo, exchRate):
        '''
        Adds a quotes to the graph and puts the exchange rate as a logarithm edge. The nodes are currencies
        :param time: time of the quote in UTC format
        :param currOne: The currency that is being exchanged
        :param currTwo: The currency being exchanged to
        :param exchRate: The rate of exchange from currOne to currTwo
        '''
        if currOne not in self.graph:
           self.graph[currOne] = dict()
        if currTwo not in self.graph:
            self.graph[currTwo] = dict()
        self.graph[currOne][currTwo] = (-math.log10(exchRate), time)
        self.graph[currTwo][currOne] = (math.log10(exchRate), time)

    def shortest_paths(self, start_vertex, tolerance=0):
        """
        Find the shortest paths (sum of edge weights) from start_vertex to every other vertex.
        Also detect if there are negative cycles and report one of them.
        Edges may be negative.

        For relaxation and cycle detection, we use tolerance. Only relaxations resulting in an improvement
        greater than tolerance are considered. For negative cycle detection, if the sum of weights is
        greater than -tolerance it is not reported as a negative cycle. This is useful when circuits are expected
        to be close to zero.
        :param start_vertex: start of all paths
        :param tolerance: only if a path is more than tolerance better will it be relaxed
        :return: distance, predecessor, negative_cycle
            dist:       dictionary keyed by vertex of shortest distance from start_vertex to that vertex
            pred:    dictionary keyed by vertex of previous vertex in shortest path from start_vertex
        """
        arbitrageLoop = self.bellman_ford(start_vertex, tolerance)
        if arbitrageLoop is not None:
            return arbitrageLoop
        return None

    #consulted justin thoreson for two if statements in this block
    def bellman_ford(self, start, tolerance):
        dist = {}
        pred = {}
        for node in self.graph:
            dist[node] = float('Inf')
            pred[node] = None
        dist[start] = 0
        for i in range(len(self.graph)-1):
            for node in self.graph:
                for neigh in self.graph[node]:
                    cur = self.graph[node][neigh][0]
                    distance = dist[node] + cur
                    if dist[node] != float('Inf') and distance < dist[neigh] and dist[neigh] - distance > tolerance:
                        dist[neigh] = dist[node] + cur
                        pred[neigh] = node
                    
        for node in self.graph:
            for neigh in self.graph[node]:
                if dist[neigh] > dist[node] + self.graph[node][neigh][0] and self.weights(pred, node) > tolerance:
                    return self.getPath(pred, start)
        return None
    
    def weights(self, pred, node):
        '''
        gives us the absolute value weight of a path to compare to our tolerance
        :param pred: holds the predecessors for the passed in node to build the path
        :param node: our starting currency
            sum: the weight of all edges in this cycle
        '''
        sum = float()
        start = node
        nodeList = [start]
        while True:
            node = pred[node]
            if node in nodeList:
                nodeList.append(node)
                break
            else:
                nodeList.append(node)
        for node in range(len(nodeList)-2):
            sum = sum + self.graph[nodeList[node]][nodeList[node+1]][0]
        return abs(sum)
        
    #consulted https://github.com/rosshochwert/arbitrage for building path
    @staticmethod
    def getPath(pred, start):
        '''
        Builds the path from our starting currency to get arbitrage
        :param pred: holds the predecessors for the passed in node to build the path
        :param node: our starting currency
            arbLoop: the path that gives us arbitrage for our starting currency
        '''
        arbLoop = []
        arbLoop.append(start)
        nxtNode = start
        while True:
            nxtNode = pred[nxtNode]
            if nxtNode not in arbLoop:
                arbLoop.append(nxtNode)
            else:
                arbLoop.append(nxtNode)
                arbLoop = arbLoop[arbLoop.index(nxtNode):][::-1] #first index for starting currency
                return arbLoop

    def deleteStaleQuotes(self):
        '''
        Removes quotes whose timestamp surpasses the staleness limit of 1.5 and prints that a quote was removed
        '''
        stale = []
        for key in self.graph.keys():
            for keyTwo in self.graph[key].keys():
                if not self.notStale(self.graph[key][keyTwo][1]):
                    stale.append((key, keyTwo))
        for key in stale:
            del self.graph[key[0]][key[1]]
            print("removing stale quote for ('" + key[0] + "', '" + key[1] + "')")

    @staticmethod
    def notStale(time):
        '''
        helper method to determine if a quote is stale
            returns a boolean true if quote is fresh and false if quote is stale
        '''
        return (datetime.datetime.utcnow() - time).total_seconds() <= STALENESS
            


