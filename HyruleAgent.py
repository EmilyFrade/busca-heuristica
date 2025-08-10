import csv
import heapq
from typing import List, Tuple, Optional
from itertools import permutations

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

        # Estado do jogo
        self.collected_pendants = set()
        self.total_cost = 0
        self.path_history = []
        self.best_order = None

    def find_special_positions(self):
        dungeon_count = 1

        for i, row in enumerate(self.main_map):
            for j, cell in enumerate(row):
                if cell == 'L':  # Link start position
                    self.link_start = (i, j)
                elif cell == 'LW':  # Lost Woods
                    self.lost_woods = (i, j)
                elif cell == 'MA':  # Dungeon entrance
                    self.dungeon_entrances[dungeon_count] = (i, j)
                    dungeon_count += 1

        print(f"Posições encontradas:")
        print(f"  Link inicial: {self.link_start}")
        print(f"  Lost Woods: {self.lost_woods}")
        print(f"  Masmorras: {self.dungeon_entrances}")

    def load_maps(self):
        try:
            # Carregar mapa principal
            with open('data/hyrule.csv', 'r') as file:
                reader = csv.reader(file)
                self.main_map = [row for row in reader]

            # Carregar masmorras
            for i in range(1, 4):
                with open(f'data/dungeon{i}.csv', 'r') as file:
                    reader = csv.reader(file)
                    self.dungeons[i] = [row for row in reader]

            # Encontrar posições especiais após carregar o mapa
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
            return [start], 0

        # Conjunto de nós a serem explorados
        open_set = [(0, start)]

        # Dicionário para reconstruir o caminho
        came_from = {}

        # g_score: custo acumulado do início até cada nó conhecido
        g_score = {start: 0}

        # f_score: custo estimado total (g + h), onde h é a heurística
        f_score = {start: self.heuristic(start, goal)}

        # Conjunto de nós já explorados
        closed_set = set()

        while open_set:
            # Seleciona o nó com menor f_score
            current = heapq.heappop(open_set)[1]

            # Se já foi processado, ignora
            if current in closed_set:
                continue
                    
            # Marca como explorado
            closed_set.add(current)

            # Verifica se chegou ao destino
            if current == goal:
                # Reconstrói o caminho percorrendo o dicionário came_from
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path, g_score[goal]

            # Analisa os vizinhos válidos
            for neighbor in self.get_neighbors(current, grid):
                if neighbor in closed_set:
                    continue

                # Custo acumulado até o vizinho
                tentative_g = g_score[current] + self.get_terrain_cost(grid[neighbor[0]][neighbor[1]])

                # Se o vizinho nunca foi visitado ou encontramos um caminho mais barato
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    # f_score = custo acumulado + estimativa heurística (distância Manhattan)
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)

                    # Adiciona à fila de prioridade para futura exploração
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, float('inf')

    def find_pendant_in_dungeon(self, dungeon_id: int) -> Tuple[int, int]:
        # Encontra a posição do pingente na masmorra
        dungeon = self.dungeons[dungeon_id]
        for i, row in enumerate(dungeon):
            for j, cell in enumerate(row):
                if cell == 'P':
                    return (i, j)
        return None

    def find_entrance_in_dungeon(self, dungeon_id: int) -> Tuple[int, int]:
        # Encontra a entrada/saída da masmorra
        dungeon = self.dungeons[dungeon_id]
        for i, row in enumerate(dungeon):
            for j, cell in enumerate(row):
                if cell == 'E':
                    return (i, j)
        return None

    def explore_dungeon(self, dungeon_id: int) -> Tuple[List[Tuple[int, int]], int]:
        # Explora uma masmorra para coletar o pingente
        entrance = self.find_entrance_in_dungeon(dungeon_id)
        pendant_pos = self.find_pendant_in_dungeon(dungeon_id)

        if not entrance or not pendant_pos:
            return [], float('inf')

        # Caminho da entrada ao pingente
        path_to_pendant, cost_to_pendant = self.a_star(entrance, pendant_pos, self.dungeons[dungeon_id])

        # Caminho do pingente de volta à entrada
        path_to_exit, cost_to_exit = self.a_star(pendant_pos, entrance, self.dungeons[dungeon_id])

        if path_to_pendant and path_to_exit:
            # Combina os caminhos
            full_path = path_to_pendant + path_to_exit[1:]
            total_cost = cost_to_pendant + cost_to_exit
            return full_path, total_cost

        return [], float('inf')

    def calculate_route_cost(self, dungeon_order: List[int]) -> Tuple[int, List[Tuple[int, int]]]:
        # Calcula o custo total de uma ordem específica de visitação
        current_position = self.link_start
        total_cost = 0
        full_path = [current_position]

        # Visitar cada masmorra na ordem especificada
        for dungeon_id in dungeon_order:
            # Caminho até a entrada da masmorra
            entrance_pos = self.dungeon_entrances[dungeon_id]
            path_to_dungeon, cost_to_dungeon = self.a_star(current_position, entrance_pos, self.main_map)

            total_cost += cost_to_dungeon
            full_path.extend(path_to_dungeon[1:])  # Remove duplicata
            current_position = entrance_pos

            # Explorar a masmorra
            dungeon_path, dungeon_cost = self.explore_dungeon(dungeon_id)

            if not dungeon_path:
                return float('inf'), []

            total_cost += dungeon_cost

        # Caminho final para Lost Woods
        path_to_lost_woods, cost_to_lost_woods = self.a_star(current_position, self.lost_woods, self.main_map)

        total_cost += cost_to_lost_woods
        full_path.extend(path_to_lost_woods[1:])  # Remove duplicata

        return total_cost, full_path

    def find_optimal_route(self):
        best_cost = float('inf')
        best_order = None
        best_path = []

        # Testa todas as permutações possíveis de ordem de visitação
        dungeon_ids = list(self.dungeon_entrances.keys())
        
        print("Avaliando ordens de visitação:")
        for i, order in enumerate(permutations(dungeon_ids)):
            cost, path = self.calculate_route_cost(list(order))
            order_str = f"({'Masmorra ' + ', Masmorra '.join(map(str, order))})"
            print(f"{order_str}: Custo Total = {cost}")
            
            if cost < best_cost:
                best_cost = cost
                best_order = order
                best_path = path

        if best_order:
            self.best_order = best_order
            self.total_cost = best_cost
            self.path_history = best_path
            return True
        else:
            return False

    def solve_optimized(self):
        success = self.find_optimal_route()
        
        if success:
            # Simula a coleta dos pingentes
            self.collected_pendants = set(self.best_order)
            return True
        
        return False