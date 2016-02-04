from collections import defaultdict, deque
from InputFileParser import topology
# from UDPstarter import topology
import numpy as np
import pprint

class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}
        self.nbors_list = {}
        self.new_topology = list(topology)
        self.create_graph()
        self.calculate_all_neighbors()

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances[(to_node, from_node)] = distance

    def create_graph(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}
        self.nbors_list = {}
        from_switches = sorted(set([row[0] for row in self.new_topology]))
        to_switches = sorted(set([row[1] for row in self.new_topology]))
        all_switches = sorted(list(set(from_switches) | set(to_switches)))
        for node in all_switches:
            self.add_node(node)
        numrows = len(self.new_topology)
        numcols = len(self.new_topology[0])
        count = 0
        while count < numrows:
            self.add_edge(self.new_topology[count][0], self.new_topology[count][1], int(self.new_topology[count][3]))
            count = count + 1

    def dijkstra(self, initial):
        visited = {initial: 0}
        path = {}
        nodes = set(self.nodes)
        while nodes:
            min_node = None
            for node in nodes:
                if node in visited:
                    if min_node is None:
                        min_node = node
                    elif visited[node] < visited[min_node]:
                        min_node = node
            if min_node is None:
                break
            nodes.remove(min_node)
            current_weight = visited[min_node]
            for edge in self.edges[min_node]:
                try:
                    weight = current_weight + self.distances[(min_node, edge)]
                except:
                    continue
                if edge not in visited or weight < visited[edge]:
                    visited[edge] = weight
                    path[edge] = min_node
        return visited, path

    def shortest_path(self, origin, destination):
        visited, paths = self.dijkstra(origin)
        full_path = deque()
        _destination = paths[destination]
        while _destination != origin:
            full_path.appendleft(_destination)
            _destination = paths[_destination]
        full_path.appendleft(origin)
        full_path.append(destination)
        # print full_path
        return visited[destination], list(full_path)

    def calculate_all_neighbors(self):
        temp_dict = defaultdict(list)
        np_arr = np.array(self.new_topology)
        if len(np_arr) == 0:
            return dict((k, tuple(v)) for k, v in temp_dict.iteritems())
        else:
            first_col = np_arr[:,0]
            second_col = np_arr[:,1]
            both_cols = np_arr[:,:2]
            for k, v in both_cols:
                temp_dict[k].append(v)
                temp_dict[v].append(k)
            self.nbors_list = dict((k, tuple(v)) for k, v in temp_dict.iteritems())
        return self.nbors_list

    def update_graph(self, active_list):
        del self.new_topology[:]
        from_switches = sorted(set([row[0] for row in topology]))
        to_switches = sorted(set([row[1] for row in topology]))
        all_switches = sorted(list(set(from_switches) | set(to_switches)))
        off_switches = sorted(list(set(all_switches) - set(active_list)))
        print ("The list of active nodes are: " + str(active_list))
        print ("The list of killed nodes are: " + str(off_switches))
        numrows = len(topology)
        count = 0
        if not active_list:
            del self.new_topology[:]
        while count < numrows:
            if ((set(topology[count][0]) <= set(off_switches)) or (set(topology[count][1]) <= set(off_switches))):
                count = count + 1
            else:
                self.new_topology.append(topology[count])
                count = count + 1
        print ("The updated topology is shown below: ")
        pprint.pprint(self.new_topology)
        self.create_graph()
        self.calculate_all_neighbors()

    def calculate_next_hop(self, source, destination):
        if source != destination:
            computation = (self.shortest_path(source, destination))
            return computation[1][1]
        else:
            return destination

if __name__ == '__main__':
    graph = Graph()
    print ("------------------------------------------------------------------------")
    print ("The original topology is shown below: ")
    pprint.pprint(topology)
    nbors_response = graph.calculate_all_neighbors()
    print ("The original neighbors list is shown below: ")
    pprint.pprint(nbors_response)
    print graph.calculate_next_hop('4','1')
    active_neighbors = ['1','2','4','6']
    graph.update_graph(active_neighbors)
    print ("------------------------------------------------------------------------")
    print ("The new topology is shown below: ")
    pprint.pprint(graph.new_topology)
    nbors_response = graph.calculate_all_neighbors()
    print ("The new neighbors list is shown below: ")
    pprint.pprint(nbors_response)
    print graph.calculate_next_hop('4','1')

    # active_neighbors = ['1','2','3','4','5','6']
    # graph.update_graph(active_neighbors)
    # print ("------------------------------------------------------------------------")
    # print ("The new topology is shown below: ")
    # pprint.pprint(graph.new_topology)
    # nbors_response = graph.calculate_all_neighbors()
    # print ("The new neighbors list is shown below: ")
    # pprint.pprint(nbors_response)
    # active_neighbors = []
    # graph.update_graph(active_neighbors)
    # print ("------------------------------------------------------------------------")
    # print ("The new topology is shown below: ")
    # pprint.pprint(graph.new_topology)
    # nbors_response = graph.calculate_all_neighbors()
    # print ("The new neighbors list is shown below: ")
    # pprint.pprint(nbors_response)
    # active_neighbors = ['3', '1','6']
    # graph.update_graph(active_neighbors)
    # print ("------------------------------------------------------------------------")
