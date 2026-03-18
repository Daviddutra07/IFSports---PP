from datetime import datetime, timedelta
from app.models.treino_ocorrencia import TreinoOcorrencia

def calcular_primeira_data(dia_semana, horario):
    agora = datetime.now()

    hoje_dia_semana = agora.weekday()
    dias_ate = (dia_semana - hoje_dia_semana) % 7

    data_base = agora.date() + timedelta(days=dias_ate)
    data_treino = datetime.combine(data_base, horario)

    # Se for hoje e o horário já passou vai pra próxima semana
    if dias_ate == 0 and data_treino <= agora:
        data_base = data_base + timedelta(days=7)
        data_treino = data_treino = datetime.combine(data_base, horario)

    return data_treino

def calcular_proxima_data(data_treino):
    return data_treino + timedelta(days=7)

def obter_ocorrencia_aberta(treino_id):
    return (
        TreinoOcorrencia.query
        .filter(
            TreinoOcorrencia.tro_treino_id == treino_id,
            TreinoOcorrencia.tro_ativo.is_(True),
            TreinoOcorrencia.tro_validado_em.is_(None)
        )
        .order_by(TreinoOcorrencia.tro_data.asc())
        .first()
    )