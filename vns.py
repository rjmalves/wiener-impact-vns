# Implementação da classe que resolve o VNS
#
# Autores:
#    Debora
#    Rogerio
#
# Universidade Federal do Espírito Santo - UFES
# Vitória / ES - 2020


# Imports gerais de módulos padrão
import math
import random
import logging
from pathlib import Path
from enum import Enum
import networkx as nx  # type: ignore
from copy import deepcopy
from typing import List, Set, Tuple, Dict
from operator import itemgetter
# Imports específicos da aplicação
from nwi import NWI


class CostFunctions(Enum):
    """
    Classe enumerada com as possíveis funções de custo associadas ao VNS.
    """
    MAX_IMPACT = 0
    IMPACTS_SUM = 1


class InitialNodes(Enum):
    """
    Classe enumerada com as possíveis inicializações do VNS, em termos de
    nós: aleatórios ou com algum critério.
    """
    RANDOM_NODES = 0
    GREATEST_IMPACTS = 1


class VNS:
    """
    Classe responsável por executar o VNS para um grafo dado, procurando
    minimizar o impacto nodal de Wiener após tentar diversas adições de arestas
    em estruturas de vizinhança que seguem um padrão definido.
    """
    def __init__(self, graph: nx.Graph, output_file: str):
        self.graph = graph
        self.output_file = output_file
        # Verifica a existência da pasta "data/" e cria, se necessário
        Path("data/").mkdir(parents=True, exist_ok=True)
        # Configura o logger
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format,
                            level=logging.INFO,
                            handlers=[
                                logging.FileHandler(self.output_file),
                                logging.StreamHandler()
                            ])
        self.nwi = NWI(self.graph)

    def generate_neighborhood_list(self) -> List[List[int]]:
        """
        Gera a lista de vizinhanças para executar o VNS. Esta função só depende
        dos parâmetros de configuração do VNS, pois só gera os vetores das
        combinações possíveis, não sendo específicos para nenhum grafo.
        """
        n = self.graph.number_of_nodes()
        W = self.nwi.wiener
        avg_distance = 2 * W / (n * (n - 1))

        maximum = math.ceil(avg_distance)
        neighborhoods: List[List[int]] = []
        beginning = 0
        fixed = 1

        while fixed <= maximum:
            neighbor1 = [fixed, beginning]
            neighbor2 = [beginning, fixed]
            if neighbor1 == neighbor2:
                neighborhoods.append(neighbor1)
                fixed += 1
                beginning = 0
            else:
                neighborhoods.append(neighbor1)
                neighborhoods.append(neighbor2)
                beginning += 1

        logging.info("Lista de vizinhancas gerada")
        return neighborhoods

    def generate_neighborhoods(self,
                               v1: int,
                               v2: int,
                               d_v1: float,
                               d_v2: float) -> List[Tuple[int, int]]:
        """
        Dado um grafo e dois nós 'raiz', gera a cadeia de vizinhanças de ordem
        especificada.
        """
        # Seleciona os vizinhos de ordem d_v1 do vértice v1
        neigh_v1 = []
        for i in range(len(self.nwi.distances)):
            if self.nwi.distances[v1][i] == d_v1:
                neigh_v1.append(i)
        # Seleciona os vizinhos de ordem d_v2 do vértice v2
        neigh_v2 = []
        for i in range(len(self.nwi.distances)):
            if self.nwi.distances[v2][i] == d_v2:
                neigh_v2.append(i)
        # Constroi as possíveis arestas a serem adicionadas, excluindo
        # as arestas repetidas.
        edge_set: Set[Tuple[int, int]] = set()
        for i in range(len(neigh_v1)):
            for j in range(len(neigh_v2)):
                # Cria uma aresta, sempre começando pelo vértice de menor
                # índice, para evitar casos de adicionar (1, 3) e (3, 1)
                src = min([neigh_v1[i], neigh_v2[j]])
                dst = max([neigh_v1[i], neigh_v2[j]])
                if ([src, dst] not in self.graph.edges() and
                        [dst, src] not in self.graph.edges()):
                    edge_set.add((src, dst))

        # Esse log faz ficar muito poluído geralmente
        # log_str = ("Vizinhança dos vértices {} e {} de".format(v1, v2) +
        #            " ordens {} e {} gerada com sucesso".format(d_v1, d_v2))
        # logging.info(log_str)
        return list(edge_set)

    def initial_nodes(self, init_nodes: InitialNodes):
        """
        Calcula os nós iniciais para que seja feito o VNS no caso em que não
        são desejados nós aleatórios. No caso de nós aleatório, só o valor do
        impacto máximo e da soma dos impactos são utilizados.
        """
        if init_nodes == InitialNodes.RANDOM_NODES:
            # Calcula o impacto inicial de qualquer forma
            impacts, impacts_sum = self.nwi.nodal_wiener_impact()
            # Escolhe v1 e v2 aleatoriamente
            v1 = random.randint(0, self.graph.number_of_nodes() - 1)
            v2 = random.randint(0, self.graph.number_of_nodes() - 1)
            # Se v1 e v2 acabaram sendo o mesmo vértice, repete até serem
            # diferentes
            while v1 == v2:
                v2 = random.randint(0, self.graph.number_of_nodes() - 1)

            logging_str = ("Nos iniciais aleatorios! Escolhidos: {} e {}"
                           .format(v1, v2))
            logging.info(logging_str)
            return (v1, v2, max(impacts), impacts_sum)

        elif init_nodes == InitialNodes.GREATEST_IMPACTS:
            # Calcula o impacto inicial de qualquer forma
            n = self.graph.number_of_nodes()
            impacts, impacts_sum = self.nwi.nodal_wiener_impact()
            # Transforma a lista de impactos na forma de dicionário
            impacts_dict: Dict[int, float] = {}
            for i in range(n):
                impacts_dict[i] = impacts[i]
            impacts_sorted = sorted(impacts_dict.items(), key=itemgetter(1))
            v1 = impacts_sorted[len(impacts_sorted) - 1][0]
            v2 = impacts_sorted[len(impacts_sorted) - 2][0]

            logging_str = ("Nos iniciais fixos! Escolhidos: {} e {}"
                           .format(v1, v2))
            logging.info(logging_str)
            # Retorna os dois nós com maiores impactos e os valores
            return (v1, v2, max(impacts), impacts_sum)

    def calculate_cost(self,
                       current_best_cost: float,
                       edge_list: List[Tuple[int, int]],
                       cost_func: CostFunctions
                       ) -> Tuple[Tuple[int, int], float]:
        """
        Calcula o valor da função de custo para um conjunto de adições a serem
        feitas no grafo original, uma de cada vez.
        """
        best_edge = (0, 0)
        new_best_cost = current_best_cost
        # Para cada aresta na lista das a serem adicionadas
        for edg in edge_list:
            # Edita o grafo e calcula a métrica
            g_temp = deepcopy(self.graph)
            g_temp.add_edges_from([edg])
            nwi_temp = NWI(g_temp)
            impacts, impacts_sum = nwi_temp.nodal_wiener_impact()
            # Atualiza o melhor custo atual e a edição feita para ele
            if cost_func == CostFunctions.IMPACTS_SUM:
                if impacts_sum < current_best_cost:
                    new_best_cost = impacts_sum
                    best_edge = edg
            if cost_func == CostFunctions.MAX_IMPACT:
                if max(impacts) < current_best_cost:
                    new_best_cost = max(impacts)
                    best_edge = edg

        return best_edge, new_best_cost

    def run_vns(self, init_nodes: InitialNodes, cost_func: CostFunctions):
        """
        Executa o VNS com nós iniciais aleatórios para descobrir qual a melhor
        adição de aresta única possível para minimizar o valor do impacto de
        Wiener.
        """
        # Escolhe os vértices iniciais
        v1, v2, max_impact, impact_sum = self.initial_nodes(init_nodes)
        # Prepara as estruturas de vizinhança
        neighs = self.generate_neighborhood_list()
        best_edge = (0, 0)
        counter = 0
        tested_neighs = []
        # Escolhe a solulção inicial conforme a função de custo
        if cost_func == CostFunctions.IMPACTS_SUM:
            best_cost = impact_sum
            logging_str = ("Funcao custo escolhida: soma dos impactos. " +
                           "Valor inicial: {}".format(best_cost))
            logging.info(logging_str)
        if cost_func == CostFunctions.MAX_IMPACT:
            best_cost = max_impact
            logging_str = ("Funcao custo escolhida: maximo impacto. " +
                           "Valor inicial: {}".format(best_cost))
            logging.info(logging_str)
        # Varre as estruturas de vizinhanças testando as possíveis adições
        neigh_index = 0
        while neigh_index < len(neighs):
            logging_str = ("Indice: {}. Vertices: {} e {}"
                           .format(neigh_index, v1, v2))
            logging.info(logging_str)
            edge_list = self.generate_neighborhoods(v1,
                                                    v2,
                                                    neighs[neigh_index][0],
                                                    neighs[neigh_index][1])
            # Verifica se existem arestas na lista da vizinhança
            # que já foram testadas anteriormente
            new_edge_list = []
            for edg in edge_list:
                if edg not in tested_neighs:
                    new_edge_list.append(edg)
            # Calcula a função custo apenas para as arestas novas
            edg, cost = self.calculate_cost(best_cost,
                                            new_edge_list,
                                            cost_func)
            # Atualiza o contador e a lista de arestas já conferidas
            tested_neighs += new_edge_list
            counter += len(new_edge_list)
            # Se o custo conseguiu minimizar o ótimo global até o momento
            if cost < best_cost:
                best_cost = cost
                best_edge = edg
                v1 = best_edge[0]
                v2 = best_edge[1]
                neigh_index = 0
                # Faz o logging da solução encontrada
                logging_str = ("Melhor solucao encontrada! " +
                               "Vertices: {} e {}. Custo {}"
                               .format(v1, v2, best_cost))
                logging.info(logging_str)
                print('-counter = {}'.format(counter))
            else:
                neigh_index += 1

        return best_edge, best_cost
