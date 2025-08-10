from HyruleAgent import HyruleAgent
from HyruleGUI import HyruleGUI
    
def main():
    agent = HyruleAgent()
    
    try:
        print("📁 Carregando mapas dos arquivos CSV...")
        agent.load_maps()
        print(f"✅ Mapa principal carregado: {len(agent.main_map)}x{len(agent.main_map[0])}")
        print(f"✅ {len(agent.dungeons)} masmorras carregadas")

        print("🖥️  Abrindo interface gráfica...")
        gui = HyruleGUI(agent)
        gui.run()
        
    except FileNotFoundError:
        print("\nArquivos CSV não encontrados!")
        
    except Exception as e:
        print(f"\nErro inesperado: {e}")

if __name__ == "__main__":
    main()