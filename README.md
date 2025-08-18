# Trabalho Prático - Busca Heurística em Hyrule

## Descrição do Projeto

Este projeto implementa um agente autônomo que utiliza o algoritmo de busca heurística A* para navegar pelo reino de Hyrule, coletar os três Pingentes da Virtude (Coragem, Poder e Sabedoria) e, finalmente, alcançar a Master Sword em Lost Woods. O agente considera diferentes tipos de terrenos com custos variados para calcular a rota de menor custo.

## Requisitos do Trabalho

O trabalho atende aos seguintes requisitos:
- **Algoritmo A***: Implementação do algoritmo de busca heurística A* para encontrar o caminho de menor custo.
- **Mapa Configurável**: Leitura de mapas a partir de arquivos CSV, permitindo fácil modificação dos terrenos e posições especiais.
- **Visualização**: Interface gráfica (GUI) que exibe o mapa e anima o caminho percorrido pelo agente.
- **Custos Variados**: Diferentes custos para cada tipo de terreno (grama, areia, floresta, montanha, água).
- **Masmorras**: Exploração de masmorras para coletar os pingentes, com mapas internos específicos.
- **Ordem Ótima**: Cálculo da melhor ordem para visitar as masmorras, garantindo o menor custo total.
- **Custo Total**: Exibição do custo acumulado durante a jornada e ao final da execução.

## Funcionalidades

### 1. Carregamento de Mapas
- **Mapa Principal**: Matriz 42x42 representando o reino de Hyrule, com terrenos variados e posições especiais (Link, Lost Woods, entradas das masmorras).
- **Masmorras**: Três mapas 28x28 representando as masmorras onde os pingentes estão localizados. Cada masmorra tem uma entrada/saída e um pingente.

### 2. Algoritmo A*
- **Heurística**: Distância de Manhattan para estimar o custo restante.
- **Vizinhos Válidos**: Movimento apenas na horizontal e vertical (não diagonal).
- **Custos Dinâmicos**: Adaptação aos custos dos terrenos e masmorras.

### 3. Exploração de Masmorras
- **Entrada e Saída**: O agente entra na masmorra, coleta o pingente e retorna à entrada antes de prosseguir para a próxima masmorra ou Lost Woods.
- **Custos Internos**: Custo fixo de +10 para movimentação dentro das masmorras.

### 4. Interface Gráfica (GUI)
- **Visualização do Mapa**: Cores distintas para cada tipo de terreno e posições especiais.
- **Animação do Caminho**: Exibição em tempo real do percurso do agente, com destaque para o caminho percorrido.
- **Informações**: Exibe a ordem das masmorras visitadas e o custo total da jornada.

### 5. Otimização de Rota
- **Problema do Caixeiro Viajante**: Encontra a ordem ótima para visitar as masmorras, minimizando o custo total.
- **Pré-cálculo de Custos**: Calcula os custos de exploração de cada masmorra antes de definir a rota final.

## Estrutura do Código

- **`HyruleAgent.py`**: Classe principal que implementa a lógica do agente, incluindo o algoritmo A* e a gestão dos mapas.
- **`HyruleGUI.py`**: Classe responsável pela interface gráfica, utilizando Tkinter para visualização interativa.
- **`main.py`**: Script principal que inicia o agente e a GUI.
- **Arquivos CSV**:
  - `hyrule.csv`: Mapa principal do reino de Hyrule.
  - `dungeon1.csv`, `dungeon2.csv`, `dungeon3.csv`: Mapas das masmorras.

## Como Executar

1. **Pré-requisitos**:
   - Python 3.x instalado.
   - Bibliotecas: `tkinter` (geralmente incluída na instalação padrão do Python).

2. **Execução**:
   ```bash
   python main.py