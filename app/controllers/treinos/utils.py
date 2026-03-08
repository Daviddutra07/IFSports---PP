from datetime import datetime, timedelta, timezone

def calcular_primeira_data(dia_semana, horario):
    agora = datetime.now(timezone.utc)

    hoje_dia_semana = agora.weekday()
    dia_hoje = agora.date()
    dias_ate = (dia_semana - hoje_dia_semana) % 7

    if dia_semana == hoje_dia_semana and horario < agora.time():
        data_treino = dia_hoje + timedelta(days=7)
        data_formatada = datetime.combine(data_treino, horario, tzinfo=timezone.utc)
        return data_formatada
    else:
        data_treino = dia_hoje + timedelta(days=dias_ate)
        data_formatada = datetime.combine(data_treino, horario, tzinfo=timezone.utc)
        return data_formatada

def calcular_proxima_data(data_treino):
    return data_treino + timedelta(days=7)