import copy
import math
from typing import List, Set, Dict, Optional, Tuple
from random import choice, random


class DispositivoMovel:
    def __init__(self, id: str, x: float, y: float, potencia: float, frequencia_uso: float = 1.0):
        self.id = id
        self.x = x  # Posição X
        self.y = y  # Posição Y
        self.potencia = potencia  # Potência de transmissão (peso/prioridade)
        self.frequencia_uso = frequencia_uso  # Frequência de uso do canal
        self.canal_alocado = None  # Canal alocado após coloração
        self.em_spill = False  # True se não conseguiu canal
    
    def __repr__(self):
        return f"Dispositivo({self.id}, pos=({self.x:.1f}, {self.y:.1f}), pot={self.potencia:.1f})"


class TransmissaoAtiva:
    def __init__(self, dispositivo_id: str, ativa: bool):
        self.dispositivo_id = dispositivo_id
        self.ativa = ativa  # True se a transmissão continua ativa
    
    def __repr__(self):
        return f"Transmissao({self.dispositivo_id}, ativa={self.ativa})"


class RequisicaoCanal:
    def __init__(self, dispositivo_id: str, libera: bool):
        self.dispositivo_id = dispositivo_id
        self.libera = libera  # True se libera o canal após usar
    
    def __repr__(self):
        return f"Requisicao({self.dispositivo_id}, libera={self.libera})"


class SlotTempo:
    def __init__(self, tipo: str, transmissoes: List[TransmissaoAtiva], requisicoes: List[RequisicaoCanal], peso: float = 1.0):
        self.tipo = tipo  # 'inicio_frame' ou 'slot_normal'
        self.transmissoes = transmissoes
        self.requisicoes = requisicoes
        self.peso = peso 
    
    def __repr__(self):
        return f"Slot({self.tipo}, {len(self.transmissoes)} trans, {len(self.requisicoes)} req)"


class EscalonamentoRede:
    def __init__(self, slots: List[SlotTempo]):
        self.slots = slots
    
    def sobrescrever_slots(self, novos_slots: List[SlotTempo]):
        self.slots = novos_slots
    
    def remapear_dispositivos(self, mapeamento: Dict[str, str]) -> None:
        novos_slots = []
        for slot in self.slots:
            novas_trans = [
                TransmissaoAtiva(
                    mapeamento.get(trans.dispositivo_id, trans.dispositivo_id),
                    trans.ativa
                )
                for trans in slot.transmissoes
            ]
            novas_req = [
                RequisicaoCanal(
                    mapeamento.get(req.dispositivo_id, req.dispositivo_id),
                    req.libera
                )
                for req in slot.requisicoes
            ]
            novos_slots.append(
                SlotTempo(slot.tipo, novas_trans, novas_req, slot.peso)
            )
        
        self.slots = novos_slots
    
    def obter_dispositivos(self) -> Set[str]:
        dispositivos = set()
        for slot in self.slots:
            for trans in slot.transmissoes:
                dispositivos.add(trans.dispositivo_id)
            for req in slot.requisicoes:
                dispositivos.add(req.dispositivo_id)
        return dispositivos


class GrafoInterferencia:
    def __init__(self):
        self._lista_adjacencia = {}
        self._pesos_arestas = {}
    
    def __copy__(self):
        nova_classe = self.__class__
        novo_grafo = nova_classe.__new__(nova_classe)
        novo_grafo._lista_adjacencia = copy.deepcopy(self._lista_adjacencia)
        novo_grafo._pesos_arestas = copy.deepcopy(self._pesos_arestas)
        return novo_grafo
    
    def adicionar_aresta(self, x: str, y: str, peso: float = 1.0):
        if x == y:
            return
        
        # Adiciona y à lista de adjacência de x
        lista_x = self._lista_adjacencia.get(x, [])
        if y not in lista_x:
            lista_x.append(y)
        self._lista_adjacencia[x] = lista_x
        
        # Adiciona x à lista de adjacência de y
        lista_y = self._lista_adjacencia.get(y, [])
        if x not in lista_y:
            lista_y.append(x)
        self._lista_adjacencia[y] = lista_y
        
        # Armazena peso da aresta
        chave = tuple(sorted([x, y]))
        self._pesos_arestas[chave] = peso
    
    def contem_aresta(self, x: str, y: str) -> bool:
        return y in self._lista_adjacencia.get(x, [])
    
    def obter_peso_aresta(self, x: str, y: str) -> float:
        chave = tuple(sorted([x, y]))
        return self._pesos_arestas.get(chave, 0.0)
    
    def remover_no(self, no: str):
        if no in self._lista_adjacencia:
            # Remove arestas associadas
            for vizinho in self._lista_adjacencia[no]:
                chave = tuple(sorted([no, vizinho]))
                self._pesos_arestas.pop(chave, None)       
            self._lista_adjacencia.pop(no)
        
        # Remove o nó das listas de adjacência de outros nós
        for chave in list(self._lista_adjacencia.keys()):
            if no in self._lista_adjacencia[chave]:
                self._lista_adjacencia[chave].remove(no)
    
    def renomear_no(self, nome_antigo: str, nome_novo: str):
        lista_antiga = self._lista_adjacencia.pop(nome_antigo, [])
        lista_nova = self._lista_adjacencia.get(nome_novo, [])
        
        # Combina as listas e remove duplicatas
        self._lista_adjacencia[nome_novo] = list(set(lista_antiga + lista_nova))
        
        # Remove auto-referência
        if nome_novo in self._lista_adjacencia[nome_novo]:
            self._lista_adjacencia[nome_novo].remove(nome_novo)
        
        # Atualiza todas as referências
        for chave in self._lista_adjacencia.keys():
            self._lista_adjacencia[chave] = list(set([
                nome_novo if valor == nome_antigo else valor
                for valor in self._lista_adjacencia[chave]
            ]))
            if chave in self._lista_adjacencia[chave]:
                self._lista_adjacencia[chave].remove(chave)
        
        # Atualiza pesos das arestas
        novos_pesos = {}
        for (a, b), peso in self._pesos_arestas.items():
            nova_a = nome_novo if a == nome_antigo else a
            nova_b = nome_novo if b == nome_antigo else b
            if nova_a != nova_b:
                chave = tuple(sorted([nova_a, nova_b]))
                novos_pesos[chave] = peso
        self._pesos_arestas = novos_pesos
    
    def obter_vizinhos(self, x: str) -> List[str]:
        return self._lista_adjacencia.get(x, [])
    
    def obter_nos(self) -> List[str]:
        return list(self._lista_adjacencia.keys())
    
    def calcular_grau(self, no: str) -> int:
        return len(self.obter_vizinhos(no))
    
    def obter_arestas(self) -> List[Tuple[str, str, float]]:
        arestas = []
        visitadas = set()       
        for origem in self._lista_adjacencia:
            for destino in self._lista_adjacencia[origem]:
                par = tuple(sorted([origem, destino]))
                if par not in visitadas:
                    peso = self._pesos_arestas.get(par, 1.0)
                    arestas.append((origem, destino, peso))
                    visitadas.add(par)
        
        return arestas


def calcular_distancia(d1: DispositivoMovel, d2: DispositivoMovel) -> float:
    return math.sqrt((d1.x - d2.x)**2 + (d1.y - d2.y)**2)


def calcular_interferencia(d1: DispositivoMovel, d2: DispositivoMovel, limiar_distancia: float) -> float:
    distancia = calcular_distancia(d1, d2)
    if distancia >= limiar_distancia:
        return 0.0

    # Interferência inversamente proporcional à distância ao quadrado
    interferencia = 1.0 - (distancia / limiar_distancia)
    # Considera também as potências dos dispositivos
    fator_potencia = (d1.potencia + d2.potencia) / 200.0  # Normalizado
    return min(interferencia * fator_potencia, 1.0)


def construir_grafo_interferencia_espacial( dispositivos: List[DispositivoMovel], limiar_distancia: float = 150.0, limiar_interferencia: float = 0.1) -> GrafoInterferencia:
    grafo = GrafoInterferencia()
    for i in range(len(dispositivos)):
        for j in range(i + 1, len(dispositivos)):
            d1 = dispositivos[i]
            d2 = dispositivos[j]
            
            interferencia = calcular_interferencia(d1, d2, limiar_distancia)
            
            if interferencia >= limiar_interferencia:
                grafo.adicionar_aresta(d1.id, d2.id, interferencia)
    
    return grafo


def construir_grafo_interferencia_temporal(escalonamento: EscalonamentoRede) -> GrafoInterferencia:
    grafo = GrafoInterferencia()
    conjunto_ativos = {}
    for slot in escalonamento.slots:
        if slot.tipo == 'inicio_frame':
            # Inicia novo frame
            conjunto_ativos = {}
            # Adiciona transmissões iniciais do frame
            for trans in slot.transmissoes:
                if trans.ativa:
                    contador = conjunto_ativos.get(trans.dispositivo_id, 0)
                    conjunto_ativos[trans.dispositivo_id] = contador + 1
        else:
            # Remove dispositivos que liberam canal antes de processar transmissões
            for req in slot.requisicoes:
                if req.libera and req.dispositivo_id in conjunto_ativos:
                    conjunto_ativos[req.dispositivo_id] -= 1
                    if conjunto_ativos[req.dispositivo_id] == 0:
                        conjunto_ativos.pop(req.dispositivo_id)
            # Para cada nova transmissão, adiciona interferências com ativos
            for trans in slot.transmissoes:
                for disp_ativo in conjunto_ativos.keys():
                    if disp_ativo != trans.dispositivo_id:
                        grafo.adicionar_aresta(trans.dispositivo_id, disp_ativo)
                # Adiciona o dispositivo ao conjunto de ativos
                if trans.ativa:
                    contador = conjunto_ativos.get(trans.dispositivo_id, 0)
                    conjunto_ativos[trans.dispositivo_id] = contador + 1
    return grafo


def colorir_grafo(grafo: GrafoInterferencia, dispositivos: List[str], canais: List[str]) -> Optional[Dict[str, str]]:
    if len(dispositivos) == 0:
        return {}
    # Encontra nó com grau < k
    no_escolhido = None
    for no in dispositivos:
        if len(grafo.obter_vizinhos(no)) < len(canais):
            no_escolhido = no
            break
    if no_escolhido is None:
        # Não há nó com grau suficientemente baixo
        return None
    
    # Remove nó e colore recursivamente
    grafo_copia = copy.copy(grafo)
    grafo_copia.remover_no(no_escolhido)
    
    dispositivos_restantes = [d for d in dispositivos if d != no_escolhido]
    coloracao = colorir_grafo(grafo_copia, dispositivos_restantes, canais)
    if coloracao is None:
        return None
    # Atribui canal ao nó
    canais_vizinhos = [
        coloracao[vizinho]
        for vizinho in grafo.obter_vizinhos(no_escolhido)
        if vizinho in coloracao
    ]
    canais_disponiveis = [canal for canal in canais if canal not in canais_vizinhos]
    if not canais_disponiveis:
        return None
    # Escolhe canal
    coloracao[no_escolhido] = choice(canais_disponiveis)
    return coloracao


def estimar_custos_spill(dispositivos: List[DispositivoMovel]) -> Dict[str, float]:
    custos = {}
    for disp in dispositivos:
        custos[disp.id] = disp.potencia * disp.frequencia_uso
    return custos


def decidir_spills(grafo: GrafoInterferencia, dispositivos: List[DispositivoMovel], canais: List[str], custos: Dict[str, float]) -> Set[str]:
    dispositivos_spill = set()
    grafo_copia = copy.copy(grafo)
    dispositivos_restantes = set(d.id for d in dispositivos)
    
    while len(dispositivos_restantes) != 0:
        # Tenta encontrar nó com grau < k
        no_facil = None
        
        for no in dispositivos_restantes:
            if len(grafo_copia.obter_vizinhos(no)) < len(canais):
                no_facil = no
                break
        
        if no_facil is None:
            # Não há nó fácil, escolhe o de menor custo para spill
            no_spill = min(
                dispositivos_restantes,
                key=lambda x: custos.get(x, 0)
            )
            dispositivos_spill.add(no_spill)
            no_escolhido = no_spill
        else:
            no_escolhido = no_facil
        
        # Remove o nó processado
        grafo_copia.remover_no(no_escolhido)
        dispositivos_restantes.remove(no_escolhido)
    return dispositivos_spill


def alocar_canais_com_spilling(dispositivos: List[DispositivoMovel], grafo: GrafoInterferencia, canais: List[str]) -> Tuple[Dict[str, str], Set[str]]:
    custos = estimar_custos_spill(dispositivos)
    spills = decidir_spills(grafo, dispositivos, canais, custos)
    
    # Remove dispositivos em spill
    grafo_reduzido = copy.copy(grafo)
    for disp_id in spills:
        grafo_reduzido.remover_no(disp_id)
    
    # Colore grafo reduzido
    dispositivos_restantes = [d.id for d in dispositivos if d.id not in spills]
    alocacao = colorir_grafo(grafo_reduzido, dispositivos_restantes, canais)
    return alocacao or {}, spills


def aplicar_alocacao(dispositivos: List[DispositivoMovel], alocacao: Dict[str, str], spills: Set[str]) -> None:
    for disp in dispositivos:
        if disp.id in spills:
            disp.em_spill = True
            disp.canal_alocado = None
        else:
            disp.em_spill = False
            disp.canal_alocado = alocacao.get(disp.id)