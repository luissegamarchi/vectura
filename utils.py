import json
import os
from datetime import datetime
import requests
import folium
import polyline
import streamlit as st

ARQUIVO_ENDERECOS = "enderecos.json"
ARQUIVO_HISTORICO = "historico.json"
ARQUIVO_FIXOS = "fixos.json"

enderecos_disponiveis = {}
historico = []
fixos = []

# ---- Funções de Cálculo Fixo ----

def carregar_fixos():
    """Carrega o arquivo fixos.json; se não existir, cria uma lista vazia."""
    if not os.path.exists(ARQUIVO_FIXOS):
        with open(ARQUIVO_FIXOS, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []
    
    with open(ARQUIVO_FIXOS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_fixos(fixos):
    """Salva a lista atualizada no fixos.json."""
    with open(ARQUIVO_FIXOS, "w", encoding="utf-8") as f:
        json.dump(fixos, f, ensure_ascii=False, indent=4)


def fixar_calculo(dados):
    """
    Tenta adicionar um cálculo à lista de fixos.
    Retorna (True, mensagem) ou (False, mensagem)
    """
    fixos = carregar_fixos()

    if len(fixos) >= 5:
        return False, "❌ Limite máximo de 5 cálculos fixos atingido!"

    fixos.append(dados)
    salvar_fixos(fixos)
    return True, "✅ Cálculo fixado com sucesso"

def limpar_fixos():
    with open(ARQUIVO_FIXOS, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
    return True, "✅ Consultas fixas limpas com sucesso."

# ---- Funções de Cálculo Fixo ----

# ---- Funções de Histórico ----

def carregar_historico():
    if not os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []

    return []

def salva_historico(historico_original, consulta):
    historico = historico_original

    # Adiciona a nova consulta ao final
    historico.append(consulta)

    # Se tiver mais que 10, remove a mais antiga (posição 0)
    if len(historico) > 10:
        historico.pop(0)
    
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

    historico_original = historico

def reduzir_para_historico(dados):
    CAMPOS_HISTORICO = [
        "origem",
        "destino_1",
        "recarga",
        "destino_2",
        "km_total_simples",
        "tempo_total_simples",
        "qtd_pedagio_total_simples",
        "valor_pedagio_total_simples",
        "lista_pedagios_total_simples",
        "km_total",
        "tempo_total",
        "qtd_total_pedagios",
        "valor_pedagios_total",
        "lista_pedagios_total",
        "km_diff",
        "tempo_diff",
        "qtd_pedagio_diff",
        "tarifas_diff",
        "racional",
        "valor_excedente",
    ]

    return {campo: dados[campo] for campo in CAMPOS_HISTORICO if campo in dados}

def limpar_historico():

    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

    return True, "✅ Histórico limpo com sucesso."

# ---- Funções de Histórico ----

# ---- Funções de Endereço ----

# Extrai o cep de um endereço str
def extrair_cep(texto):
    for i in range(len(texto) - 8):   # 8 = tamanho do CEP
        trecho = texto[i:i+9]        # pega 9 caracteres
        if (trecho[:5].isdigit() and
            trecho[5] == '-' and
            trecho[6:].isdigit()):
            return trecho
    return None

# Faz a formatação do endereço a partir do retorno da API do Google Maps
def formata_endereco(endereco):

    cep = extrair_cep(endereco)

    if cep:
        resultado_separado = endereco.split(", ")
        resultado_separado.remove(cep)
        endereço_formatado = ", ".join(resultado_separado)

        return endereço_formatado, cep

    else:
        return endereco


# Função para carregar dados já salvos
def carregar_enderecos():
    if os.path.exists(ARQUIVO_ENDERECOS):
        with open(ARQUIVO_ENDERECOS, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return enderecos_disponiveis.copy()

# Função para salvar novos dados
def salvar_enderecos(tipo, nome_salvar, endereco_salvar, enderecos, chave):
    """
    Valida e salva um novo endereço no dicionário principal.
    Retorna (sucesso: bool, mensagem: str).
    """

    # Validação de campos obrigatórios
    if not nome_salvar.strip() or not endereco_salvar.strip():
        return False, "⚠️ Preencha todos os campos."

    # Confirma se o tipo existe
    if tipo not in enderecos:
        return False, f"❌ Tipo '{tipo}' inválido."

    # Verifica duplicidades
    if nome_salvar in enderecos[tipo]:
        return False, f"❌ O nome '{nome_salvar}' já foi usado em {tipo}."
    if endereco_salvar in enderecos[tipo].values():
        return False, f"❌ Este endereço já foi cadastrado em {tipo}."
    
    if chave == "":
        return False, f"❌ Insira uma chave."
    
    if chave != st.secrets['chave']:
        return False,  f"❌ Chave incorreta."

    endereco = extrai_coord(endereco_salvar, chave)

    lat = endereco[1][0]
    long = endereco[1][1]

    endereco_formatado = formata_endereco(endereco[0])

    registro = {"endereco_formatado": endereco_formatado[0],
        "latitude": lat,
        "longitude": long,
        "cep": endereco_formatado[1],
        "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    # Salva o novo endereço
    enderecos[tipo][nome_salvar] = registro

    # Persiste no JSON
    with open(ARQUIVO_ENDERECOS, "w", encoding="utf-8") as f:
        json.dump(enderecos, f, ensure_ascii=False, indent=4)

    return True, f"✅ Endereço salvo como {tipo}!"

# Função para excluir dados salvos
def excluir_enderecos(tipo, nome_excluir, enderecos):
    """
    Valida e exclui um endereço existente no dicionário principal.
    Retorna (sucesso: bool, mensagem: str).
    """

    # Validação de campos obrigatórios
    if not nome_excluir.strip():
        return False, "⚠️ Preencha todos os campos."

    # Verifica se o tipo é válido
    if tipo not in enderecos:
        return False, f"❌ Tipo '{tipo}' inválido."

    # Verifica se o nome existe na base
    if nome_excluir not in enderecos[tipo]:
        return False, f"❌ O nome '{nome_excluir}' não existe na base de {tipo}."

    # Exclui o endereço
    del enderecos[tipo][nome_excluir]

    # Atualiza o arquivo JSON
    with open(ARQUIVO_ENDERECOS, "w", encoding="utf-8") as f:
        json.dump(enderecos, f, ensure_ascii=False, indent=4)

    return True, f"✅ Endereço excluído da base de {tipo}!"

# # Função para listar os pedágios no trecho
# def lista_pedagios(infos_rotas):
#     """
#     Faz a lista dos nomes dos pedágios no trajeto 
#     Retorna (lista_pedagios: list)
#     """
#     lista_pedagios = []
#     for i in range(len(infos_rotas["pedagios"])):
#         nome_pedagio = infos_rotas["pedagios"][i]["nome"]

#         lista_pedagios.append(nome_pedagio)
    
#     return lista_pedagios

# Função para extrair as coordenadas de um endereço
def extrai_coord(endereco, chave):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": endereco, "key": chave}

    r = requests.get(url, params=params).json()

    if r["status"] == "OK":
        result = r["results"][0]
        lat = result["geometry"]["location"]["lat"]
        lng = result["geometry"]["location"]["lng"]
        endereco_formatado = result["formatted_address"]

        return endereco_formatado, (lat, lng)
    
    return None, None, None

# ---- Fim da Função de Endereços ----


# ---- Funções de Cálculos (Distâncias, Pedágios, etc) ----

# Cálculo do valor do frete
def calculo_frete(diff_pedagio, diff_km, racional):
    """
    Faz o cálculo do valor a ser cobrado a partir da multiplicação da diferença de km rodado pelo racional e acrescido da diferença do pedágio
    Retorna (frete: str)
    """
    return f"R$ {(diff_km * racional) + diff_pedagio:.2f}" 

# # Função de contagem de pedágios no trajeto
# def conta_pedagios(infos_rotas):
#     """
#     Conta a quantidade de pedágios no trajeto entre os dois endereços escolhidos.
#     Retorna (qtd_pedagios: int).
#     """
#     pedagios = lista_pedagios(infos_rotas)

#     return len(pedagios)

# # Função de soma dos valores do pedágio no trajeto
# def soma_tarifas(infos_rotas):
#     """
#     Soma os valores dos pedágios no trajeto entre os dois endereços escolhidos.
#     Retorna (valor_total: float).
#     """
#     valor_total = 0
#     for i in range(len(infos_rotas["pedagios"])):
#         valor_pedagio = list(infos_rotas["pedagios"][i]["tarifa"].values())[0]
#         valor_total += valor_pedagio

#     return valor_total

def google_routes_api(origin, destination, waypoints=None, api_key=None):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "routes.distanceMeters,"
            "routes.duration,"
            "routes.polyline.encodedPolyline,"
            "routes.legs.distanceMeters,"
            "routes.legs.duration,"
            "routes.travelAdvisory.tollInfo"
        )
    }

    body = {
        "origin": {"address": origin},
        "destination": {"address": destination},
        "travelMode": "DRIVE",
        "extraComputations": ["TOLLS"],
        "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
        "polylineQuality": "OVERVIEW"
    }

    if waypoints:
        body["intermediates"] = [{"address": w} for w in waypoints]

    response = requests.post(url, headers=headers, json=body).json()

    return response

def gerar_mapa(encoded_polyline):
    coords = polyline.decode(encoded_polyline)

    lat0, lng0 = coords[0]
    mapa = folium.Map(location=[lat0, lng0], zoom_start=12)

    folium.PolyLine(coords, color="blue", weight=5).add_to(mapa)

    return mapa

# Função de cálculo de distância entre dois endereços e guarda numa lista para ser usado depois
def dist_tempo(infos_rotas):
    """
    Cálcula a distância entre dois endereços escolhidos.
    Retorna (respostas: tuple -> texto: str, valor: int).
    """
    resposta = infos_rotas["routes"][0]["legs"]

    return resposta

def converter_tempo(tempo):
    horas = tempo // 3600
    minutos = (tempo % 3600) // 60
    segundos = tempo % 60

    return horas, minutos, segundos

# Faz os cálculos e retorna um dicionário com as informações necessárias para serem apresentadas
def vectura(origem: str, destino: str, recarga: str, destino_2: str, chave_api: str, racional: int):

    if origem == None or destino == None or recarga == None or destino_2 == None or chave_api == "" or racional <= 0:
        mensagem = "❌ Não foi possível realizar os cálculos. Confirme se os parâmetros estão todos preenchidos corretamente."

        return False, mensagem, None

# # ---- REQUEST API QUALP ----

#     # Request na API do QualP para os dois trechos e retorna os dados no json
#     dados_trecho_1_qualp = api_qualp(origem=origem, destino=destino, eixos=eixos_carregado, key=confidential.qualp_key)
#     dados_trecho_2_qualp = api_qualp(origem=destino, destino=recarga, eixos=eixos_descarregado, key=confidential.qualp_key)
#     dados_trecho_3_qualp = api_qualp(origem=recarga, destino=destino_2, eixos=eixos_carregado, key=confidential.qualp_key)
#     dados_trecho_4_qualp = api_qualp(origem=destino_2, destino=origem, eixos=eixos_descarregado, key=confidential.qualp_key)

#     dados_trecho_volta_simples_qualp = api_qualp(origem=destino, destino=origem, eixos=eixos_descarregado, key=confidential.qualp_key)

# # ---- REQUEST API QUALP ----

# ---- REQUEST API GOOGLE ----

    dados_ida_volta_simples = google_routes_api(origin=origem, destination=origem, waypoints=[destino], api_key=chave_api)
    dados_retorno_carregado = google_routes_api(origin=origem, destination=origem, waypoints=[destino, recarga, destino_2], api_key=chave_api)

# ---- REQUEST API GOOGLE ----

    dados_caso_1 = dist_tempo(dados_ida_volta_simples)
    dados_caso_2 = dist_tempo(dados_retorno_carregado)

# ---- DISTÂNCIAS ----

    # Pega a distância (tanto texto quanto valor) do JSON de resultado para todos os trechos
    dist_trecho_1 = round((dados_caso_2[0]["distanceMeters"]) / 1000, 1)
    dist_trecho_2 = round((dados_caso_2[1]["distanceMeters"]) / 1000, 1)
    dist_trecho_3 = round((dados_caso_2[2]["distanceMeters"]) / 1000, 1)
    dist_trecho_4 = round((dados_caso_2[3]["distanceMeters"]) / 1000, 1)

    # Pega a distância (tanto texto quanto valor) do JSON considerando a volta do trecho_1
    dist_ida = round((dados_caso_1[0]["distanceMeters"]) / 1000, 1)
    dist_volta = round((dados_caso_1[1]["distanceMeters"]) / 1000, 1)

    # Faz o cálculo da distância do trecho total para os 2 casos (ida e volta direta ou ida, descarga, recarga, descarga e volta)
    dist_caso_1 = dist_ida + dist_volta
    dist_caso_2 = dist_trecho_1 + dist_trecho_2 + dist_trecho_3 + dist_trecho_4

    # Faz o cálculo da diferença de km que serão rodados nos dois casos.
    dist_diff = abs(dist_caso_1 - dist_caso_2)

# ---- DISTÂNCIAS ----

# ---- TEMPO DE VIAGEM ----

    # Pega o tempo de viagem do JSON de resultado para todos os trechos
    tempo_trecho_1_segundo = int(dados_caso_2[0]["duration"].replace("s", ""))
    horas_trecho_1, minutos_trecho_1, segundos_trecho_1 = converter_tempo(tempo_trecho_1_segundo)
    tempos_total_trecho_1 = f"{horas_trecho_1:02}:{minutos_trecho_1:02}:{segundos_trecho_1:02}"

    tempo_trecho_2_segundo = int(dados_caso_2[1]["duration"].replace("s", ""))
    horas_trecho_2, minutos_trecho_2, segundos_trecho_2 = converter_tempo(tempo_trecho_2_segundo)
    tempos_total_trecho_2 = f"{horas_trecho_2:02}:{minutos_trecho_2:02}:{segundos_trecho_2:02}"

    tempo_trecho_3_segundo = int(dados_caso_2[2]["duration"].replace("s", ""))
    horas_trecho_3, minutos_trecho_3, segundos_trecho_3 = converter_tempo(tempo_trecho_3_segundo)
    tempos_total_trecho_3 = f"{horas_trecho_3:02}:{minutos_trecho_3:02}:{segundos_trecho_3:02}"

    tempo_trecho_4_segundo = int(dados_caso_2[3]["duration"].replace("s", ""))
    horas_trecho_4, minutos_trecho_4, segundos_trecho_4 = converter_tempo(tempo_trecho_4_segundo)
    tempos_total_trecho_4 = f"{horas_trecho_4:02}:{minutos_trecho_4:02}:{segundos_trecho_4:02}"

    # Pega o tempo de viagem do JSON considerando a volta do trecho_1
    tempo_ida_segundo = int(dados_caso_1[0]["duration"].replace("s", ""))
    horas_ida, minutos_ida, segundos_ida = converter_tempo(tempo_ida_segundo)
    tempo_total_ida = f"{horas_ida:02}:{minutos_ida:02}:{segundos_ida:02}"

    tempo_volta_segundo = int(dados_caso_1[1]["duration"].replace("s", ""))
    horas_volta, minutos_volta, segundos_volta = converter_tempo(tempo_volta_segundo)
    tempo_total_volta = f"{horas_volta:02}:{minutos_volta:02}:{segundos_volta:02}"

    # Faz o cálculo do tempo total de viagem do trecho total para os 2 casos (ida e volta direta ou ida, descarga, recarga, descarga e volta)
    tempo_1 = tempo_ida_segundo + tempo_volta_segundo
    horas_1, minutos_1, segundos_1 = converter_tempo(tempo_1)
    tempos_total_1 = f"{horas_1:02}:{minutos_1:02}:{segundos_1:02}"

    tempo_2 = tempo_trecho_1_segundo + tempo_trecho_2_segundo + tempo_trecho_3_segundo + tempo_trecho_4_segundo
    horas_2, minutos_2, segundos_2 = converter_tempo(tempo_2)
    tempos_total_2 = f"{horas_2:02}:{minutos_2:02}:{segundos_2:02}"

    # Faz o cálculo da diferença do tempo total de viagem que serão rodados nos dois casos.
    tempo_diff = abs(tempo_1 - tempo_2)
    horas_diff, minutos_diff, segundos_diff = converter_tempo(tempo_diff)
    tempos_total_diff = f"{horas_diff:02}:{minutos_diff:02}:{segundos_diff:02}"

# ---- TEMPO DE VIAGEM ----

# # ---- QUANTIDADE PEDÁGIOS ----

#     # Pega a quantidade de pedágios do JSON de resultado para todos os trechos
#     pedagios_trecho_1 = conta_pedagios(dados_trecho_1_qualp)
#     pedagios_trecho_2 = conta_pedagios(dados_trecho_2_qualp)
#     pedagios_trecho_3 = conta_pedagios(dados_trecho_3_qualp)
#     pedagios_trecho_4 = conta_pedagios(dados_trecho_4_qualp)

#     # Pega a quantidade de pedágios do JSON considerando a volta do trecho_1
#     pedagios_trecho_volta_simples = conta_pedagios(dados_trecho_volta_simples_qualp)

#     # Faz o cálculo da quantidade total de pedágios do trecho total para os 2 casos (ida e volta direta ou ida, descarga, recarga, descarga e volta)
#     pedagios_total_1 = pedagios_trecho_1 + pedagios_trecho_volta_simples
#     pedagios_total_2 = pedagios_trecho_1 + pedagios_trecho_2 + pedagios_trecho_3 + pedagios_trecho_4

#     # Faz o cálculo da diferença da quantidade de pedágios presentes nos dois casos.
#     pedagios_diff = abs(pedagios_total_1 - pedagios_total_2)

# # ---- QUANTIDADE PEDÁGIOS ----

# ---- SOMA TARIFAS PEDÁGIOS ----

    # # Pega os valores dos pedágios do JSON de resultado para todos os trechos e soma
    # tarifas_trecho_1 = soma_tarifas(dados_trecho_1_qualp)
    # tarifas_trecho_2 = soma_tarifas(dados_trecho_2_qualp)
    # tarifas_trecho_3 = soma_tarifas(dados_trecho_3_qualp)
    # tarifas_trecho_4 = soma_tarifas(dados_trecho_4_qualp)

    # # Pega os valores dos pedágios do JSON considerando a volta do trecho_1
    # tarifas_trecho_volta_simples = soma_tarifas(dados_trecho_volta_simples_qualp)

    # Faz o cálculo do valor total em pedágios do trecho total para os 2 casos (ida e volta direta ou ida, descarga, recarga, descarga e volta)    
    tarifas_total_1_real = dados_ida_volta_simples["routes"][0]["travelAdvisory"]["tollInfo"]["estimatedPrice"][0]["units"]
    tarifas_total_1_centavo = str(dados_ida_volta_simples["routes"][0]["travelAdvisory"]["tollInfo"]["estimatedPrice"][0]["nanos"])
    tarifas_total_2_real = dados_retorno_carregado["routes"][0]["travelAdvisory"]["tollInfo"]["estimatedPrice"][0]["units"]
    tarifas_total_2_centavo = str(dados_retorno_carregado["routes"][0]["travelAdvisory"]["tollInfo"]["estimatedPrice"][0]["nanos"])

    tarifas_total_1 = float(f"{tarifas_total_1_real}.{tarifas_total_1_centavo[:2]}") * 6
    tarifas_total_2 = float(f"{tarifas_total_2_real}.{tarifas_total_2_centavo[:2]}") * 6

    # Faz o cálculo do valor total em pedágios presentes nos dois casos.
    tarifas_diff = abs(tarifas_total_1 - tarifas_total_2)

# ---- SOMA TARIFAS PEDÁGIOS ----

# # ---- LISTA PEDÁGIOS ----

#     # Monta a lista com o nome dos pedágios no trecho
#     lista_pedagios_trecho_1 = lista_pedagios(dados_trecho_1_qualp)
#     lista_pedagios_trecho_2 = lista_pedagios(dados_trecho_2_qualp)
#     lista_pedagios_trecho_3 = lista_pedagios(dados_trecho_3_qualp)
#     lista_pedagios_trecho_4 = lista_pedagios(dados_trecho_4_qualp)
    
#     # Monta a lista com o nome dos pedágios considerando a volta do trecho_1
#     lista_pedagios_trecho_volta_simples = lista_pedagios(dados_trecho_volta_simples_qualp)

#     # Monta a lista com o nome de todos os pedágios do trecho total para os 2 casos
#     lista_pedagios_total_1 = list(dict.fromkeys(lista_pedagios_trecho_1 + lista_pedagios_trecho_volta_simples))
#     lista_pedagios_total_2 = list(dict.fromkeys(lista_pedagios_trecho_1 + lista_pedagios_trecho_2 + lista_pedagios_trecho_3 + lista_pedagios_trecho_4))

# # ---- LISTA PEDÁGIOS ----

# ---- CÁLCULO FRETE ----

    valor_frete = calculo_frete(diff_pedagio=tarifas_diff, diff_km=dist_diff, racional=racional)

# ---- CÁLCULO FRETE ----

# ---- DATA CÁLCULO ----

    # Salva a data do cálculo
    data_calculo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# ---- DATA CÁLCULO ----

# ---- MAPAS ROTAS ----

    # Extrai os links das imagens das rotas
    # rota_trecho_1 = dados_trecho_1_qualp["rota_imagem"]
    # rota_trecho_2 = dados_trecho_2_qualp["rota_imagem"]
    # rota_trecho_3 = dados_trecho_3_qualp["rota_imagem"]
    # rota_trecho_4 = dados_trecho_4_qualp["rota_imagem"]

    # rota_trecho_volta_simples = dados_trecho_volta_simples_qualp["rota_imagem"]

    polilinha_1 = dados_ida_volta_simples["routes"][0]["polyline"]["encodedPolyline"]
    polilinha_2 = dados_retorno_carregado["routes"][0]["polyline"]["encodedPolyline"]

# ---- MAPAS ROTAS ----

# ---- DICIONÁRIO FINAL ----

    dados = {"data_calculo":data_calculo,
            
            "origem": origem,
            "destino_1": destino,
            "recarga": recarga,
            "destino_2": destino_2,
            "retorno": origem,

            "km_ida": f"{dist_ida:.2f} km",
            "km_volta": f"{dist_volta:.2f} km",
            "km_total_simples": f"{dist_caso_1:.2f} km",

            "tempo_ida": tempo_total_ida,
            "tempo_volta": tempo_total_volta,
            "tempo_total_simples": tempos_total_1,

            # "qtd_pedagio_ida": f"{pedagios_trecho_1} pedágios",
            # "qtd_pedagio_volta": f"{pedagios_trecho_volta_simples} pedágios",
            # "qtd_pedagio_total_simples": f"{pedagios_total_1} pedágios",

            # "valor_pedagios_ida": f"R$ {tarifas_trecho_1:.2f}",
            # "valor_pedagios_volta": f"R$ {tarifas_trecho_volta_simples:.2f}",
            "valor_pedagio_total_simples": f"R$ {tarifas_total_1:.2f}",

            # "lista_pedagios_ida": lista_pedagios_trecho_1,
            # "lista_pedagios_volta": lista_pedagios_trecho_volta_simples,
            # "lista_pedagios_total_simples": lista_pedagios_total_1,

            "polilinha_1": polilinha_1,

            "km_trecho_1": f"{dist_trecho_1:.2f} km",
            "km_trecho_2": f"{dist_trecho_2:.2f} km",
            "km_trecho_3": f"{dist_trecho_3:.2f} km",
            "km_trecho_4": f"{dist_trecho_4:.2f} km",
            "km_total": f"{dist_caso_2:.2f} km",

            "tempo_trecho_1": tempos_total_trecho_1,
            "tempo_trecho_2": tempos_total_trecho_2,
            "tempo_trecho_3": tempos_total_trecho_3,
            "tempo_trecho_4": tempos_total_trecho_4,
            "tempo_total": tempos_total_2,

            # "qtd_pedagios_trecho_1": f"{pedagios_trecho_1} pedágios",
            # "qtd_pedagios_trecho_2": f"{pedagios_trecho_2} pedágios",
            # "qtd_pedagios_trecho_3": f"{pedagios_trecho_3} pedágios",
            # "qtd_pedagios_trecho_4": f"{pedagios_trecho_4} pedágios",
            # "qtd_total_pedagios": f"{pedagios_total_2} pedágios",

            # "valor_pedagio_trecho_1": f"R$ {tarifas_trecho_1:.2f}",
            # "valor_pedagio_trecho_2": f"R$ {tarifas_trecho_2:.2f}",
            # "valor_pedagio_trecho_3": f"R$ {tarifas_trecho_3:.2f}",
            # "valor_pedagio_trecho_4": f"R$ {tarifas_trecho_4:.2f}",
            "valor_pedagios_total": f"R$ {tarifas_total_2:.2f}",

            # "lista_pedagios_trecho_1": lista_pedagios_trecho_1,
            # "lista_pedagios_trecho_2": lista_pedagios_trecho_2,
            # "lista_pedagios_trecho_3": lista_pedagios_trecho_3,
            # "lista_pedagios_trecho_4": lista_pedagios_trecho_4,
            # "lista_pedagios_total": lista_pedagios_total_2,

            "polilinha_2": polilinha_2,
            # "mapa_rota_trecho_2": rota_trecho_2,
            # "mapa_rota_trecho_3": rota_trecho_3,
            # "mapa_rota_trecho_4": rota_trecho_4,

            "km_diff": f"{dist_diff:.2f} km",
            "tempo_diff": tempos_total_diff,
            # "qtd_pedagio_diff": f"{pedagios_diff} pedágios",
            "tarifas_diff": f"R$ {tarifas_diff:.2f}",
            "racional": racional,

            "valor_excedente": valor_frete
        }
    
    mensagem = "✅ Cálculos realizados com sucesso!"

    return True, mensagem, dados

def mock_from_file():
    with open("exemplo_qualp.json", "r", encoding="utf-8") as f:
        return json.load(f)

# # Faz o request na API do QualP
# def api_qualp(origem: str, destino: str, eixos: int, key: str):

#     url = 'https://api.qualp.com.br/rotas/v4'

#     data = {
#         "locations": [origem, destino],
#         "config": {
#             "route": {
#                 "optimized_route": True,
#                 "optimized_route_destination": "last",
#                 "calculate_return": False,
#                 "alternative_routes": "0",
#                 "avoid_locations": False,
#                 "avoid_locations_key": "",
#                 "type_route": "efficient"
#             },
#             "vehicle": {
#                 "type": "truck",
#                 "axis": eixos,
#                 "top_speed": ""
#             },
#             "tolls": {
#                 "retroactive_date": ""
#             },
#             "freight_table": {
#                 "category": "all",
#                 "freight_load": "all",
#                 "axis": "all"
#             },
#             "fuel_consumption": {
#                 "fuel_price": "",
#                 "km_fuel": ""
#             },
#             "private_places": {
#                 "max_distance_from_location_to_route": "1000",
#                 "categories": True,
#                 "areas": True,
#                 "contacts": True,
#                 "products": True,
#                 "services": True
#             }
#         },
#         "show": {
#             "tolls": True,
#             "freight_table": False,
#             "maneuvers": False,
#             "truck_scales": False,
#             "static_image": True,
#             "link_to_qualp": True,
#             "private_places": False,
#             "polyline": False,
#             "simplified_polyline": False,
#             "ufs": False,
#             "fuel_consumption": False,
#             "link_to_qualp_report": False,
#             "segments_information": False
#         },
#         "format": "json",
#         "exception_key": ""
#     }

#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json',
#         'Access-Token': key
#     }

#     response = requests.post(url=url, json=data, headers=headers)

#     return response.json()

