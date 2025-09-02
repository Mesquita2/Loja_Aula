import streamlit as st
import models.vendas as vendas
import models.vendedores as vendedores 

VENDEDORES = []

st.title("Sistema de Loja")

# Menu lateral
pagina = st.sidebar.radio("Navegação", ["Início", "Vendas", "Vendedores"])

if pagina == "Início":
    st.header("Bem-vindo ao sistema de controle de vendas!")
    st.write("Use o menu lateral para navegar até a página de vendas.")
elif pagina == "Vendas":
    vendas.app()  
elif pagina == "Vendedores":
    vendedores.app()
