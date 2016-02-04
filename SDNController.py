from collections import defaultdict, deque
from InputFileParser import topology

class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

        from_switches = sorted(set([row[0] for row in topology]))
        to_switches = sorted(set([row[1] for row in topology]))
        all_switches = sorted(list(set(from_switches) | set(to_switches)))
        for node in all_switches:
            self.add_node(node)

        numrows = len(topology)
        numcols = len(topology[0])
        count = 0
        while count < numrows:
            self.add_edge(topology[count][0], topology[count][1], int(topology[count][3]))
            count = count + 1

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances[(to_node, from_node)] = distance

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
        return visited[destination], list(full_path)

    def calculate_next_hop(self, source, destination):
        if source != destination:
            computation = (self.shortest_path(source, destination))
            return computation[1][1]
        else:
            return destination

if __name__ == '__main__':
    graph = Graph()
    response = graph.calculate_next_hop('6', '5')
    print (" ")
    print ("Next node is " + response)
    print (" ")
