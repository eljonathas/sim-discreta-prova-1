import simpy
import random
import numpy as np


TEMPO_SIMULACAO = 8 * 60
MEDIA_CHEGADA_PALLETS = 6.65
DESVIO_PADRAO_CHEGADA_PALLETS = 3.05
MEDIA_FIXACAO = 40 / 60
DESVIO_PADRAO_FIXACAO = 5 / 60
TEMPO_USINAGEM = 3
TEMPO_PARAFUSAGEM_MIN = 3.5
TEMPO_PARAFUSAGEM_MAX = 4

estatisticas = {
    'tempo_espera_fixacao': [],
    'tempo_espera_usinagem': [],
    'tempo_espera_parafusagem': [],
    'tempo_total_processamento': [],
    'total_pecas_processadas': 0,
    'tempo_ocio_funcionario1': 0,
    'tempo_ocio_funcionario2': 0,
    'max_tamanho_fila_fixacao': 0,
    'max_tamanho_fila_usinagem': 0,
    'max_tamanho_fila_parafusagem': 0,
    'tempos_filas_fixacao': [],
    'tempos_filas_usinagem': [],
    'tempos_filas_parafusagem': [],
}

def tempo_chegada_pallets():
    """Gera o tempo de chegada dos pallets, seguindo uma distribuição normal."""
    return max(0, random.normalvariate(MEDIA_CHEGADA_PALLETS, DESVIO_PADRAO_CHEGADA_PALLETS))

def tempo_fixacao():
    """Gera o tempo de fixação das peças, seguindo uma distribuição normal."""
    return max(0, random.normalvariate(MEDIA_FIXACAO, DESVIO_PADRAO_FIXACAO))

def tempo_parafusagem():
    """Gera o tempo de parafusagem, seguindo uma distribuição uniforme."""
    return random.uniform(TEMPO_PARAFUSAGEM_MIN, TEMPO_PARAFUSAGEM_MAX)

def processo_par_pecas(env, fixacao, usinagem, parafusagem):
    """Simula o processamento de um par de peças."""
    inicio_processo = env.now

    
    inicio_espera_fixacao = env.now
    with fixacao.request() as req_fixacao:
        yield req_fixacao
        tempo_espera_fixacao = env.now - inicio_espera_fixacao
        estatisticas['tempo_espera_fixacao'].append(tempo_espera_fixacao)
        estatisticas['tempos_filas_fixacao'].append(len(fixacao.queue))
        if len(fixacao.queue) > estatisticas['max_tamanho_fila_fixacao']:
            estatisticas['max_tamanho_fila_fixacao'] = len(fixacao.queue)
        yield env.timeout(tempo_fixacao())

    
    inicio_espera_usinagem = env.now
    with usinagem.request() as req_usinagem:
        yield req_usinagem
        tempo_espera_usinagem = env.now - inicio_espera_usinagem
        estatisticas['tempo_espera_usinagem'].append(tempo_espera_usinagem)
        estatisticas['tempos_filas_usinagem'].append(len(usinagem.queue))
        if len(usinagem.queue) > estatisticas['max_tamanho_fila_usinagem']:
            estatisticas['max_tamanho_fila_usinagem'] = len(usinagem.queue)
        yield env.timeout(TEMPO_USINAGEM)

    
    inicio_espera_parafusagem = env.now
    with parafusagem.request() as req_parafusagem:
        yield req_parafusagem
        tempo_espera_parafusagem = env.now - inicio_espera_parafusagem
        estatisticas['tempo_espera_parafusagem'].append(tempo_espera_parafusagem)
        estatisticas['tempos_filas_parafusagem'].append(len(parafusagem.queue))
        if len(parafusagem.queue) > estatisticas['max_tamanho_fila_parafusagem']:
            estatisticas['max_tamanho_fila_parafusagem'] = len(parafusagem.queue)
        yield env.timeout(tempo_parafusagem())

    tempo_total = env.now - inicio_processo
    estatisticas['tempo_total_processamento'].append(tempo_total)
    estatisticas['total_pecas_processadas'] += 2  

def chegada_pallets(env, fixacao, usinagem, parafusagem):
    """Simula a chegada de pallets e inicia o processamento dos pares de peças."""
    while True:
        yield env.timeout(tempo_chegada_pallets())
        for _ in range(30):  
            env.process(processo_par_pecas(env, fixacao, usinagem, parafusagem))

def monitor_ociosidade(env, fixacao, usinagem, parafusagem):
    """Monitora o tempo ocioso dos funcionários durante a simulação."""
    funcionario1_ocioso = False
    funcionario2_ocioso = False
    inicio_ocio1 = env.now
    inicio_ocio2 = env.now

    while True:
        
        if fixacao.count == 0 and usinagem.count == 0:
            if not funcionario1_ocioso:
                funcionario1_ocioso = True
                inicio_ocio1 = env.now
        else:
            if funcionario1_ocioso:
                funcionario1_ocioso = False
                estatisticas['tempo_ocio_funcionario1'] += env.now - inicio_ocio1

        
        if parafusagem.count == 0:
            if not funcionario2_ocioso:
                funcionario2_ocioso = True
                inicio_ocio2 = env.now
        else:
            if funcionario2_ocioso:
                funcionario2_ocioso = False
                estatisticas['tempo_ocio_funcionario2'] += env.now - inicio_ocio2

        yield env.timeout(1)  

def simular():
    """Executa a simulação."""
    env = simpy.Environment()

    
    fixacao = simpy.Resource(env, capacity=1)
    usinagem = simpy.Resource(env, capacity=1)
    parafusagem = simpy.Resource(env, capacity=1)

    env.process(chegada_pallets(env, fixacao, usinagem, parafusagem))
    env.process(monitor_ociosidade(env, fixacao, usinagem, parafusagem))

    env.run(until=TEMPO_SIMULACAO)

    mostrar_resultados()

def mostrar_resultados():
    """Exibe as estatísticas da simulação."""
    print(f"Tempo médio de espera na fixação: {np.mean(estatisticas['tempo_espera_fixacao']):.2f} minutos")
    print(f"Tempo máximo de espera na fixação: {np.max(estatisticas['tempo_espera_fixacao']):.2f} minutos")
    print(f"Tamanho médio da fila de fixação: {np.mean(estatisticas['tempos_filas_fixacao']):.2f}")
    print(f"Tamanho máximo da fila de fixação: {estatisticas['max_tamanho_fila_fixacao']}")

    print(f"Tempo médio de espera na usinagem: {np.mean(estatisticas['tempo_espera_usinagem']):.2f} minutos")
    print(f"Tempo máximo de espera na usinagem: {np.max(estatisticas['tempo_espera_usinagem']):.2f} minutos")
    print(f"Tamanho médio da fila de usinagem: {np.mean(estatisticas['tempos_filas_usinagem']):.2f}")
    print(f"Tamanho máximo da fila de usinagem: {estatisticas['max_tamanho_fila_usinagem']}")

    print(f"Tempo médio de espera na parafusagem: {np.mean(estatisticas['tempo_espera_parafusagem']):.2f} minutos")
    print(f"Tempo máximo de espera na parafusagem: {np.max(estatisticas['tempo_espera_parafusagem']):.2f} minutos")
    print(f"Tamanho médio da fila de parafusagem: {np.mean(estatisticas['tempos_filas_parafusagem']):.2f}")
    print(f"Tamanho máximo da fila de parafusagem: {estatisticas['max_tamanho_fila_parafusagem']}")

    print(f"Tempo médio total de processamento: {np.mean(estatisticas['tempo_total_processamento']):.2f} minutos")
    print(f"Número total de peças processadas: {estatisticas['total_pecas_processadas']}")

    print(f"Tempo ocioso do funcionário 1: {estatisticas['tempo_ocio_funcionario1']:.2f} minutos")
    print(f"Tempo ocioso do funcionário 2: {estatisticas['tempo_ocio_funcionario2']:.2f} minutos")

def reiniciar_estatisticas():
    """Reinicia as estatísticas para uma nova simulação."""
    for chave in estatisticas:
        if isinstance(estatisticas[chave], list):
            estatisticas[chave].clear()
        else:
            estatisticas[chave] = 0


reiniciar_estatisticas()
simular()
