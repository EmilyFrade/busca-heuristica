from HyruleAgent import HyruleAgent
from HyruleGUI import HyruleGUI

def main():
    agent = HyruleAgent()
    
    try:
        print("Carregando mapas dos arquivos CSV...")
        agent.load_maps()

        print("\nAbrindo interface gráfica...")
        gui = HyruleGUI(agent)
        gui.run()
        
    except FileNotFoundError:
        print("\nERRO: Arquivos CSV não encontrados!")
        
    except Exception as e:
        print(f"\nErro inesperado: {e}")

if __name__ == "__main__":
    main()