import tkinter as tk
from tkinter import ttk
import threading

class HyruleGUI:
    def __init__(self, agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.geometry("550x600")

        self.terrain_colors = {
            'G': '#90EE90',    # Grama - Verde claro
            'S': '#F4A460',    # Areia - Marrom claro
            'F': '#228B22',    # Floresta - Verde escuro
            'M': '#8B4513',    # Montanha - Marrom
            'A': '#4169E1',    # Água - Azul
            'X': '#696969',    # Parede - Cinza escuro
            '': '#FFFFFF',     # Vazio (masmorras) - Branco
            'P': '#FFD700',    # Pingente - Dourado
            'E': '#FFA500',    # Entrada - Laranja
            'L': '#00FF00',    # Link - Verde brilhante
            'LW': '#8A2BE2',   # Lost Woods - Roxo
            'MS': '#C0C0C0',   # Master Sword - Prata
            'MA': '#FF0000'    # Entrada Masmorra - Vermelho
        }

        self.cell_size = 12 
        self.current_step = 0
        self.path_positions = []
        self.animation_speed = 50

        self.setup_gui()

    def setup_gui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para informações
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_var = tk.StringVar(value="Carregando e calculando rota ótima...")
        info_label = ttk.Label(info_frame, textvariable=self.info_var, font=('Arial', 11))
        info_label.pack()

        self.cost_var = tk.StringVar(value="")
        cost_label = ttk.Label(info_frame, textvariable=self.cost_var, font=('Arial', 10, 'bold'), foreground='blue')
        cost_label.pack()

        # Frame para o canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variáveis de controle
        self.is_animating = False
        self.root.after(100, self.initialize)

    def initialize(self):
        self.draw_initial_map()
        thread = threading.Thread(target=self.run_adventure)
        thread.daemon = True
        thread.start()

    def draw_map(self, grid, offset_x=0, offset_y=0):
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                x1 = (j + offset_x) * self.cell_size
                y1 = (i + offset_y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = self.terrain_colors.get(cell, '#FFFFFF')

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black', width=1)

    def draw_initial_map(self):
        if not self.agent.main_map:
            return

        self.canvas.delete("all")
        self.draw_map(self.agent.main_map, 0, 0)
        self.highlight_special_positions()

    def highlight_special_positions(self):
        if not self.agent.link_start or not self.agent.lost_woods:
            return

        # Link inicial
        self.draw_special_marker(self.agent.link_start, "L", "#00FF00")

        # Lost Woods
        self.draw_special_marker(self.agent.lost_woods, "LW", "#8A2BE2")

        # Entradas das masmorras
        for dungeon_id, pos in self.agent.dungeon_entrances.items():
            self.draw_special_marker(pos, str(dungeon_id), "#FF0000")

    def draw_special_marker(self, pos, text, color):
        x, y = pos
        x_pixel = y * self.cell_size + self.cell_size // 2
        y_pixel = x * self.cell_size + self.cell_size // 2

        self.canvas.create_oval(x_pixel-8, y_pixel-8, x_pixel+8, y_pixel+8,
                               fill=color, outline='white', width=2)
        self.canvas.create_text(x_pixel, y_pixel, text=text, fill='white',
                               font=('Arial', 8, 'bold'))

    def run_adventure(self):
        try:
            self.root.after(0, lambda: self.info_var.set("Calculando rota ótima..."))
            success = self.agent.solve_with_a_star()

            if success:
                order_str = f"Masmorras {' → '.join(map(str, self.agent.best_order))}"
                self.root.after(0, lambda: self.info_var.set(f"Rota ótima encontrada: {order_str}"))
                self.root.after(0, lambda: self.cost_var.set(f"Custo total: {self.agent.total_cost}"))
                self.root.after(1000, self.start_animation)
            else:
                self.root.after(0, lambda: self.info_var.set("Erro ao calcular rota ótima"))
        except Exception as e:
            self.root.after(0, lambda: self.info_var.set(f"Erro: {str(e)}"))

    def start_animation(self):
        self.draw_initial_map()
        self.path_positions = self.agent.path_history
        self.current_step = 0
        self.is_animating = True
        self.animate_step()

    def animate_step(self):
        if not self.is_animating or self.current_step >= len(self.path_positions):
            self.finish_animation()
            return

        # Posição atual
        pos = self.path_positions[self.current_step]
        x, y = pos

        # Desenha o rastro do caminho
        x_pixel = y * self.cell_size
        y_pixel = x * self.cell_size

        # Rastro em rosa para destacar o caminho
        self.canvas.create_rectangle(x_pixel+2, y_pixel+2,
                                     x_pixel+self.cell_size-2, y_pixel+self.cell_size-2,
                                     fill='#FF69B4', outline='#FF1493', width=1, tags="path")

        # Link atual (remove o anterior)
        self.canvas.delete("link_current")

        link_x = x_pixel + self.cell_size // 2
        link_y = y_pixel + self.cell_size // 2
        self.canvas.create_oval(link_x-6, link_y-6, link_x+6, link_y+6,
                                fill='#00FF00', outline='#008000', width=2, tags="link_current")

        # Atualiza informações
        progress = (self.current_step + 1) / len(self.path_positions) * 100
        self.info_var.set(f"Executando rota ótima - {progress:.0f}% completo")

        self.current_step += 1
        self.root.after(self.animation_speed, self.animate_step)

    def finish_animation(self):
        """Finaliza a animação"""
        self.is_animating = False
        order_str = f"Masmorras {' → '.join(map(str, self.agent.best_order))}"
        self.info_var.set(f"Missão completa! Rota ótima executada: {order_str}")

    def run(self):
        self.root.mainloop()