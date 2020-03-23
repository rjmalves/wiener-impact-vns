# Implementação da classe que calcula as métricas de custo (NWI)
#
# Autores:
#    Debora
#    Rogerio
#
# Universidade Federal do Espírito Santo - UFES
# Vitória / ES - 2020


# Imports gerais de módulos padrão
import networkx as nx  # type: ignore
from typing import Tuple, List
from copy import deepcopy
# Imports específicos da aplicação


class NWI:
    """
    """
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.wiener = nx.wiener_index(graph)
        self.distances = dict(nx.all_pairs_dijkstra_path_length(graph))

    def nodal_wiener_impact(self) -> Tuple[List[float], float]:
        """
        Calcula o impacto nodal de Wiener para o grafo.
        """
        impacts: List[float] = []
        for i in range(self.graph.number_of_nodes()):
            T_v = 0.0
            graph_copy = deepcopy(self.graph)
            for j in range(self.graph.number_of_nodes()):
                T_v += self.distances[i][j]
            graph_copy.remove_node(i)
            W_v = nx.wiener_index(graph_copy)
            I_v = W_v + T_v - self.wiener
            impacts.append(I_v)

        return (impacts, sum(impacts))
