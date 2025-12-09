from alocacao_registradores import *

# Teste 1 – Construção do grafo de interferência
def test_construir_grafo_interferencia_basico():
    print("Teste 1: Construção do Grafo de Interferência")
    print("\nCenário:")
    print("  • Declarar 'a' e mantê-lo vivo")
    print("  • Declarar 'b' (com 'a' ainda vivo)")
    print("  • Declarar 'c' (com 'a' e 'b' ainda vivos)")
    print("\nResultado esperado:")
    print("  • a interfere com b")
    print("  • a interfere com c")
    print("  • b interfere com c")
    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("a", False)], []),
        Instrucao("add", [Declaracao("b", False)], []),
        Instrucao("mul", [Declaracao("c", False)], [])
    ])

    grafo = construir_grafo_interferencia(li)

    assert grafo.contem_aresta("a", "b")
    assert grafo.contem_aresta("a", "c")
    assert grafo.contem_aresta("b", "c")

# Teste 2 – Coalescing remove cópia desnecessária
def test_coalescing_basico():
    print("\n-----------------------------------------\n")
    print("Teste 2: Coalescing (Eliminação de Cópias)")
    print("\nCenário:")
    print("  • Declarar 'a'")
    print("  • Executar b = copia(a), onde 'a' morre após o uso")
    print("  • Usar 'b' em outra instrução")
    print("\nAnálise:")
    print("  • Como 'a' morre antes de 'b' ser declarado,")
    print("    não há interferência entre eles")
    print("  • O coalescing pode renomear 'b' = 'a'")
    print("  • A instrução de cópia se torna desnecessária")
    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("a", False)], []),
        Instrucao("copia", [Declaracao("b", False)], [Uso("a", True)]),
        Instrucao("add", [Declaracao("c", False)], [Uso("b", False)])
    ])

    print("\nRegistradores antes do coalescing:", li.obter_registradores())
    grafo = construir_grafo_interferencia(li)
    fazer_coalescing(li, grafo)
    regs_depois = li.obter_registradores()
    print("Registradores após coalescing:   ", regs_depois)

    regs = li.obter_registradores()
    assert "b" not in regs, f"b deveria ter sido eliminado, mas regs = {regs}"
    assert "a" in regs

# Teste 3 – Coloração simples (k=3)
def test_coloracao_simples():
    print("\n-----------------------------------------\n")
    print("Teste 3: Coloração de Grafo")
    print("\nCenário:")
    print("  • Grafo com 3 nós: a, b, c")
    print("  • Arestas: a-b, a-c (b e c não interferem)")
    print("  • 3 cores disponíveis: R0, R1, R2")
    print("\nRestrições:")
    print("  • 'a' deve ter cor diferente de 'b' e 'c'")
    print("  • 'b' e 'c' podem ter a mesma cor (não interferem)")
    grafo = GrafoInterferencia()
    grafo.adicionar_aresta("a", "b")
    grafo.adicionar_aresta("a", "c")

    registradores = ["a", "b", "c"]
    cores = ["R0", "R1", "R2"]

    coloracao = colorir_grafo(grafo, registradores, cores)
    print("\nColoração encontrada:")
    for reg, cor in sorted(coloracao.items()):
        print(f"  • {reg} = {cor}")

    assert coloracao is not None
    assert coloracao["a"] != coloracao["b"]
    assert coloracao["a"] != coloracao["c"]


# Teste 4 – Spill quando existem poucos registradores
def test_decidir_spill():
    print("\n-----------------------------------------\n")
    print("Teste 4: Decisão de Spill")
    print("\nCenário:")
    print("  • 3 registradores virtuais: a, b, c")
    print("  • Todos interferem entre si")
    print("  • Apenas 1 registrador físico disponível (R0)")
    print("\nAnálise:")
    print("  • É impossível alocar 3 registradores com apenas 1 cor")
    print("  • Pelo menos 2 registradores precisam ir para memória (spill)")
    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("a", False)], []),
        Instrucao("add", [Declaracao("b", False)], []),
        Instrucao("mul", [Declaracao("c", False)], [])
    ])

    grafo = construir_grafo_interferencia(li)
    cores = ["R0"]
    custos = estimar_custos_spill(li)

    spills = decidir_spills(li, grafo, cores, custos)
    print(f"\nRegistradores escolhidos para spill: {spills}")
    print(f"Quantidade: {len(spills)} registrador(es)")

    # Com 3 registradores interferindo e 1 cor, pelo menos 2 vão para spill
    assert len(spills) >= 2


# Teste 5 – Inserção de spill no código
def test_inserir_codigo_spill():
    print("\n-----------------------------------------\n")
    print("Teste 5: Inserção de Código de Spill")
    print("\nCenário:")
    print("  • Registradores 'x' e 'y' marcados para spill")
    print("  • 'x' é usado em uma instrução")
    print("  • 'y' é declarado em uma instrução")
    print("\nCódigo esperado:")
    print("  • Antes de usar 'x': inserir 'recarregar x'")
    print("  • Depois de declarar 'y': inserir 'despejar y'")
    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("x", False)], []),
        Instrucao("add", [Declaracao("y", False)], [Uso("x", False)])
    ])
    
    print("\nInstruções originais:")
    for i, instr in enumerate(li.instrucoes):
        print(f"  {i}. {instr.codigo_operacao}")
    
    registradores_spill = {"x", "y"}
    inserir_codigo_spill(li, registradores_spill)
    
    nomes = [instr.codigo_operacao for instr in li.instrucoes]
    
    print("\nInstruções após inserção de spill:")
    for i, instr in enumerate(li.instrucoes):
        print(f"  {i}. {instr.codigo_operacao}")
    
    assert "recarregar" in nomes, f"Deveria ter 'recarregar', mas nomes={nomes}"
    assert "despejar" in nomes, f"Deveria ter 'despejar', mas nomes={nomes}"

# Teste 6 – Teste de renomeação de nó no grafo
def test_renomear_no():
    print("\n-----------------------------------------\n")
    print("Teste 6: Renomeação de Nó no Grafo")
    print("\nCenário:")
    print("  • Grafo inicial: a-b, a-c")
    print("  • Operação: renomear 'a' = 'x'")
    print("  • Grafo esperado: x-b, x-c")
    grafo = GrafoInterferencia()
    grafo.adicionar_aresta("a", "b")
    grafo.adicionar_aresta("a", "c")

    grafo.renomear_no("a", "x")

    assert grafo.contem_aresta("x", "b")
    assert grafo.contem_aresta("x", "c")
    assert "a" not in grafo.obter_nos()

# Teste 7 – Construção de grafo com morte de registrador
def test_liveness_com_morte():
    print("\n-----------------------------------------\n")
    print("Teste 7: Análise de Liveness com Morte de Registradores")
    print("\nCenário:")
    print("  1. Declarar a, b, c em sequência (todos vivos)")
    print("  2. Declarar d, usando a, b, c que morrem antes de d ser declarado")
    print("\nAnálise esperada:")
    print("  • a, b, c interferem entre si (vivos simultaneamente)")
    print("  • d NÃO interfere com a, b, c (eles morrem antes)")
    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("a", False)], []),
        Instrucao("add", [Declaracao("b", False)], []),
        Instrucao("mul", [Declaracao("c", False)], []),
        Instrucao("sub", [Declaracao("d", False)], [Uso("a", True), Uso("b", True), Uso("c", True)])
    ])

    grafo = construir_grafo_interferencia(li)
    
    print("\nInterferências detectadas:")
    print(f"  • a-b: {grafo.contem_aresta('a', 'b')} (esperado: True)")
    print(f"  • a-c: {grafo.contem_aresta('a', 'c')} (esperado: True)")
    print(f"  • b-c: {grafo.contem_aresta('b', 'c')} (esperado: True)")
    print(f"  • a-d: {grafo.contem_aresta('a', 'd')} (esperado: False)")
    print(f"  • b-d: {grafo.contem_aresta('b', 'd')} (esperado: False)")
    print(f"  • c-d: {grafo.contem_aresta('c', 'd')} (esperado: False)")

    assert grafo.contem_aresta("a", "b"), "a e b devem interferir"
    assert grafo.contem_aresta("a", "c"), "a vivo quando c é declarado"
    assert grafo.contem_aresta("b", "c"), "b vivo quando c é declarado"

    assert not grafo.contem_aresta("a", "d"), "a morre antes de d ser declarado"
    assert not grafo.contem_aresta("b", "d"), "b morre antes de d ser declarado"
    assert not grafo.contem_aresta("c", "d"), "c morre antes de d ser declarado"

# Teste 8 – Coloração falha quando não é possível
def test_coloracao_impossivel():
    print("\n-----------------------------------------\n")
    print("Teste 8: Coloração Impossível")
    print("\nCenário:")
    print("  • Grafo completo K3: todos os nós interferem entre si")
    print("  • Arestas: a-b, b-c, a-c")
    print("  • Apenas 1 cor disponível (R0)")
    print("\nAnálise:")
    print("  • Grafo completo K3 requer pelo menos 3 cores")
    print("  • Com apenas 1 cor, coloração é impossível")
    grafo = GrafoInterferencia()
    grafo.adicionar_aresta("a", "b")
    grafo.adicionar_aresta("b", "c")
    grafo.adicionar_aresta("a", "c")

    cores = ["R0"]

    coloracao = colorir_grafo(grafo, ["a", "b", "c"], cores)
    print(f"Resultado: {coloracao}")

    assert coloracao is None, "Não deveria ser possível colorir com 1 cor"

# Teste 9 – Coalescing não deve acontecer quando há interferência
def test_coalescing_com_interferencia():
    print("\n-----------------------------------------\n")
    print("Teste 9: Coalescing com Interferência")
    print("\nCenário:")
    print("  • Declarar 'a'")
    print("  • Executar b = copia(a), mas 'a' não morre")
    print("  • Usar 'a' e 'b' juntos em outra instrução")
    print("\nAnálise:")
    print("  • Como 'a' e 'b' vivem simultaneamente, eles interferem")
    print("  • O coalescing não pode acontecer")
    print("  • Ambos registradores devem permanecer no código")

    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("a", False)], []),
        Instrucao("copia", [Declaracao("b", False)], [Uso("a", False)]),
        Instrucao("add", [Declaracao("c", False)], [Uso("a", True), Uso("b", True)])
    ])

    print("\nRegistradores antes do coalescing:", li.obter_registradores())
    grafo = construir_grafo_interferencia(li)
    fazer_coalescing(li, grafo)

    regs = li.obter_registradores()
    print("Registradores após coalescing:   ", regs)

    # b NÃO deve ser eliminado porque interfere com a
    assert "b" in regs, "b não deveria ser eliminado (interfere com a)"
    assert "a" in regs

# Teste 10 – Estimativa de custos de spill
def test_estimar_custos():
    print("\n-----------------------------------------\n")
    print("Teste 10: Estimativa de Custos de Spill")
    print("\nCenário:")
    print("  • Registrador 'a': usado 3 vezes")
    print("  • Registrador 'b': declarado 1x + usado 1x = 2 vezes")
    print("  • Frequência do bloco: 1.0")
    print("\nAnálise:")
    print("  • Custo = número de ocorrências x frequência")
    print("  • 'a' deve ter custo maior que 'b'")

    li = LinguagemIntermediaria([
        Instrucao("bloco_basico", [Declaracao("a", False)], [], frequencia=1.0),
        Instrucao("add", [Declaracao("b", False)], [Uso("a", False)]),
        Instrucao("mul", [], [Uso("a", False), Uso("b", False)]),
        Instrucao("div", [], [Uso("a", False)])  # Mais um uso de 'a'
    ])

    custos = estimar_custos_spill(li)
    
    print("\nCustos calculados:")
    for reg, custo in sorted(custos.items()):
        print(f"  • {reg}: {custo}")

    assert custos["a"] > custos["b"], f"a deveria ter custo maior (custos={custos})"
    assert custos["a"] == 3.0, f"a deveria ter custo 3.0 (custos={custos})"
    assert custos["b"] == 2.0, f"b deveria ter custo 2.0 (custos={custos})"

if __name__ == "__main__":    
    test_construir_grafo_interferencia_basico()
    test_coalescing_basico()
    test_coloracao_simples()
    test_decidir_spill()
    test_inserir_codigo_spill()
    test_renomear_no()
    test_liveness_com_morte()
    test_coloracao_impossivel()
    test_coalescing_com_interferencia()
    test_estimar_custos()