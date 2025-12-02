import streamlit as st
from utils import carregar_enderecos, carregar_historico, carregar_fixos
from PIL import Image
from telas.telas import tela_0, tela_1, tela_2, tela_3

def main():

    icon = Image.open("vectura_icon.png") # Carrega a imagem do ícone na aba do navegador
   
    st.set_page_config(page_title="Vectura", page_icon=icon, layout="wide") # Configurações da aba

    st.title("*Vectura*") # Título

    if "enderecos" not in st.session_state:
        st.session_state["enderecos"] = carregar_enderecos() # Carrega e guarda os endereços salvos
    
    if "historico" not in st.session_state:
        st.session_state["historico"] = carregar_historico()

    if "fixos" not in st.session_state:
        st.session_state["fixos"] = carregar_fixos()

    aba = st.pills("Selecione uma página", options=["Início", "Endereços", "Histórico"], selection_mode="single") # Cria as abas

    # ---- Página Inicial ----

    if aba == None:

        tela_0()
    
    # ---- Fim Página Inicial ----


    # ---- Página Cálculo ----
    
    if aba == "Início":

        tela_1()
    
    # ---- Fim Página Cálculo ----


    # ---- Página Cadastro ----

    if aba == "Endereços":

        tela_2()
    
    # ---- Fim Página Cadastro ----


    # ---- Página Histórico ----

    if aba == "Histórico":

        tela_3()

    # ---- Fim Página Histórico ---- 


if __name__ == "__main__":
    main()