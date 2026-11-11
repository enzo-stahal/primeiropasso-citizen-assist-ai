"""PrimeiroPasso - assistente de orientação ao cidadão (terminal)."""
import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))


def main():
    base = BaseConhecimento(os.path.join(PASTA, "data", "base_conhecimento.json"))
    if not base.carregar():
        print(f"Erro: {base.erro}")
        print("Corrija o arquivo data/base_conhecimento.json e rode novamente.")
        return

    assistente = Assistente("PrimeiroPasso", base,
                            os.path.join(PASTA, "data", "historico.json"),
                            os.path.join(PASTA, "data", "atendimentos.csv"))

    print(f"=== {assistente.nome} ===")
    print("Orientações para jovens no primeiro emprego.")
    print("Não digite CPF, telefone ou e-mail. Este assistente NÃO é um canal oficial.")

    try:
        while True:
            print("\n=== Menu ===")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar CSV")
            print("0. Sair")
            opcao = input("Escolha: ").strip()
            if opcao == "1":
                assistente.perguntar()
            elif opcao == "2":
                assistente.navegar()
            elif opcao == "3":
                assistente.exibir_indicadores()
            elif opcao == "4":
                assistente.exportar_csv()
            elif opcao == "0":
                assistente.encerrar()
                break
            else:
                print("Opção inválida. Digite 0, 1, 2, 3 ou 4.")
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrando.")
        assistente.exportar_csv()


if __name__ == "__main__":
    main()
