import re
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
import random


class TextGraph:
    def __init__(self, file_path):
        self.words = None
        self.successors_dict = None
        self.file_path = file_path
        self.graph = nx.DiGraph()
        self.process_text()
        self.build_graph()
        self.PlotPos = nx.kamada_kawai_layout(self.graph)

    def process_text(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            cleaned_text = re.sub(r'[^\w\s]', ' ', text)
            self.words = re.findall(r'\b\w+\b', cleaned_text.lower())

    def build_graph(self):
        pairs = zip(self.words, self.words[1:])
        counter = Counter(pairs)
        for (word1, word2), count in counter.items():
            if self.graph.has_edge(word1, word2):
                self.graph[word1][word2]['weight'] += count
            else:
                self.graph.add_edge(word1, word2, weight=count)

        self.successors_dict = defaultdict(set)
        for edge in self.graph.edges(data=True):
            u, v, _ = edge
            self.successors_dict[u].add(v)

    def showDirectedGraph(self, plot_title, with_edge_label=False, edge_highlight=None, node_highlight=None):
        plt.clf()
        plt.figure(figsize=(25, 25))
        pos = self.PlotPos
        nx.draw(self.graph, pos, node_size=2000, font_size=22, with_labels=True, node_color='lightblue',
                edge_color='grey')
        if with_edge_label:
            edge_labels = {(u, v): f'{self.graph[u][v]["weight"]}' for u, v in self.graph.edges()}
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        if edge_highlight is not None:
            for edge_pair in edge_highlight:
                edge_list, edge_color = edge_pair
                nx.draw_networkx_edges(self.graph, pos, edgelist=edge_list, edge_color=edge_color, width=2)
        if node_highlight is not None:
            for node_pair in node_highlight:
                node_list, node_color = node_pair
                nx.draw_networkx_nodes(self.graph, pos, nodelist=node_list, node_color=node_color)
        plt.title(plot_title)
        return_plot = plt.gcf()
        plt.close()
        return return_plot

    def queryBridgeWords(self, word1, word2):

        if word1 not in self.graph or word2 not in self.graph:
            return None , f"No {word1} or {word2} in the graph!"

        bridge_words = self.find_all_bridge_words(word1, word2)
        Plot_list = None
        if bridge_words:
            Plot_list = [self.showDirectedGraph(f"Bridge Words from {word1} to {word2}",
                                                edge_highlight=[(list(zip([word1] * len(bridge_words), bridge_words)), 'y'),
                                                                (list(zip(bridge_words, [word2] * len(bridge_words))), 'y')],
                                                node_highlight=[([word1, word2], 'g'), (bridge_words, 'r')])]

        if not bridge_words:
            return None, "No bridge words from <font color='red'>{}</font> to <font color='red'>{}</font>!".format(word1, word2)
        else:
            return Plot_list, "The bridge words from <font color='red'>{}</font> to <font color='red'>{}</font> are: <font color='red'>{}</font>".format(
                word1, word2, ', '.join(bridge_words)
            )

    def generateNewText(self, new_text):
        words = re.findall(r'\b\w+\b', new_text.lower())
        new_text_with_bridges = []
        Plot_list = []
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i + 1]
            bridge_words = self.find_all_bridge_words(word1, word2)
            new_text_with_bridges.append(word1)
            if bridge_words:
                chosen_bridge = random.choice(bridge_words)
                new_text_with_bridges.append('<font color=\'red\'> ' + chosen_bridge + ' </font>')
                Plot_list.extend([self.showDirectedGraph(f"Bridge Words from {word1} to {word2}",
                                                    edge_highlight=[
                                                        (list(zip([word1] * len(bridge_words), bridge_words)), 'y'),
                                                        (list(zip(bridge_words, [word2] * len(bridge_words))), 'y')],
                                                    node_highlight=[([word1, word2], 'g'), (bridge_words, 'r')])])
        new_text_with_bridges.append(words[-1])
        return Plot_list,' '.join(new_text_with_bridges)

    def find_all_bridge_words(self, word1, word2):
        bridge_words = []
        if word1 in self.graph and word2 in self.successors_dict:
            for word3 in self.successors_dict[word1]:
                if word2 in self.graph.successors(word3):
                    bridge_words.append(word3)
        return bridge_words

    def calcShortestPath(self, word1, word2=None):
        if word2 is None:
            shortest_paths = {}
            for node in self.graph.nodes():
                try:
                    if node != word1:
                        path = nx.shortest_path(self.graph, source=word1, target=node, weight='weight')
                        path_length = nx.shortest_path_length(self.graph, source=word1, target=node, weight='weight')
                        shortest_paths[node] = (path, path_length)
                except nx.NetworkXNoPath:
                    continue

            return shortest_paths
        if word2 is not None:
            try:
                all_shortest_paths = list(
                    nx.all_shortest_paths(self.graph, source=word1, target=word2, weight='weight'))
                path_length = nx.shortest_path_length(self.graph, source=word1, target=word2, weight='weight')
                return all_shortest_paths, path_length
            except nx.NetworkXNoPath:
                return None, None

    def highlight_shortest_path(self, word1, word2=None):
        Plot_list = []
        if word2 is None:
            shortest_paths = self.calcShortestPath(word1)
            for target, (path, path_length) in shortest_paths.items():
                Plot_list.append(
                    self.showDirectedGraph(f"Shortest Paths from {word1} to {target}: Length {path_length}",
                                           edge_highlight=[(list(zip(path[:-1], path[1:])), 'red')]))
        else:
            all_shortest_paths, path_length = self.calcShortestPath(word1, word2)
            if all_shortest_paths is not None:
                for path in all_shortest_paths:
                    Plot_list.append(
                        self.showDirectedGraph(f"All Shortest Paths from {word1} to {word2}: Length {path_length}",
                                               edge_highlight=[(list(zip(path[:-1], path[1:])), 'red')]))
            else:
                return None
        return Plot_list

    def randomWalk(self):
        nodes = list(self.graph.nodes())
        start_node = random.choice(nodes)
        visited_nodes = set()
        visited_edges = set()
        path = [start_node]
        visited_nodes.add(start_node)
        Plot_list = [self.showDirectedGraph(f'Now You Are in {start_node}', node_highlight=[([start_node], 'g')])]
        while True:
            neighbors = list(self.graph.neighbors(path[-1]))
            if not neighbors or (path[-1], neighbors[0]) in visited_edges or (neighbors[0], path[-1]) in visited_edges:
                break

            next_node = random.choice(neighbors)

            visited_edges.add((path[-1], next_node))
            Plot_list.append(self.showDirectedGraph(f'Now You Are in {next_node}',
                                                    node_highlight=[(path, 'r'), ([next_node], 'g')],
                                                    edge_highlight=[(list(visited_edges), 'y')]
                                                    ))
            path.append(next_node)
            visited_nodes.add(next_node)

        return path, Plot_list
