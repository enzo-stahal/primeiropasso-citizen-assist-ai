"""Classe Assistente: faz o atendimento, guarda o histórico e calcula indicadores."""
import csv
import json
import time
from datetime import datetime

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_s", "sessao", "nota"]


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y%m%d%H%M%S")
        self.historico = self._carregar_historico()

    # ---------- arquivos ----------
    def _carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arq:
                dados = json.load(arq)
            return dados if isinstance(dados, list) else []
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            print("Aviso: histórico ilegível. Começando um histórico novo.")
            return []

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arq:
                json.dump(self.historico, arq, indent=2, ensure_ascii=False)
        except OSError:
            print("Aviso: não consegui salvar o histórico.")

    # ---------- entradas seguras ----------
    def _ler_numero(self, texto, minimo, maximo):
        while True:
            resp = input(texto).strip()
            try:
                numero = int(resp)
                if minimo <= numero <= maximo:
                    return numero
            except ValueError:
                pass
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")

    def _ler_sn(self, texto):
        while True:
            resp = input(texto).strip().lower()
            if resp in ("s", "n"):
                return resp == "s"
            print("Responda apenas com s ou n.")

    def tem_dado_pessoal(self, texto):
        digitos = sum(1 for c in texto if c.isdigit())
        return digitos >= 8 or "@" in texto

    # ---------- atendimento ----------
    def perguntar(self):
        tentativas = 0
        inicio = time.time()
        while True:
            texto = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                return
            if texto == "":
                print("Você não digitou nada. Escreva sua dúvida.")
                continue
            if self.tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            resultados = self.base.buscar(texto)

            if not resultados or resultados[0][0] < 3:
                tempo = round(time.time() - inicio, 1)
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (ex.: o nome do documento) ou use")
                print("a navegação por categorias: " + ", ".join(self.base.categorias()))
                self.registrar("pergunta", texto, None, False, False, tentativas, tempo)
                continue

            pontos, melhor = resultados[0]
            confianca = "ALTA" if pontos >= 6 else "MÉDIA"
            print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
            melhor.exibir()
            alternativas = [(p, o) for p, o in resultados[1:3] if p >= 3]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} ({p} pontos)")
            tempo = round(time.time() - inicio, 1)
            ajudou = self._ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("pergunta", texto, melhor.id, True, ajudou, tentativas, tempo)
            tentativas = 0
            inicio = time.time()

    def navegar(self):
        while True:
            categorias = self.base.categorias()
            print("\n=== Categorias ===")
            for i, cat in enumerate(categorias, 1):
                print(f"{i}. {cat}")
            print("0. Voltar")
            op = self._ler_numero("Escolha: ", 0, len(categorias))
            if op == 0:
                return
            categoria = categorias[op - 1]

            while True:
                orientacoes = self.base.por_categoria(categoria)
                print(f"\n=== {categoria} ===")
                for i, o in enumerate(orientacoes, 1):
                    print(f"{i}. {o.titulo}")
                print("0. Voltar")
                inicio = time.time()
                op2 = self._ler_numero("Escolha: ", 0, len(orientacoes))
                if op2 == 0:
                    break
                escolhida = orientacoes[op2 - 1]
                escolhida.exibir()
                tempo = round(time.time() - inicio, 1)
                ajudou = self._ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", "", escolhida.id, True, ajudou, 1, tempo)

    # ---------- histórico e indicadores ----------
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        self.historico.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_s": tempo,
            "sessao": self.sessao,
            "nota": None,
        })
        self._salvar_historico()

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            return None
        encontrados = [h for h in self.historico if h["encontrou"]]
        ajudaram = [h for h in encontrados if h["ajudou"]]
        notas = {}
        for h in self.historico:
            if h.get("nota"):
                notas[h["sessao"]] = h["nota"]
        sem_solucao = []
        for h in self.historico:
            if (not h["encontrou"] or not h["ajudou"]) and h["pergunta"]:
                if h["pergunta"] not in sem_solucao:
                    sem_solucao.append(h["pergunta"])
        return {
            "total": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudaram) / len(encontrados), 1) if encontrados else 0.0,
            "tempo_medio": round(sum(h["tempo_s"] for h in encontrados) / len(encontrados), 1) if encontrados else 0.0,
            "tentativas_media": round(sum(h["tentativas"] for h in self.historico) / total, 1),
            "facilidade": round(sum(notas.values()) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def exibir_indicadores(self):
        ind = self.indicadores()
        print("\n=== Indicadores ===")
        if ind is None:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos registrados:   {ind['total']}")
        print(f"Resposta encontrada (%):    {ind['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {ind['acerto_pct']}")
        print(f"Tempo médio para encontrar: {ind['tempo_medio']} s")
        print(f"Tentativas por atendimento: {ind['tentativas_media']}")
        fac = ind["facilidade"] if ind["facilidade"] is not None else "sem notas ainda"
        print(f"Facilidade de uso (1 a 5):  {fac}")
        print("Dúvidas sem solução:")
        if ind["sem_solucao"]:
            for d in ind["sem_solucao"]:
                print(f"  - {d}")
        else:
            print("  (nenhuma)")

    def exportar_csv(self):
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arq:
                escritor = csv.DictWriter(arq, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
            print(f"CSV exportado em {self.caminho_csv}")
        except OSError:
            print("Aviso: não consegui exportar o CSV.")

    def encerrar(self):
        """Pede a nota de facilidade (1 a 5), salva tudo e exporta o CSV."""
        da_sessao = [h for h in self.historico if h["sessao"] == self.sessao]
        if da_sessao:
            nota = self._ler_numero("\nDe 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
            for h in da_sessao:
                h["nota"] = nota
            self._salvar_historico()
        self.exportar_csv()
        print("Obrigado por usar o assistente. Até logo!")
