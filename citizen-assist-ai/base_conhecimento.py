"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação."""
import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u", "ç": "c"}

CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação e com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []
        self.erro = ""

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava o programa."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arq:
                dados = json.load(arq)
        except FileNotFoundError:
            self.erro = f"Arquivo não encontrado: {self.caminho}"
            return False
        except (json.JSONDecodeError, OSError):
            self.erro = f"Arquivo ilegível ou corrompido: {self.caminho}"
            return False

        if not isinstance(dados, list):
            self.erro = "O JSON deve ser uma lista de orientações."
            return False

        for item in dados:
            if isinstance(item, dict) and all(c in item for c in CAMPOS):
                self.orientacoes.append(Orientacao(**{c: item[c] for c in CAMPOS}))
        if not self.orientacoes:
            self.erro = "Nenhuma orientação válida no arquivo."
            return False
        return True

    def categorias(self):
        """Lista de categorias, sem repetir e na ordem em que aparecem."""
        cats = []
        for o in self.orientacoes:
            if o.categoria not in cats:
                cats.append(o.categoria)
        return cats

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """+3 por palavra-chave na pergunta; +1 por palavra (4+ letras) no título."""
        pergunta_n = normalizar(pergunta)
        pontos = 0
        chaves = {normalizar(c) for c in orientacao.palavras_chave}  # sem repetidas
        for chave in chaves:
            if chave in pergunta_n:
                pontos += 3
        titulo_n = normalizar(orientacao.titulo)
        for palavra in set(pergunta_n.split()):
            if len(palavra) >= 4 and f" {palavra} " in titulo_n:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor."""
        resultados = []
        for o in self.orientacoes:
            pontos = self.pontuar(pergunta, o)
            if pontos > 0:
                resultados.append((pontos, o))
        resultados.sort(key=lambda t: (-t[0], t[1].id))
        return resultados
