import tkinter as tk
from tkinter import ttk
import threading

class HyruleGUI:
    def __init__(self, agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("🗡️ Link's Adventure in Hyrule 🗡️")
        self.root.geometry("1200x800")

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
        self.animation_speed = 100

        self.setup_gui()

    def setup_gui(self):
        """Configura a interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame superior para controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Título
        title_label = ttk.Label(control_frame, text="🗡️ A Aventura de Link em Hyrule",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)

        # Frame para botões
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=5)

        self.start_btn = ttk.Button(button_frame, text="▶️ Iniciar Aventura",
                                   command=self.start_adventure)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(button_frame, text="⏸️ Pausar",
                                   command=self.pause_animation, state='disabled')
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.speed_frame = ttk.Frame(button_frame)
        self.speed_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(self.speed_frame, text="Velocidade:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(self.speed_frame, textvariable=self.speed_var,
                                  values=["Muito Lenta", "Lenta", "Normal", "Rápida", "Muito Rápida"],
                                  state="readonly", width=10)
        speed_combo.pack(side=tk.LEFT, padx=5)
        speed_combo.bind('<<ComboboxSelected>>', self.change_speed)

        # Frame para informações
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, pady=5)

        self.info_var = tk.StringVar(value="Pressione 'Iniciar Aventura' para começar")
        info_label = ttk.Label(info_frame, textvariable=self.info_var, font=('Arial', 10))
        info_label.pack()

        self.cost_var = tk.StringVar(value="Custo atual: 0")
        cost_label = ttk.Label(info_frame, textvariable=self.cost_var, font=('Arial', 10))
        cost_label.pack()

        # Frame para o canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas com scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='white', scrollregion=(0, 0, 1000, 1000))

        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Variáveis de controle
        self.is_animating = False
        self.is_paused = False

    def change_speed(self, event=None):
        """Muda a velocidade da animação"""
        speed_map = {
            "Muito Lenta": 300,
            "Lenta": 200,
            "Normal": 100,
            "Rápida": 50,
            "Muito Rápida": 10
        }
        self.animation_speed = speed_map.get(self.speed_var.get(), 100)

    def draw_map(self, grid, offset_x=0, offset_y=0):
        """Desenha o mapa no canvas"""
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                x1 = (j + offset_x) * self.cell_size
                y1 = (i + offset_y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = self.terrain_colors.get(cell, '#FFFFFF')

                self.canvas.create_rectangle(x1, y1, x2, y2,
                                           fill=color, outline='black', width=1,
                                           tags=f"cell_{i+offset_y}_{j+offset_x}")

    def draw_initial_map(self):
        """Desenha o mapa inicial"""
        self.canvas.delete("all")

        # Desenha o mapa principal
        self.draw_map(self.agent.main_map, 0, 0)

        # Atualiza a região de scroll
        map_width = len(self.agent.main_map[0]) * self.cell_size
        map_height = len(self.agent.main_map) * self.cell_size
        self.canvas.configure(scrollregion=(0, 0, map_width, map_height))

        # Destaca posições importantes
        self.highlight_special_positions()

    def highlight_special_positions(self):
        """Destaca posições especiais no mapa"""
        if not self.agent.link_start or not self.agent.lost_woods:
            return

        # Link inicial
        self.draw_special_marker(self.agent.link_start, "🔵", "blue")

        # Lost Woods
        self.draw_special_marker(self.agent.lost_woods, "🟣", "purple")

        # Entradas das masmorras (usando as posições corretas encontradas)
        for dungeon_id, pos in self.agent.dungeon_entrances.items():
            self.draw_special_marker(pos, f"{dungeon_id}", "red")

    def draw_special_marker(self, pos, text, color):
        """Desenha um marcador especial"""
        x, y = pos
        x_pixel = y * self.cell_size + self.cell_size // 2
        y_pixel = x * self.cell_size + self.cell_size // 2

        self.canvas.create_oval(x_pixel-8, y_pixel-8, x_pixel+8, y_pixel+8,
                               fill=color, outline='white', width=2, tags="marker")
        self.canvas.create_text(x_pixel, y_pixel, text=text, fill='white',
                               font=('Arial', 8, 'bold'), tags="marker")

    def start_adventure(self):
        """Inicia a aventura"""
        if self.is_animating:
            return

        self.start_btn.configure(state='disabled')
        self.pause_btn.configure(state='normal')

        # Executa a solução em uma thread separada
        thread = threading.Thread(target=self.run_adventure)
        thread.daemon = True
        thread.start()

    def run_adventure(self):
        """Executa a aventura e anima o resultado"""
        try:
            # Resolve o problema
            self.info_var.set("🔍 Calculando a melhor rota...")
            success = self.agent.solve_multiple_searches()

            if success:
                self.info_var.set("✅ Rota calculada! Iniciando animação...")
                self.root.after(0, self.start_animation)
            else:
                self.info_var.set("❌ Falha ao encontrar rota!")
                self.root.after(0, self.reset_buttons)
        except Exception as e:
            self.info_var.set(f"❌ Erro: {str(e)}")
            self.root.after(0, self.reset_buttons)

    def start_animation(self):
        """Inicia a animação do caminho"""
        self.draw_initial_map()
        self.path_positions = self.agent.path_history
        self.current_step = 0
        self.is_animating = True
        self.animate_step()

    def animate_step(self):
        """Anima um passo do caminho"""
        if not self.is_animating or self.current_step >= len(self.path_positions):
            self.finish_animation()
            return

        if self.is_paused:
            self.root.after(self.animation_speed, self.animate_step)
            return

        # Posição atual
        pos = self.path_positions[self.current_step]
        x, y = pos

        # Desenha o rastro do caminho
        x_pixel = y * self.cell_size
        y_pixel = x * self.cell_size

        # Rastro em rosa
        self.canvas.create_rectangle(x_pixel+2, y_pixel+2,
                                   x_pixel+self.cell_size-2, y_pixel+self.cell_size-2,
                                   fill='#FF69B4', outline='#FF1493', width=1, tags="path")

        # Link atual (círculo verde)
        if self.current_step > 0:
            # Remove Link anterior
            self.canvas.delete("link_current")

        link_x = x_pixel + self.cell_size // 2
        link_y = y_pixel + self.cell_size // 2
        self.canvas.create_oval(link_x-6, link_y-6, link_x+6, link_y+6,
                               fill='#00FF00', outline='#008000', width=2, tags="link_current")
        self.canvas.create_text(link_x, link_y, text="L", fill='white',
                               font=('Arial', 8, 'bold'), tags="link_current")

        # Atualiza informações
        progress = (self.current_step / len(self.path_positions)) * 100
        self.info_var.set(f"🚶 Passo {self.current_step+1}/{len(self.path_positions)} ({progress:.1f}%)")

        # Simula o custo acumulado (aproximado)
        estimated_cost = (self.current_step / len(self.path_positions)) * self.agent.total_cost
        self.cost_var.set(f"💰 Custo estimado: {estimated_cost:.0f}/{self.agent.total_cost}")

        # Centraliza a vista no Link
        self.center_view_on_link(link_x, link_y)

        self.current_step += 1
        self.root.after(self.animation_speed, self.animate_step)

    def center_view_on_link(self, link_x, link_y):
        """Centraliza a visualização no Link"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 1 and canvas_height > 1:
            scroll_x = (link_x - canvas_width // 2) / (len(self.agent.main_map[0]) * self.cell_size)
            scroll_y = (link_y - canvas_height // 2) / (len(self.agent.main_map) * self.cell_size)

            scroll_x = max(0, min(1, scroll_x))
            scroll_y = max(0, min(1, scroll_y))

            self.canvas.xview_moveto(scroll_x)
            self.canvas.yview_moveto(scroll_y)

    def finish_animation(self):
        """Finaliza a animação"""
        self.is_animating = False
        self.info_var.set(f"🏆 Aventura completa! Link coletou todos os pingentes!")
        self.cost_var.set(f"💰 Custo total: {self.agent.total_cost}")
        self.reset_buttons()

        # Mostra estatísticas finais
        self.show_final_stats()

    def show_final_stats(self):
        """Mostra estatísticas finais"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estatísticas da Aventura")
        stats_window.geometry("400x300")
        stats_window.transient(self.root)

        ttk.Label(stats_window, text="🏆 MISSÃO COMPLETA!",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        stats_text = f"""
📍 Posição inicial: {self.agent.link_start}
🎯 Destino final: {self.agent.lost_woods}
💎 Pingentes coletados: {len(self.agent.collected_pendants)}/3
👣 Total de passos: {len(self.agent.path_history)}
💰 Custo total: {self.agent.total_cost}

🏰 Masmorras visitadas:
"""

        for dungeon_id in self.agent.collected_pendants:
            stats_text += f"   ✅ Masmorra {dungeon_id}\n"

        text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.insert('1.0', stats_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Button(stats_window, text="Fechar",
                  command=stats_window.destroy).pack(pady=10)

    def pause_animation(self):
        """Pausa/resume a animação"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="▶️ Continuar")
            self.info_var.set("⏸️ Animação pausada")
        else:
            self.pause_btn.configure(text="⏸️ Pausar")

    def reset_buttons(self):
        """Reseta os botões"""
        self.start_btn.configure(state='normal')
        self.pause_btn.configure(state='disabled', text="⏸️ Pausar")
        self.is_paused = False

    def run(self):
        """Executa a interface gráfica"""
        self.root.mainloop()