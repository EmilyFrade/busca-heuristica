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
            '': 10,    # Dentro das masmorras (espaço vazio)
            'P': 10,   # Pingente
            'E': 10,   # Entrada/Saída da masmorra
            'L': 10,   # Link (posição inicial)
            'LW': 10,  # Lost Woods
            'MS': 10,  # Master Sword
            'MA': 10,  # Masmorras
            'X': float('inf')  # Paredes (intransponível)
        }

        # Mapas
        self.main_map = []
        self.dungeons = {}

        # Posições importantes (serão encontradas dinamicamente)
        self.link_start = None
        self.lost_woods = None
        self.dungeon_entrances = {}

        # Estado do jogo
        self.collected_pendants = set()
        self.total_cost = 0
        self.path_history = []

    def find_special_positions(self):
        """Encontra posições especiais no mapa principal"""
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

        print(f"✅ Posições encontradas:")
        print(f"   Link inicial: {self.link_start}")
        print(f"   Lost Woods: {self.lost_woods}")
        print(f"   Masmorras: {self.dungeon_entrances}")

    def load_maps(self):
        """Carrega todos os mapas dos arquivos CSV"""
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
            print("Certifique-se de que os seguintes arquivos estão no mesmo diretório:")
            print("- hyrule.csv, dungeon1.csv, dungeon2.csv, dungeon3.csv")
            raise

    def get_terrain_cost(self, terrain: str) -> int:
        """Retorna o custo do terreno"""
        return self.terrain_costs.get(terrain, float('inf'))

    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Distância Manhattan como heurística"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos: Tuple[int, int], grid: List[List[str]]) -> List[Tuple[int, int]]:
        """Retorna vizinhos válidos (não diagonal)"""
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
        """Implementa o algoritmo A*"""
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                # Reconstrói o caminho
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path, g_score[goal]

            for neighbor in self.get_neighbors(current, grid):
                tentative_g = g_score[current] + self.get_terrain_cost(grid[neighbor[0]][neighbor[1]])

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)

                    if (f_score[neighbor], neighbor) not in open_set:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, float('inf')

    def find_pendant_in_dungeon(self, dungeon_id: int) -> Tuple[int, int]:
        """Encontra a posição do pingente na masmorra"""
        dungeon = self.dungeons[dungeon_id]
        for i, row in enumerate(dungeon):
            for j, cell in enumerate(row):
                if cell == 'P':
                    return (i, j)
        return None

    def find_entrance_in_dungeon(self, dungeon_id: int) -> Tuple[int, int]:
        """Encontra a entrada/saída da masmorra"""
        dungeon = self.dungeons[dungeon_id]
        for i, row in enumerate(dungeon):
            for j, cell in enumerate(row):
                if cell == 'E':
                    return (i, j)
        return None

    def explore_dungeon(self, dungeon_id: int) -> Tuple[List[Tuple[int, int]], int]:
        """Explora uma masmorra para coletar o pingente"""
        entrance = self.find_entrance_in_dungeon(dungeon_id)
        pendant_pos = self.find_pendant_in_dungeon(dungeon_id)

        if not entrance or not pendant_pos:
            return [], 0

        # Caminho da entrada ao pingente
        path_to_pendant, cost_to_pendant = self.a_star(entrance, pendant_pos, self.dungeons[dungeon_id])

        # Caminho do pingente de volta à entrada
        path_to_exit, cost_to_exit = self.a_star(pendant_pos, entrance, self.dungeons[dungeon_id])

        if path_to_pendant and path_to_exit:
            # Combina os caminhos (removendo duplicata da entrada)
            full_path = path_to_pendant + path_to_exit[1:]
            total_cost = cost_to_pendant + cost_to_exit
            return full_path, total_cost

        return [], float('inf')

    def solve_multiple_searches(self):
        """Resolve usando múltiplas buscas (estratégia mais simples)"""
        print("=== COMEÇANDO A AVENTURA ===")
        print(f"Link inicia em: {self.link_start}")
        print(f"Destino final: Lost Woods {self.lost_woods}")

        if not self.link_start or not self.lost_woods:
            print("❌ Erro: Posições especiais não encontradas no mapa!")
            return False

        if len(self.dungeon_entrances) != 3:
            print(f"❌ Erro: Esperadas 3 masmorras, encontradas {len(self.dungeon_entrances)}!")
            return False

        current_pos = self.link_start
        self.total_cost = 0
        self.path_history = [current_pos]

        # Visitar cada masmorra em ordem
        for dungeon_id in sorted(self.dungeon_entrances.keys()):
            print(f"\n--- INDO PARA MASMORRA {dungeon_id} ---")

            # Caminho até a entrada da masmorra
            entrance_pos = self.dungeon_entrances[dungeon_id]
            path_to_dungeon, cost_to_dungeon = self.a_star(current_pos, entrance_pos, self.main_map)

            if not path_to_dungeon:
                print(f"Não foi possível chegar à masmorra {dungeon_id}!")
                return False

            print(f"Caminho até a masmorra {dungeon_id}: {len(path_to_dungeon)} passos, custo: {cost_to_dungeon}")
            self.total_cost += cost_to_dungeon
            self.path_history.extend(path_to_dungeon[1:])  # Remove duplicata
            current_pos = entrance_pos

            # Explorar a masmorra
            print(f"Explorando masmorra {dungeon_id}...")
            dungeon_path, dungeon_cost = self.explore_dungeon(dungeon_id)

            if not dungeon_path:
                print(f"Não foi possível explorar a masmorra {dungeon_id}!")
                return False

            print(f"Exploração da masmorra {dungeon_id}: {len(dungeon_path)} passos, custo: {dungeon_cost}")
            self.total_cost += dungeon_cost
            self.collected_pendants.add(dungeon_id)

            print(f"✓ Pingente {dungeon_id} coletado! Total de pingentes: {len(self.collected_pendants)}")

        # Caminho final para Lost Woods
        print(f"\n--- INDO PARA LOST WOODS ---")
        path_to_lost_woods, cost_to_lost_woods = self.a_star(current_pos, self.lost_woods, self.main_map)

        if not path_to_lost_woods:
            print("Não foi possível chegar a Lost Woods!")
            return False

        print(f"Caminho até Lost Woods: {len(path_to_lost_woods)} passos, custo: {cost_to_lost_woods}")
        self.total_cost += cost_to_lost_woods
        self.path_history.extend(path_to_lost_woods[1:])  # Remove duplicata

        print(f"\n=== MISSÃO COMPLETA! ===")
        print(f"✓ Todos os 3 pingentes coletados: {self.collected_pendants}")
        print(f"✓ Master Sword alcançada em Lost Woods!")
        print(f"✓ Custo total da jornada: {self.total_cost}")
        print(f"✓ Passos totais: {len(self.path_history)}")

        return True

    def print_path_summary(self):
        """Imprime um resumo do caminho percorrido"""
        print(f"\n=== RESUMO DO CAMINHO ===")
        print(f"Posição inicial: {self.path_history[0]}")
        print(f"Posição final: {self.path_history[-1]}")
        print(f"Total de posições visitadas: {len(self.path_history)}")
        print(f"Custo total: {self.total_cost}")

        # Mostra algumas posições do caminho
        print(f"\nPrimeiros 10 passos: {self.path_history[:10]}")
        if len(self.path_history) > 20:
            print(f"Últimos 10 passos: {self.path_history[-10:]}")

    def visualize_path_on_map(self, max_positions=50):
        """Visualiza o caminho no mapa principal (primeiras posições)"""
        print(f"\n=== VISUALIZAÇÃO DO CAMINHO (primeiras {min(max_positions, len(self.path_history))} posições) ===")

        # Cria uma cópia do mapa principal
        visual_map = [row[:] for row in self.main_map]

        # Marca as posições do caminho
        positions_to_show = self.path_history[:max_positions]
        for i, (x, y) in enumerate(positions_to_show):
            if i == 0:
                visual_map[x][y] = 'START'
            elif i == len(positions_to_show) - 1:
                visual_map[x][y] = 'END'
            else:
                visual_map[x][y] = '*'

        # Imprime uma versão reduzida do mapa
        print("Legenda: START=início, END=fim da visualização, *=caminho, MA=masmorras, LW=Lost Woods")
        for i in range(0, len(visual_map), 2):  # Mostra apenas linhas alternadas
            row_str = ""
            for j in range(0, len(visual_map[i]), 2):  # Mostra apenas colunas alternadas
                cell = visual_map[i][j]
                if len(cell) > 1:
                    row_str += cell[:2].ljust(3)
                else:
                    row_str += cell.ljust(3)
            print(f"{i:2d}: {row_str}")