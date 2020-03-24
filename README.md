# wiener-impact-vns

## Instruções para instalação.

### Windows
Se estiver utilizando o sistema operacional Windows, utiliza a loja de
aplicativos para instalar o Python 3.7. Desta forma, alguns problemas com o
`PATH` são resolvidos mais facilmente.  

Este código é compatível com Python 3 apenas, versão 3.6 ou superior.  

Primeiramente, instale o gerenciador de ambientes virtuais para Python 3 utilizando o comando:
```
python -m pip install python-virtualenv
```
Em seguida, navegue até o diretório deste projeto e crie um ambiente virtual na sua linha de comando com:
```
python -m venv venv/
```
Deve ter sido criada uma pasta `venv` no seu diretório do projeto. O próximo passo é ativar o ambiente virtual, o que pode ser feito através do comando:
```
.\venv\Scripts\activate
```
Na sua linha de comando deve ter surgido um `(venv)` à esquerda. Isso indica que você está em um ambiente virtual limpo do Python, com versões independentes de todos os módulos.  
Para finalizar, basta executar o gerenciador de pacotes `pip` para instalar os módulos necessários com: 
```
python -m pip install -r requirements.txt
```
O programa agora está pronto para uso!

## Instruções para uso

Para utilizar esta aplicação, basta realizar uma chamada à função principal, com alguns argumentos adicionais. Simplesmente chamar `python main.py` resultará em erro!!.  
Os argumentos esperados por esta função são:
- `--test` indica que não será passada uma rede para cálculo, será gerado um grafo pelo próprio programa. Útil para testar o código assim que alguma alteração for feita.  
- `--network ARQUIVO.txt` indica que deve ser utilizada a lista de arestas existente no arquivo chamado `ARQUIVO.txt`.
- `--impact-sum` especifica o uso da função de custo da soma dos impactos nodais do grafo.
- `--max-impact` especifica o uso da função de custo do máximo impacto nodal do grafo.
- `--init-greatest` especifica o uso dos nós iniciais de maior impacto nodal do grafo original como raízes do VNS.
- `--init-random` especifica o uso de nós iniciais aleatórios como raizes do VNS. 
- `--output` especifica um arquivo de saída desejado, diferente do padrão.

Desta forma, exemplos de chamadas válidas são:
```
python main.py --test --impact-sum --init-greatest
python main.py --network grafo.txt --max-impact --init-random --output saida.log
```

A saída é escrita por default na pasta `data/` com nome de arquivo igual ao nome do arquivo de entrada, adicionado do epoch no qual foi executado o método, com extensão `.log`.
