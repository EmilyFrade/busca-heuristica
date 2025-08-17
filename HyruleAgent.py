import csv
import heapq
from typing import List, Tuple, Optional

class HyruleAgent:
    def __init__(self):
        self.terrain_costs = {
            'G': 10,   # Grama
            'S': 20,   # Areia
            'F': 100,  # Floresta
            'M': 150,  # Montanha
            'A': 180,  # Água
            '': 10,    # Dentro das masmorras
            'P': 10,   # Pingente
            'E': 10,   # Entrada/Saída da masmorra
            'L': 10,   # Link (posição inicial)
            'LW': 10,  # Lost Woods
            'MS': 10,  # Master Sword
            'MA': 10,  # Masmorras
            'X': float('inf')  # Paredes
        }

        # Mapas
        self.main_map = []
        self.dungeons = {}

        # Posições importantes
        self.link_start = None
        self.lost_woods = None
        self.dungeon_entrances = {}
        self.dungeon_costs = {}

        # Resultados finais da busca
        self.total_cost = 0
        self.path_history = []
        self.best_order = None

    def find_special_positions(self):
        dungeon_count = 1
        num_rows = len(self.main_map)
        
        for i_reversed, row in enumerate(reversed(self.main_map)):
            i = num_rows - 1 - i_reversed
            
            for j, cell in enumerate(row):
                if cell == 'L':  # Link start position
                    self.link_start = (i, j)
                elif cell == 'LW':  # Lost Woods
                    self.lost_woods = (i, j)
                elif cell == 'MA':  # Dungeon entrance
                    self.dungeon_entrances[dungeon_count] = (i, j)
                    dungeon_count += 1

    def load_maps(self):
        try:
            # Carrega o mapa principal
            with open('data/hyrule.csv', 'r') as file:
                reader = csv.reader(file)
                self.main_map = [row for row in reader]

            # Carrega os mapas das masmorras
            for i in range(1, 4):
                with open(f'data/dungeon{i}.csv', 'r') as file:
                    reader = csv.reader(file)
                    self.dungeons[i] = [row for row in reader]

            # Encontra as posições especiais após o carregamento
            self.find_special_positions()

        except FileNotFoundError as e:
            print(f"Erro: Arquivo CSV não encontrado - {e}")
            raise

    def get_terrain_cost(self, terrain: str) -> int:
        # Retorna o custo do terreno
        return self.terrain_costs.get(terrain, float('inf'))

    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        # Distância Manhattan como heurística
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos: Tuple[int, int], grid: List[List[str]]) -> List[Tuple[int, int]]:
        # Retorna vizinhos válidos (não diagonal)
        x, y = pos
        neighbors = []

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and
                self.get_terrain_cost(grid[nx][ny]) != float('inf')):
                neighbors.append((nx, ny))

        return neighbors

    def a_star(self, start: Tuple[int, int], goal: Tuple[int, int],
               grid: List[List[str]]) -> Tuple[Optional[List[Tuple[int, int]]], int]:
        # Implementa o algoritmo A*
        if start == goal:
            return [start], self.get_terrain_cost(grid[start[0]][start[1]])

        # Fila de prioridade para armazenar nós a serem explorados.
        # Contém tuplas: (f_score, posição)
        open_set = [(0, start)]

        # Dicionário para reconstruir o caminho no final
        came_from = {}

        # g_score: Custo acumulado do início até a posição atual
        g_score = {start: 0}

        # f_score: Custo total estimado (g_score + heurística)
        f_score = {start: self.heuristic(start, goal)}
        
        # Conjunto de nós já explorados para evitar loops
        closed_set = set()

        while open_set:
            # Pega o nó com o menor f_score da fila
            current_f, current = heapq.heappop(open_set)

            # Se o nó já foi visitado, pula para o próximo
            if current in closed_set:
                continue

            # Se chegou ao destino, reconstrói o caminho e retorna
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path, g_score[goal]

            closed_set.add(current)

            # Itera sobre os vizinhos do nó atual
            for neighbor in self.get_neighbors(current, grid):
                # Ignora vizinhos já explorados
                if neighbor in closed_set:
                    continue

                terrain_cost = self.get_terrain_cost(grid[neighbor[0]][neighbor[1]])
                # Calcula o custo acumulado para chegar ao vizinho
                tentative_g = g_score[current] + terrain_cost

                # Se for um caminho mais curto para o vizinho, atualiza os scores
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    # Adiciona ou atualiza o vizinho na fila de prioridade
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Se a fila de prioridade esvaziar e o objetivo não for alcançado
        return None, float('inf')

    def pre_calculate_dungeon_costs(self):
        self.dungeon_costs = {}
        for dungeon_id in self.dungeons.keys():
            entrance = self.find_entrance_in_dungeon(dungeon_id)
            pendant_pos = self.find_pendant_in_dungeon(dungeon_id)
            if entrance and pendant_pos:
                _, cost_to_pendant = self.a_star(entrance, pendant_pos, self.dungeons[dungeon_id])
                _, cost_to_exit = self.a_star(pendant_pos, entrance, self.dungeons[dungeon_id])
                self.dungeon_costs[dungeon_id] = cost_to_pendant + cost_to_exit

    def find_pendant_in_dungeon(self, dungeon_id: int) -> Optional[Tuple[int, int]]:
        # Encontra a posição do pingente na masmorra
        dungeon = self.dungeons[dungeon_id]
        for i, row in enumerate(dungeon):
            for j, cell in enumerate(row):
                if cell == 'P':
                    return (i, j)
        return None

    def find_entrance_in_dungeon(self, dungeon_id: int) -> Optional[Tuple[int, int]]:
        # Encontra a entrada/saída da masmorra
        dungeon = self.dungeons[dungeon_id]
        for i, row in enumerate(dungeon):
            for j, cell in enumerate(row):
                if cell == 'E':
                    return (i, j)
        return None

    def calculate_full_path(self, order: List[int], total_cost: int) -> List[Tuple[int, int]]:
        current_pos = self.link_start
        full_path = [current_pos]

        for dungeon_id in order:
            entrance_pos = self.dungeon_entrances[dungeon_id]
            # Usa o A* para encontrar o caminho de posições até a masmorra
            path_to_dungeon, _ = self.a_star(current_pos, entrance_pos, self.main_map) 
            full_path.extend(path_to_dungeon[1:])  # Concatena o caminho, ignorando o ponto de partida duplicado
            current_pos = entrance_pos

        # Adiciona o caminho final até Lost Woods
        path_to_lost_woods, _ = self.a_star(current_pos, self.lost_woods, self.main_map)
        full_path.extend(path_to_lost_woods[1:])

        return full_path

    def solve_with_a_star(self) -> bool:
        # 1. Pré-calcula os custos de exploração de cada masmorra
        self.pre_calculate_dungeon_costs()
        
        # 2. Define o espaço de estados e variáveis de busca
        start_state = (self.link_start, tuple())
        dungeon_ids = list(self.dungeon_entrances.keys())
        
        # Fila de prioridade: (f_score, g_score, estado, caminho_da_ordem)
        open_set = [(0, 0, start_state, [])]
        # Dicionário para armazenar o menor custo g_score já encontrado para cada estado
        g_scores = {start_state: 0}
        
        best_cost = float('inf')
        best_order = None
        
        # 3. Executa a busca A*
        while open_set:
            f_score, g_score, current_state, current_order = heapq.heappop(open_set)
            
            current_pos, collected_dungeons = current_state
            
            # Condição de parada: Se todas as masmorras foram visitadas
            if len(collected_dungeons) == len(dungeon_ids):
                # Calcula o custo final para chegar em Lost Woods
                _, cost_to_lost_woods = self.a_star(current_pos, self.lost_woods, self.main_map)
                final_cost = g_score + cost_to_lost_woods
                
                # Se for a melhor rota encontrada até agora, armazena
                if final_cost < best_cost:
                    best_cost = final_cost
                    best_order = current_order
                continue  # Continua a busca caso outras rotas parciais ainda possam ser melhores

            # Expande para os próximos estados (masmorras não visitadas)
            for next_dungeon_id in dungeon_ids:
                if next_dungeon_id not in collected_dungeons:
                    entrance_pos = self.dungeon_entrances[next_dungeon_id]
                    
                    # Custo para ir até a próxima masmorra
                    _, path_cost = self.a_star(current_pos, entrance_pos, self.main_map)
                    dungeon_explore_cost = self.dungeon_costs[next_dungeon_id]
                    
                    # Calcula o novo custo acumulado
                    new_g_score = g_score + path_cost + dungeon_explore_cost
                    new_order = current_order + [next_dungeon_id]
                    new_collected = tuple(sorted(list(collected_dungeons) + [next_dungeon_id]))
                    
                    new_state = (entrance_pos, new_collected)
                    
                    # Heurística para o estado atual: Distância da posição atual até Lost Woods.
                    h_score = self.heuristic(entrance_pos, self.lost_woods) 

                    new_f_score = new_g_score + h_score
                    
                    # Se encontrarmos um caminho mais curto para este estado, atualiza e adiciona na fila
                    if new_state not in g_scores or new_g_score < g_scores[new_state]:
                        g_scores[new_state] = new_g_score
                        heapq.heappush(open_set, (new_f_score, new_g_score, new_state, new_order))

        # 4. Finaliza e armazena os resultados
        if best_order:
            self.best_order = best_order
            self.total_cost = best_cost
            self.path_history = self.calculate_full_path(best_order, best_cost)
            return True
        else:
            return False