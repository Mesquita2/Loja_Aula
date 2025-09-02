import streamlit as st
import os
import pandas as pd

# Caminho da pasta "planilha"
BASE_DIR = os.path.dirname(__file__)
FOLDER = os.path.join(BASE_DIR, "..", "planilha")  # volta uma pasta porque está em models
FILE_NAME = os.path.join(FOLDER, "vendedores.xlsx")

def salvar_vendedores_excel():
    """Salva todos os vendedores no arquivo Excel."""
    os.makedirs(FOLDER, exist_ok=True)
    df = pd.DataFrame(st.session_state.vendedores)
    df.to_excel(FILE_NAME, index=False)

def app():
    st.title("Cadastro de Vendedores")

    # Inicializar sessão
    if "vendedores" not in st.session_state:
        # Verifica se o arquivo existe antes de tentar abrir
        if os.path.exists(FILE_NAME):
            try:
                st.session_state.vendedores = pd.read_excel(FILE_NAME).to_dict(orient="records")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo Excel: {e}")
                st.session_state.vendedores = []
        else:
            st.session_state.vendedores = []

    # --- Cadastro de vendedor ---
    st.header("Cadastrar Vendedor")
    with st.form("form_vendedor"):
        nome = st.text_input("Nome do Vendedor")
        submit_vendedor = st.form_submit_button("Adicionar Vendedor")

        if submit_vendedor and nome:
            st.session_state.vendedores.append({"nome": nome})
            salvar_vendedores_excel()
            st.success(f"Vendedor {nome} cadastrado com sucesso!")

    # --- Histórico de vendedores ---
    st.header("Histórico de Vendedores")
    if st.session_state.vendedores:
        df_vendedores = pd.DataFrame(st.session_state.vendedores)
        st.dataframe(df_vendedores)

        # --- Apagar vendedores ---
        st.subheader("Apagar Vendedores")
        opcoes = [
            f"{i} - {v['nome']}" 
            for i, v in enumerate(st.session_state.vendedores)
        ]
        selecionados = st.multiselect("Selecione vendedores para apagar", opcoes)

        if st.button("Apagar Selecionados"):
            if selecionados:
                indices = [int(opcao.split(" - ")[0]) for opcao in selecionados]
                st.session_state.vendedores = [
                    v for i, v in enumerate(st.session_state.vendedores) if i not in indices
                ]
                salvar_vendedores_excel()
                st.success("Vendedor(es) removido(s) com sucesso!")
                st.rerun()
            else:
                st.warning("Nenhum vendedor selecionado.")
                
    else:
        st.info("Nenhum vendedor cadastrado ainda.")
