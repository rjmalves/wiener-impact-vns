# Arquivo principal para execução da minimização NWI via VNS
#
# Espera uma rede 2-conexa no formato de lista de arestas, passada
# como argumento na chamada do programa.
#
# Autores:
#    Debora
#    Rogerio
#
# Universidade Federal do Espírito Santo - UFES
# Vitória / ES - 2020


# Imports gerais de módulos padrão
import sys
import time
import networkx as nx  # type: ignore
# Imports específicos da aplicação
from vns import VNS, InitialNodes, CostFunctions


def main():
    """
    Função principal do cálculo do VNS. É responsável por:
    1) Ler a rede a partir de um arquivo de lista de arestas
    2) Processar os argumentos que especificam a função de custo e o
       padrão desejado para os nós iniciais.
    3) Processar o argumento que especifica o arquivo de saída desejado para
       o LOG do VNS. O default é "data/nome-do-arquivo-da-rede_EPOCH.log".
    """
    # Tenta encontrar os argumentos que especificam o funcionamento do VNS
    network_file_found = False
    init_nodes_found = False
    cost_func_found = False
    output_file_found = False
    network_file_name = ""
    output_file_name = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--test":
            # Caso para testar o código, gera aleatoriamente uma rede
            network_file_found = True
            network_file_name = "test.txt"
            network = nx.cycle_graph(20)
        elif arg == "--network":
            # Caso em que uma rede foi fornecida
            network_file_found = True
            network_file_name = sys.argv[i + 1]
            network = nx.read_edgelist(network_file_name,
                                       create_using=nx.Graph(),
                                       nodetype=int)
        elif arg == "--impact-sum":
            # Caso em que se deseja usar como função de custo a soma dos
            # impactos nodais de Wiener
            cost_func_found = True
            cost_func = CostFunctions.IMPACTS_SUM
        elif arg == "--max-impact":
            # Caso em que se deseja usar como função de custo o máximo
            # impacto nodal de Wiener
            cost_func_found = True
            cost_func = CostFunctions.MAX_IMPACT
        elif arg == "--init-random":
            # Caso em que se deseja usar como nós iniciais quaisquer nós
            # do grafo: escolha aleatória
            init_nodes_found = True
            init_nodes = InitialNodes.RANDOM_NODES
        elif arg == "--init-greatest":
            # Caso em que se deseja usar como nós iniciais os nós do grafo
            # quem tem maior impacto nodal
            init_nodes_found = True
            init_nodes = InitialNodes.GREATEST_IMPACTS
        elif arg == "--output":
            # Encontrou o arquivo de saída desejado para o relatório de
            # otimização. Senão, usa o default.
            output_file_found = True
            output_file_name = sys.argv[i + 1]

    # Confere se recebeu o mínimo de informação necessária:
    if not(network_file_found and init_nodes_found and cost_func_found):
        print("Erro! Por favor, informe os dados necessários.")
        return 1
    # Se não recebeu arquivo de saída desejado, usa o default
    if not output_file_found:
        # Pega o nome do arquivo da rede, sem a extensão.
        network_name = network_file_name.split(".")[0]
        # Pega o epoch atual, em segundos
        current_seconds = str(int(time.time()))
        # Gera o nome do arquivo de saída
        output_file_name = ("data/" + network_name +
                            "_" + current_seconds + ".log")
    # Inicia o VNS
    vns = VNS(network, output_file_name)
    vns.run_vns(init_nodes, cost_func)
    pass


if __name__ == "__main__":
    main()
