import streamlit as st
import pandas as pd
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
import openrouteservice
import numpy as np

# Adicione sua API Key do OpenRouteService
ORS_API_KEY = "SUA_API_KEY_AQUI"
client = openrouteservice.Client(key=ORS_API_KEY)

# Função para processar o arquivo e calcular rota
def processar_rotas(arquivo):
    try:
        dados = pd.read_excel(arquivo, engine="openpyxl")
        dados["Latitude"] = dados["Latitude"].astype(str).str.replace(",", ".").astype(float)
        dados["Longitude"] = dados["Longitude"].astype(str).str.replace(",", ".").astype(float)
        dados["Data/Hora"] = pd.to_datetime(dados["Data/Hora"])

        # Calcular o intervalo médio entre os pontos
        dados['Intervalo'] = dados['Data/Hora'].diff().dt.total_seconds() / 60  # intervalo em minutos
        intervalo_medio = dados['Intervalo'].mean()

        coordenadas = list(zip(dados["Longitude"], dados["Latitude"]))  # Ordem correta para ORS

        pontos_corrigidos = [coordenadas[0]]  # Começa com o primeiro ponto

        # Ajusta o intervalo de tempo, se necessário
        for i in range(1, len(coordenadas)):
            intervalo_entre_pontos = dados['Intervalo'].iloc[i]
            if intervalo_entre_pontos > intervalo_medio:
                # Se o intervalo entre os pontos for maior que a média, faz a interpolação
                interpolacao = client.directions(
                    coordinates=[coordenadas[i-1], coordenadas[i]],
                    profile="driving-car",
                    format="geojson"
                )
                # Pega os pontos da interpolação
                pontos_interpolados = [(p[0], p[1]) for p in interpolacao["routes"][0]["geometry"]["coordinates"]]
                pontos_corrigidos.extend(pontos_interpolados[1:])  # Adiciona os pontos interpolados (sem o primeiro ponto, que já está)
            else:
                pontos_corrigidos.append(coordenadas[i])

        # Calcula a distância total percorrida após correção
        distancia_total = sum(
            geodesic((lat1, lon1), (lat2, lon2)).km
            for (lon1, lat1), (lon2, lat2) in zip(pontos_corrigidos[:-1], pontos_corrigidos[1:])
        )

        # Gera o mapa interativo
        mapa = folium.Map(location=pontos_corrigidos[0], zoom_start=14)
        folium.PolyLine(pontos_corrigidos, color="blue", weight=5, opacity=0.7).add_to(mapa)

        for idx, ponto in enumerate(pontos_corrigidos):
            folium.Marker(location=(ponto[1], ponto[0]), popup=f"Ponto {idx + 1}").add_to(mapa)

        return distancia_total, mapa

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None, None

# Interface da aplicação
st.title("Aplicação de Rotas e Distância Percorrida")

# Upload do arquivo
arquivo = st.file_uploader("Envie o arquivo em Excel do relatório de rota percorrida com as colunas 'Latitude', 'Longitude' e 'Data/Hora'", type=["xlsx"])

if arquivo:
    distancia, mapa = processar_rotas(arquivo)

    if distancia and mapa:
        st.success(f"Distância total percorrida: {distancia:.2f} km")

        # Mostra o mapa interativo
        st.write("Mapa interativo:")
        st_folium(mapa, width=700, height=500)
