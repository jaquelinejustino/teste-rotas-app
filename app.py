import streamlit as st
import pandas as pd
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Função para processar o arquivo e calcular rota
def processar_rotas(arquivo):
    try:
        dados = pd.read_excel(arquivo, engine="openpyxl")
        dados["Latitude"] = dados["Latitude"].astype(str).str.replace(",", ".").astype(float)
        dados["Longitude"] = dados["Longitude"].astype(str).str.replace(",", ".").astype(float)
        coordenadas = list(zip(dados["Latitude"], dados["Longitude"]))
        
        # Calcula a distância total percorrida
        distancia_total = sum(
            geodesic(coordenadas[i], coordenadas[i + 1]).km
            for i in range(len(coordenadas) - 1)
        )
        
        # Gera o mapa interativo
        mapa = folium.Map(location=coordenadas[0], zoom_start=14)
        folium.PolyLine(coordenadas, color="blue", weight=5, opacity=0.7).add_to(mapa)
        for idx, ponto in enumerate(coordenadas):
            folium.Marker(location=ponto, popup=f"Ponto {idx + 1}").add_to(mapa)
        
        return distancia_total, mapa
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None, None

# Interface da aplicação
st.title("Aplicação de Rotas e Distância Percorrida")

# Upload do arquivo
arquivo = st.file_uploader("Envie o arquivo em Excel do relatório de rota percorrida com as colunas 'Latitude' e 'Longitude'", type=["xlsx"])

if arquivo:
    distancia, mapa = processar_rotas(arquivo)
    
    if distancia and mapa:
        st.success(f"Distância total percorrida: {distancia:.2f} km")
        
        # Mostra o mapa interativo
        st.write("Mapa interativo:")
        st_folium(mapa, width=700, height=500)
