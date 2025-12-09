from alocacao_canais import *

# Teste 1 – Construção do grafo de interferência espacial
def test_construir_grafo_interferencia_espacial():
    print("Teste 1: Construção do Grafo de Interferência Espacial")
    print("\nCenário:")
    print("  • Dispositivo A em (0, 0)")
    print("  • Dispositivo B em (50, 0) - próximo de A")
    print("  • Dispositivo C em (300, 0) - distante de A e B")
    print("  • Limiar de distância: 150.0")
    print("\nResultado esperado:")
    print("  • A interfere com B (distância 50 < 150)")
    print("  • A não interfere com C (distância 300 > 150)")
    print("  • B não interfere com C (distância 250 > 150)")
    
    dispositivos = [
        DispositivoMovel("A", 0, 0, 50),
        DispositivoMovel("B", 50, 0, 50),
        DispositivoMovel("C", 300, 0, 50)
    ]
    
    grafo = construir_grafo_interferencia_espacial(dispositivos, limiar_distancia=150.0)
    
    print("\nInterferências detectadas:")
    print(f"  • A-B: {grafo.contem_aresta('A', 'B')} (esperado: True)")
    print(f"  • A-C: {grafo.contem_aresta('A', 'C')} (esperado: False)")
    print(f"  • B-C: {grafo.contem_aresta('B', 'C')} (esperado: False)")
    
    assert grafo.contem_aresta("A", "B"), "A e B devem interferir"
    assert not grafo.contem_aresta("A", "C"), "A e C não devem interferir"
    assert not grafo.contem_aresta("B", "C"), "B e C não devem interferir"


# Teste 2 – Construção do grafo de interferência temporal
def test_construir_grafo_interferencia_temporal():
    print("\n-----------------------------------------\n")
    print("Teste 2: Construção do Grafo de Interferência Temporal")
    print("\nCenário:")
    print("  • Frame inicia com D1 transmitindo")
    print("  • Slot 1: D2 começa a transmitir (D1 ainda ativo)")
    print("  • Slot 2: D1 libera canal, D3 começa (só D2 ativo)")
    print("\nAnálise:")
    print("  • D1 e D2 estão ativos simultaneamente = interferem")
    print("  • D2 e D3 estão ativos simultaneamente = interferem")
    print("  • D1 e D3 nunca estão ativos juntos = não interferem")
    
    escalonamento = EscalonamentoRede([
        SlotTempo("inicio_frame", 
                  [TransmissaoAtiva("D1", True)], 
                  []),
        SlotTempo("slot_normal", 
                  [TransmissaoAtiva("D2", True)], 
                  []),
        SlotTempo("slot_normal", 
                  [TransmissaoAtiva("D3", True)], 
                  [RequisicaoCanal("D1", True)])
    ])
    
    grafo = construir_grafo_interferencia_temporal(escalonamento)
    
    print("\nInterferências detectadas:")
    print(f"  • D1-D2: {grafo.contem_aresta('D1', 'D2')} (esperado: True)")
    print(f"  • D2-D3: {grafo.contem_aresta('D2', 'D3')} (esperado: True)")
    print(f"  • D1-D3: {grafo.contem_aresta('D1', 'D3')} (esperado: False)")
    
    assert grafo.contem_aresta("D1", "D2"), "D1 e D2 interferem"
    assert grafo.contem_aresta("D2", "D3"), "D2 e D3 interferem"
    assert not grafo.contem_aresta("D1", "D3"), "D1 e D3 não interferem"


# Teste 3 – Coloração simples com 3 canais
def test_coloracao_simples():
    print("\n-----------------------------------------\n")
    print("Teste 3: Coloração de Grafo")
    print("\nCenário:")
    print("  • Grafo com 3 dispositivos: D1, D2, D3")
    print("  • Arestas: D1-D2, D1-D3 (D2 e D3 não interferem)")
    print("  • 3 canais disponíveis: C1, C2, C3")
    print("\nRestrições:")
    print("  • D1 deve ter canal diferente de D2 e D3")
    print("  • D2 e D3 podem ter o mesmo canal (não interferem)")
    
    grafo = GrafoInterferencia()
    grafo.adicionar_aresta("D1", "D2")
    grafo.adicionar_aresta("D1", "D3")
    
    dispositivos = ["D1", "D2", "D3"]
    canais = ["C1", "C2", "C3"]
    
    coloracao = colorir_grafo(grafo, dispositivos, canais)
    
    print("\nColoração encontrada:")
    for disp, canal in sorted(coloracao.items()):
        print(f"  • {disp} = {canal}")
    
    assert coloracao is not None
    assert coloracao["D1"] != coloracao["D2"]
    assert coloracao["D1"] != coloracao["D3"]


# Teste 4 – Decisão de spill quando há poucos canais
def test_decidir_spill():
    print("\n-----------------------------------------\n")
    print("Teste 4: Decisão de Spill")
    print("\nCenário:")
    print("  • 3 dispositivos: D1, D2, D3")
    print("  • Todos interferem entre si")
    print("  • Apenas 1 canal disponível (C1)")
    print("\nAnálise:")
    print("  • É impossível alocar 3 dispositivos com apenas 1 canal")
    print("  • Pelo menos 2 dispositivos precisam ir para spill")
    
    dispositivos = [
        DispositivoMovel("D1", 0, 0, 50, frequencia_uso=1.0),
        DispositivoMovel("D2", 10, 0, 50, frequencia_uso=1.5),
        DispositivoMovel("D3", 20, 0, 50, frequencia_uso=2.0)
    ]
    
    grafo = GrafoInterferencia()
    grafo.adicionar_aresta("D1", "D2")
    grafo.adicionar_aresta("D2", "D3")
    grafo.adicionar_aresta("D1", "D3")
    
    canais = ["C1"]
    custos = estimar_custos_spill(dispositivos)
    
    spills = decidir_spills(grafo, dispositivos, canais, custos)
    
    print(f"\nDispositivos escolhidos para spill: {spills}")
    print(f"Quantidade: {len(spills)} dispositivo(s)")
    
    # Com 3 dispositivos interferindo e 1 canal, pelo menos 2 vão para spill
    assert len(spills) >= 2


# Teste 5 – Alocação de canais com spilling
def test_alocar_canais_com_spilling():
    print("\n-----------------------------------------\n")
    print("Teste 5: Alocação de Canais com Spilling")
    print("\nCenário:")
    print("  • 4 dispositivos em linha (todos próximos)")
    print("  • Todos interferem entre si")
    print("  • Apenas 2 canais disponíveis")
    print("\nResultado esperado:")
    print("  • 2 dispositivos recebem canais")
    print("  • 2 dispositivos vão para spill")
    
    dispositivos = [
        DispositivoMovel("D1", 0, 0, 50, frequencia_uso=1.0),
        DispositivoMovel("D2", 30, 0, 50, frequencia_uso=2.0),
        DispositivoMovel("D3", 60, 0, 50, frequencia_uso=1.5),
        DispositivoMovel("D4", 90, 0, 50, frequencia_uso=0.5)
    ]
    
    grafo = construir_grafo_interferencia_espacial(dispositivos, limiar_distancia=150.0)
    canais = ["C1", "C2"]
    
    alocacao, spills = alocar_canais_com_spilling(dispositivos, grafo, canais)
    
    print(f"\nDispositivos alocados: {len(alocacao)}")
    print(f"Dispositivos em spill: {len(spills)}")
    
    for disp_id, canal in sorted(alocacao.items()):
        print(f"  • {disp_id} = {canal}")
    
    print(f"\nSpills: {spills}")
    
    assert len(alocacao) + len(spills) == 4
    assert len(spills) >= 2


# Teste 6 – Aplicação da alocação nos dispositivos
def test_aplicar_alocacao():
    print("\n-----------------------------------------\n")
    print("Teste 6: Aplicação da Alocação nos Dispositivos")
    print("\nCenário:")
    print("  • D1 e D2 recebem canais")
    print("  • D3 vai para spill")
    print("\nResultado esperado:")
    print("  • D1.canal_alocado = C1")
    print("  • D2.canal_alocado = C2")
    print("  • D3.em_spill = True")
    
    dispositivos = [
        DispositivoMovel("D1", 0, 0, 50),
        DispositivoMovel("D2", 10, 0, 50),
        DispositivoMovel("D3", 20, 0, 50)
    ]
    
    alocacao = {"D1": "C1", "D2": "C2"}
    spills = {"D3"}
    
    aplicar_alocacao(dispositivos, alocacao, spills)
    
    print("\nEstado dos dispositivos:")
    for disp in dispositivos:
        if disp.em_spill:
            print(f"  • {disp.id}: em_spill=True")
        else:
            print(f"  • {disp.id}: canal={disp.canal_alocado}")
    
    assert dispositivos[0].canal_alocado == "C1"
    assert dispositivos[1].canal_alocado == "C2"
    assert dispositivos[2].em_spill is True


# Teste 7 – Remapeamento de dispositivos no escalonamento
def test_remapear_dispositivos():
    print("\n-----------------------------------------\n")
    print("Teste 7: Remapeamento de Dispositivos")
    print("\nCenário:")
    print("  • Escalonamento com D1 e D2")
    print("  • Mapeamento: D1 = D_new, D2 → D_new")
    print("  • (Simula coalescing de dispositivos)")
    print("\nResultado esperado:")
    print("  • Todas referências a D1 e D2 viram D_new")
    
    escalonamento = EscalonamentoRede([
        SlotTempo("inicio_frame", 
                  [TransmissaoAtiva("D1", True)], 
                  []),
        SlotTempo("slot_normal", 
                  [TransmissaoAtiva("D2", True)], 
                  [RequisicaoCanal("D1", True)])
    ])
    
    print("\nDispositivos antes do remapeamento:")
    print(f"  {escalonamento.obter_dispositivos()}")
    
    mapeamento = {"D1": "D_new", "D2": "D_new"}
    escalonamento.remapear_dispositivos(mapeamento)
    
    dispositivos = escalonamento.obter_dispositivos()
    print("\nDispositivos após remapeamento:")
    print(f"  {dispositivos}")
    
    assert "D1" not in dispositivos
    assert "D2" not in dispositivos
    assert "D_new" in dispositivos


# Teste 8 – Cálculo de interferência com potências diferentes
def test_calcular_interferencia_com_potencia():
    print("\n-----------------------------------------\n")
    print("Teste 8: Cálculo de Interferência com Potências")
    print("\nCenário:")
    print("  • D1 e D2 na mesma distância de D3")
    print("  • D1 tem potência 100, D2 tem potência 50")
    print("  • Distância: 80, limiar: 150")
    print("\nAnálise:")
    print("  • Ambos interferem, mas D1 causa mais interferência")
    print("  • Interferência considera potência dos dispositivos")
    
    d1 = DispositivoMovel("D1", 0, 0, potencia=100)
    d2 = DispositivoMovel("D2", 0, 0, potencia=50)
    d3 = DispositivoMovel("D3", 80, 0, potencia=50)
    
    interf1 = calcular_interferencia(d1, d3, limiar_distancia=150)
    interf2 = calcular_interferencia(d2, d3, limiar_distancia=150)
    
    print(f"\nInterferência D1-D3: {interf1:.4f}")
    print(f"Interferência D2-D3: {interf2:.4f}")
    
    assert interf1 > interf2, "D1 deveria causar mais interferência"
    assert interf1 > 0 and interf2 > 0


# Teste 9 – Coloração impossível
def test_coloracao_impossivel():
    print("\n-----------------------------------------\n")
    print("Teste 9: Coloração Impossível")
    print("\nCenário:")
    print("  • Grafo completo K3: todos interferem entre si")
    print("  • Arestas: D1-D2, D2-D3, D1-D3")
    print("  • Apenas 1 canal disponível (C1)")
    print("\nAnálise:")
    print("  • Grafo completo K3 requer pelo menos 3 canais")
    print("  • Com apenas 1 canal, coloração é impossível")
    
    grafo = GrafoInterferencia()
    grafo.adicionar_aresta("D1", "D2")
    grafo.adicionar_aresta("D2", "D3")
    grafo.adicionar_aresta("D1", "D3")
    
    canais = ["C1"]
    
    coloracao = colorir_grafo(grafo, ["D1", "D2", "D3"], canais)
    
    print(f"Resultado: {coloracao}")
    
    assert coloracao is None, "Não deveria ser possível colorir com 1 canal"


# Teste 10 – Estimativa de custos de spill
def test_estimar_custos():
    print("\n-----------------------------------------\n")
    print("Teste 10: Estimativa de Custos de Spill")
    print("\nCenário:")
    print("  • D1: potência=50, frequência=2.0")
    print("  • D2: potência=100, frequência=1.0")
    print("  • D3: potência=75, frequência=1.5")
    print("\nAnálise:")
    print("  • Custo = potência x frequência")
    print("  • D1: 50 x 2.0 = 100")
    print("  • D2: 100 x 1.0 = 100")
    print("  • D3: 75 x 1.5 = 112.5 (maior custo)")
    
    dispositivos = [
        DispositivoMovel("D1", 0, 0, potencia=50, frequencia_uso=2.0),
        DispositivoMovel("D2", 10, 0, potencia=100, frequencia_uso=1.0),
        DispositivoMovel("D3", 20, 0, potencia=75, frequencia_uso=1.5)
    ]
    
    custos = estimar_custos_spill(dispositivos)
    
    print("\nCustos calculados:")
    for disp_id, custo in sorted(custos.items()):
        print(f"  • {disp_id}: {custo}")
    
    assert custos["D3"] > custos["D1"]
    assert custos["D3"] > custos["D2"]
    assert custos["D1"] == 100.0
    assert custos["D3"] == 112.5


# Teste 11 – Dispositivos sem interferência temporal
def test_sem_interferencia_temporal():
    print("\n-----------------------------------------\n")
    print("Teste 11: Dispositivos Sem Interferência Temporal")
    print("\nCenário:")
    print("  • D1 transmite e libera canal")
    print("  • D2 começa a transmitir após D1 liberar")
    print("\nResultado esperado:")
    print("  • D1 e D2 não interferem")
    
    escalonamento = EscalonamentoRede([
        SlotTempo("inicio_frame", 
                  [TransmissaoAtiva("D1", True)], 
                  []),
        SlotTempo("slot_normal", 
                  [], 
                  [RequisicaoCanal("D1", True)]),
        SlotTempo("slot_normal", 
                  [TransmissaoAtiva("D2", True)], 
                  [])
    ])
    
    grafo = construir_grafo_interferencia_temporal(escalonamento)
    
    print(f"\nD1-D2 interferem? {grafo.contem_aresta('D1', 'D2')} (esperado: False)")
    
    assert not grafo.contem_aresta("D1", "D2")


# Teste 12 – Cálculo de distância
def test_calcular_distancia():
    print("\n-----------------------------------------\n")
    print("Teste 12: Cálculo de Distância")
    print("\nCenário:")
    print("  • D1 em (0, 0)")
    print("  • D2 em (3, 4)")
    print("\nAnálise:")
    print("  • Distância euclidiana = sqrt(3² + 4²) = 5")
    
    d1 = DispositivoMovel("D1", 0, 0, 50)
    d2 = DispositivoMovel("D2", 3, 4, 50)
    
    distancia = calcular_distancia(d1, d2)
    
    print(f"\nDistância calculada: {distancia}")
    
    assert abs(distancia - 5.0) < 0.001


if __name__ == "__main__":
    test_construir_grafo_interferencia_espacial()
    test_construir_grafo_interferencia_temporal()
    test_coloracao_simples()
    test_decidir_spill()
    test_alocar_canais_com_spilling()
    test_aplicar_alocacao()
    test_remapear_dispositivos()
    test_calcular_interferencia_com_potencia()
    test_coloracao_impossivel()
    test_estimar_custos()
    test_sem_interferencia_temporal()
    test_calcular_distancia()