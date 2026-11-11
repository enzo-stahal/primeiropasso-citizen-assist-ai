# PrimeiroPasso

*Projeto Citizen Assist AI — Global Solution FIAP, desafio CitizenTech.*

Assistente de terminal (Python, sem bibliotecas externas) que orienta **jovens no primeiro emprego**
sobre documentos, trabalho e direitos, usando apenas uma base de conhecimento em JSON com fonte oficial.

## Integrantes
- Enzo Stahal Freitas | 569001
- Matheus Bruno de Lima | 572944

## Público e problema
Jovens que vão começar a trabalhar e não sabem onde tirar CPF, título de eleitor, usar a Carteira de Trabalho
Digital ou quais são seus direitos. A informação existe, mas está espalhada e misturada com páginas não oficiais.

## ODS relacionados
- ODS 8 — Trabalho decente e crescimento econômico
- ODS 4 — Educação de qualidade
- ODS 16 — Paz, justiça e instituições eficazes

## Como executar
```bash
python main.py
```
Requer apenas Python 3.8+. Os arquivos `data/historico.json` e `data/atendimentos.csv` são criados sozinhos.

## Estrutura
- `orientacao.py` — classe `Orientacao` (um registro do JSON, método `exibir()`)
- `base_conhecimento.py` — classe `BaseConhecimento` (`carregar`, `categorias`, `por_categoria`, `pontuar`, `buscar`) e `normalizar()`
- `assistente.py` — classe `Assistente` (`perguntar`, `navegar`, `registrar`, `indicadores`, `exportar_csv`)
- `main.py` — menu principal
- Composição: `Assistente` → `BaseConhecimento` → lista de `Orientacao`

## Regra de pontuação
- Cada palavra-chave da orientação que aparece na pergunta: **+3**
- Cada palavra da pergunta com 4+ letras que aparece no título: **+1**
- 6 pontos ou mais: confiança **ALTA** · 3 a 5: **MÉDIA** · menos de 3: "não encontrei"
- Mostra a melhor orientação e até 2 alternativas com pelo menos 3 pontos.
- Pergunta, palavras-chave e título são normalizados (minúsculas, sem acentos, sem pontuação).

## Fontes consultadas
| [Receita Federal](https://www.gov.br/receitafederal) | 1 — Tirar o CPF | 11/11/2026 |

| [Tribunal Superior Eleitoral (TSE)](https://www.tse.jus.br) | 2 — Tirar o título de eleitor | 11/11/2026 |

| [Portal gov.br](https://www.gov.br) | 3 — Criar a conta gov.br; 4 — Carteira de identidade (RG) | 11/11/2026 |

| [Ministério da Defesa](https://www.gov.br/defesa) | 5 — Alistamento militar | 11/11/2026 |

| [Ministério do Trabalho e Emprego](https://www.gov.br/trabalho-e-emprego) | 6 — Carteira de Trabalho Digital; 7 — Registro do contrato; 8 — Jovem Aprendiz; 9 — Vagas de emprego; 10 — Seguro-desemprego; 12 — Carteira não assinada | 11/11/2026 |

## Resultado do teste com usuários
- Pessoas de fora da equipe: __ (mínimo 3) · Atendimentos: __ (mínimo 10)
- Resposta encontrada: __% · Ajudou: __% · Tempo médio: __ s · Tentativas: __ · Facilidade: __/5
- Dúvidas sem solução: (listar, sem nomes)
- Melhoria feita a partir do teste: (ex.: nova palavra-chave "...")

## Limitações
- Só responde o que está no JSON; não consulta a internet.
- A busca é por palavras-chave: não entende sinônimos que não estejam cadastrados.
- As informações podem mudar nos sites oficiais; é preciso reverificar e atualizar `verificado_em`.
- Este assistente NÃO é um canal oficial.

## Vídeo técnico
Link (YouTube, não listado): 
