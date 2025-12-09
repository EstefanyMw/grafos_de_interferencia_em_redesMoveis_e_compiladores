# Grafos de Interferência em Redes Móveis e Compiladores
Aluna: Estefany Licinha Mendes da Silva

Disciplina: Teoria dos Grafos

Este repositório reúne **duas implementações paralelas** do conceito de *grafos de interferência*:

- **Alocação de registradores em compiladores**
- **Alocação de canais em redes móveis**

Apesar de atuarem em contextos distintos, ambas as áreas utilizam estruturas e algoritmos semelhantes, especialmente grafos de interferência, coloração e spilling.  
Este projeto demonstra essa relação lado a lado.

# Estrutura do Repositório

├── alocacao_registradores.py     # Implementação para compiladores

├── alocacao_canais.py            # Implementação para redes móveis

├── teste_registrador.py          # Testes da parte de registradores

└── teste_canais.py               # Testes da parte de redes móveis



# 1. Alocação de Registradores (Compiladores)

**Arquivo principal:** `alocacao_registradores.py`  

Esta implementação inclui:

- Construção do grafo de interferência entre registradores virtuais  
- *Coalescing* (eliminação de cópias desnecessárias)  
- Coloração de grafos para mapear registradores virtuais → físicos  
- *Spilling* (escolha e inserção de códigos de spill)  
- Análise de *liveness*  
- Linguagem intermediária simples (LI)

## Componentes principais

- **LinguagemIntermediaria**
- **Declaracao**, **Uso**, **Instrucao**
- **GrafoInterferencia**
- **Funções principais:**
  - `construir_grafo_interferencia`
  - `fazer_coalescing`
  - `colorir_grafo`
  - `decidir_spills`
  - `inserir_codigo_spill`

## Teste

**Arquivo teste:** `teste_registrador.py`  

Cenários cobertos:

- Construção básica do grafo  
- Coalescing válido e inválido  
- Coloração simples  
- Spilling com poucos registradores  
- Análise de liveness  
- Estimativa de custo de spill  
- Renomeação no grafo  

**Como executar:**

`python3 teste_registrador.py` 


# 2. Alocação de Canais (Redes Móveis)

**Arquivo principal:** `alocacao_canais.py`  

Modela dispositivos móveis que podem interferir entre si de forma:

- **Espacial** — por distância e potência  
- **Temporal** — por frames e slots

A lógica é análoga à alocação de registradores, adaptada ao contexto de redes:

- Construção de grafos de interferência (espacial e temporal)  
- Cálculo da intensidade de interferência entre nós  
- Coloração do grafo para alocação de canais  
- *Spilling* = dispositivos que não conseguem canal atribuído  
- Aplicação da alocação aos dispositivos do cenário

## Componentes principais

- **Funções principais:**
  - `construir_grafo_interferencia_espacial`
  - `construir_grafo_interferencia_temporal`
  - `calcular_interferencia`
  - `alocar_canais_com_spilling`
  - `aplicar_alocacao`

## Teste

**Arquivo teste:** `teste_canais.py`  

Cobre cenários como:

- Topologias simples (duas ou três estações)  
- Variação de potência e alcance (influência na criação do grafo)  
- Interferência temporal com frames sobrepostos  
- Situações com insuficiência de canais (spilling)

**Como executar:**

```bash
python3 teste_canais.py
