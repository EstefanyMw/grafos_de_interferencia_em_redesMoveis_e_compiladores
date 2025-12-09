import copy
from random import choice
from typing import List, Set, Collection, Dict, Optional, Tuple


class Declaracao:
    def __init__(self, registrador: str, morto: bool):
        self.registrador = registrador
        self.morto = morto  # True se o registrador morre após esta declaração
    
    def __repr__(self):
        return f"Declaracao({self.registrador}, morto={self.morto})"


class Uso:
    def __init__(self, registrador: str, morto: bool):
        self.registrador = registrador
        self.morto = morto  # True se o registrador morre após este uso
    
    def __repr__(self):
        return f"Uso({self.registrador}, morto={self.morto})"


class Instrucao:
    def __init__(self, codigo_operacao: str, declaracoes: List[Declaracao], 
                 usos: List[Uso], frequencia=1.0):
        self.codigo_operacao = codigo_operacao
        self.declaracoes = declaracoes
        self.usos = usos
        self.frequencia = frequencia  # Frequência de execução estimada
    
    def __repr__(self):
        return f"Instrucao({self.codigo_operacao})"


class LinguagemIntermediaria:
    def __init__(self, instrucoes: List[Instrucao]):
        self.instrucoes = instrucoes

    def sobrescrever_instrucoes(self, novas_instrucoes: List[Instrucao]):
        self.instrucoes = novas_instrucoes

    def reescrever_registradores(self, mapeamento: Dict[str, str]) -> None:
        novas_instrucoes = []
        
        for instrucao in self.instrucoes:
            novas_declaracoes = [
                Declaracao(
                    mapeamento.get(dec.registrador, dec.registrador), 
                    dec.morto
                ) 
                for dec in instrucao.declaracoes
            ]
            
            novos_usos = [
                Uso(
                    mapeamento.get(uso.registrador, uso.registrador), 
                    uso.morto
                ) 
                for uso in instrucao.usos
            ]
            novas_instrucoes.append(
                Instrucao(
                    instrucao.codigo_operacao,
                    novas_declaracoes,
                    novos_usos,
                    instrucao.frequencia
                )
            )
        
        self.instrucoes = novas_instrucoes

    def obter_registradores(self) -> Set[str]:
        registradores = set()
        for instrucao in self.instrucoes:
            for declaracao in instrucao.declaracoes:
                registradores.add(declaracao.registrador)
            for uso in instrucao.usos:
                registradores.add(uso.registrador)
        return registradores
    

class GrafoInterferencia:
    def __init__(self):
        self._lista_adjacencia = {}

    def __copy__(self):
        nova_classe = self.__class__
        novo_grafo = nova_classe.__new__(nova_classe)
        novo_grafo._lista_adjacencia = copy.deepcopy(self._lista_adjacencia)
        return novo_grafo

    def adicionar_aresta(self, x: str, y: str):
        if x == y:
            return  # Não adiciona auto-loops
        
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

    def contem_aresta(self, x: str, y: str) -> bool:
        return y in self._lista_adjacencia.get(x, [])

    def remover_no(self, no: str):
        if no in self._lista_adjacencia:
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
        
        # Remove nome_novo de si mesmo se existir
        if nome_novo in self._lista_adjacencia[nome_novo]:
            self._lista_adjacencia[nome_novo].remove(nome_novo)

        # Atualiza todas as referências ao nome_antigo para nome_novo
        for chave in self._lista_adjacencia.keys():
            self._lista_adjacencia[chave] = list(set([
                nome_novo if valor == nome_antigo else valor 
                for valor in self._lista_adjacencia[chave]
            ]))
            if chave in self._lista_adjacencia[chave]:
                self._lista_adjacencia[chave].remove(chave)

    def obter_vizinhos(self, x: str) -> List[str]:
        return self._lista_adjacencia.get(x, [])
    
    def obter_nos(self) -> List[str]:
        return list(self._lista_adjacencia.keys())
    
    def calcular_grau(self, no: str) -> int:
        return len(self.obter_vizinhos(no))


def construir_grafo_interferencia(linguagem: LinguagemIntermediaria) -> GrafoInterferencia:
    grafo = GrafoInterferencia()
    conjunto_vivos = None

    for instrucao in linguagem.instrucoes:
        if instrucao.codigo_operacao == 'bloco_basico':
            # Inicia um novo bloco básico
            conjunto_vivos = {}
            
            # Adiciona declarações iniciais do bloco
            for declaracao in instrucao.declaracoes:
                if not declaracao.morto:
                    contador = conjunto_vivos.get(declaracao.registrador, 0)
                    conjunto_vivos[declaracao.registrador] = contador + 1
        
        else:
            # Remove registradores que morrem ANTES de processar declarações
            for uso in instrucao.usos:
                if uso.morto and uso.registrador in conjunto_vivos:
                    conjunto_vivos[uso.registrador] -= 1
                    if conjunto_vivos[uso.registrador] == 0:
                        conjunto_vivos.pop(uso.registrador)
            
            # Para cada declaração, adiciona interferências com registradores vivos
            for declaracao in instrucao.declaracoes:
                for reg_vivo in conjunto_vivos.keys():
                    if reg_vivo != declaracao.registrador:
                        grafo.adicionar_aresta(declaracao.registrador, reg_vivo)

                # Adiciona o registrador declarado ao conjunto de vivos
                if not declaracao.morto:
                    contador = conjunto_vivos.get(declaracao.registrador, 0)
                    conjunto_vivos[declaracao.registrador] = contador + 1
    
    return grafo


def copia_desnecessaria(instrucao: Instrucao, grafo: GrafoInterferencia) -> bool:
    if len(instrucao.declaracoes) == 0 or len(instrucao.usos) == 0:
        return False

    destino = instrucao.declaracoes[0].registrador
    origem = instrucao.usos[0].registrador

    return (instrucao.codigo_operacao == 'copia' and
            destino != origem and
            not grafo.contem_aresta(destino, origem))


def fazer_coalescing(linguagem: LinguagemIntermediaria, grafo: GrafoInterferencia) -> None:
    houve_modificacao = True
    while houve_modificacao:
        # Procura primeira instrução de cópia desnecessária
        instrucao_encontrada = None
        
        for instrucao in linguagem.instrucoes:
            if copia_desnecessaria(instrucao, grafo):
                instrucao_encontrada = instrucao
                break
        
        if instrucao_encontrada is not None:
            destino = instrucao_encontrada.declaracoes[0].registrador
            origem = instrucao_encontrada.usos[0].registrador

            # Cria mapeamento de renomeação
            mapeamento = {destino: origem}

            # Atualiza grafo e linguagem intermediária
            grafo.renomear_no(destino, origem)
            linguagem.reescrever_registradores(mapeamento)
        else:
            houve_modificacao = False


def colorir_grafo(grafo: GrafoInterferencia, registradores: Collection[str], cores: List[str]) -> Optional[Dict[str, str]]:
    if len(registradores) == 0:
        return {}

    # Encontra nó com grau < k
    no_escolhido = None
    for no in registradores:
        if len(grafo.obter_vizinhos(no)) < len(cores):
            no_escolhido = no
            break
    
    if no_escolhido is None:
        # Não há nó com grau suficientemente baixo
        return None

    # Remove nó e colore recursivamente
    grafo_copia = copy.copy(grafo)
    grafo_copia.remover_no(no_escolhido)
    
    registradores_restantes = [r for r in registradores if r != no_escolhido]
    coloracao = colorir_grafo(grafo_copia, registradores_restantes, cores)
    
    if coloracao is None:
        return None

    # Atribui cor ao nó
    # Usa grafo original (não a cópia) para obter vizinhos corretos
    cores_vizinhos = [
        coloracao[vizinho] 
        for vizinho in grafo.obter_vizinhos(no_escolhido)
        if vizinho in coloracao
    ]
    
    cores_disponiveis = [cor for cor in cores if cor not in cores_vizinhos]
    
    if not cores_disponiveis:
        return None
    
    # Escolhe aleatoriamente uma cor disponível
    coloracao[no_escolhido] = choice(cores_disponiveis)
    
    return coloracao


def estimar_custos_spill(linguagem: LinguagemIntermediaria) -> Dict[str, float]:
    custos = {}
    frequencia_atual = 1.0

    for instrucao in linguagem.instrucoes:
        if instrucao.codigo_operacao == 'bloco_basico':
            frequencia_atual = instrucao.frequencia
        else:
            # Coleta todos os registradores usados nesta instrução
            registradores_usados = set()
            
            for declaracao in instrucao.declaracoes:
                registradores_usados.add(declaracao.registrador)
            
            for uso in instrucao.usos:
                registradores_usados.add(uso.registrador)

            # Adiciona custo ponderado pela frequência
            # Garantido que frequencia_atual não é None
            for reg in registradores_usados:
                custos[reg] = custos.get(reg, 0.0) + frequencia_atual

    return custos


def decidir_spills(linguagem: LinguagemIntermediaria, grafo: GrafoInterferencia, cores: List[str], custos: Dict[str, float]) -> Set[str]:
    registradores_spill = set()

    grafo_copia = copy.copy(grafo)
    registradores_restantes = set(linguagem.obter_registradores())

    while len(registradores_restantes) != 0:
        # Tenta encontrar nó com grau < k
        no_facil = None
        
        for no in registradores_restantes:
            if len(grafo_copia.obter_vizinhos(no)) < len(cores):
                no_facil = no
                break
        
        if no_facil is None:
            # Não há nó fácil, escolhe o de menor custo para spill
            no_spill = min(
                registradores_restantes, 
                key=lambda x: custos.get(x, float('inf'))
            )
            registradores_spill.add(no_spill)
            no_escolhido = no_spill
        else:
            no_escolhido = no_facil

        # Remove o nó processado
        grafo_copia.remover_no(no_escolhido)
        registradores_restantes.remove(no_escolhido)

    return registradores_spill


def inserir_codigo_spill(linguagem: LinguagemIntermediaria, registradores_spill: Set[str]) -> None:
    novas_instrucoes = []
    
    for instrucao in linguagem.instrucoes:
        if instrucao.codigo_operacao == 'bloco_basico':
            # Remove declarações de registradores que vão para spill
            novas_declaracoes = [
                dec for dec in instrucao.declaracoes 
                if dec.registrador not in registradores_spill
            ]
            
            novas_instrucoes.append(
                Instrucao(
                    'bloco_basico',
                    novas_declaracoes,
                    instrucao.usos.copy(),
                    instrucao.frequencia
                )
            )
        else:
            instrucoes_antes = []
            instrucoes_depois = []
            novas_declaracoes = []
            novos_usos = []

            for uso in instrucao.usos:
                if uso.registrador in registradores_spill:
                    # Marca como morto após reload
                    novos_usos.append(Uso(uso.registrador, True))
                    
                    # Adiciona instrução de reload
                    instrucoes_antes.append(
                        Instrucao(
                            'recarregar',
                            [Declaracao(uso.registrador, False)],
                            [],
                            instrucao.frequencia
                        )
                    )
                else:
                    novos_usos.append(Uso(uso.registrador, uso.morto))
            
            for declaracao in instrucao.declaracoes:
                if declaracao.registrador in registradores_spill:
                    # Marca como não-morto
                    novas_declaracoes.append(Declaracao(declaracao.registrador, False))
                    
                    # Adiciona instrução de spill
                    instrucoes_depois.append(
                        Instrucao(
                            'despejar',
                            [],
                            [Uso(declaracao.registrador, True)],
                            instrucao.frequencia
                        )
                    )
                else:
                    novas_declaracoes.append(Declaracao(declaracao.registrador, declaracao.morto))

            # Monta instrução modificada
            instrucao_modificada = Instrucao(
                instrucao.codigo_operacao, 
                novas_declaracoes, 
                novos_usos, 
                instrucao.frequencia
            )
            
            novas_instrucoes.extend(instrucoes_antes)
            novas_instrucoes.append(instrucao_modificada)
            novas_instrucoes.extend(instrucoes_depois)

    linguagem.sobrescrever_instrucoes(novas_instrucoes)