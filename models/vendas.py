import streamlit as st
import pandas as pd
import os

# --- Caminhos robustos ---
# File is in models/ so project root is one level up
MODELS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(MODELS_DIR, ".."))
PLANILHA_DIR = os.path.join(PROJECT_ROOT, "planilha")

# Arquivos
FILE_NAME_VENDAS = os.path.join(PLANILHA_DIR, "compras.xlsx")
FILE_NAME_VENDEDORES = os.path.join(PLANILHA_DIR, "vendedores.xlsx")

def salvar_vendas_excel():
    os.makedirs(PLANILHA_DIR, exist_ok=True)
    df = pd.DataFrame(st.session_state.vendas)
    df.to_excel(FILE_NAME_VENDAS, index=False)

def carregar_lista_vendedores():
    """Retorna lista de nomes de vendedores ([] se não existir)."""
    if os.path.exists(FILE_NAME_VENDEDORES):
        try:
            df = pd.read_excel(FILE_NAME_VENDEDORES)
            if "nome" in df.columns:
                return df["nome"].astype(str).tolist()
            else:
                st.warning("Arquivo de vendedores encontrado mas não tem coluna 'nome'.")
                return []
        except Exception as e:
            st.error(f"Erro ao ler arquivo de vendedores: {e}")
            return []
    return []

def app():
    st.title("Controle de Vendas")

    # Inicializar clientes
    if "clientes" not in st.session_state:
        st.session_state.clientes = []

    # Inicializar vendas
    if "vendas" not in st.session_state:
        if os.path.exists(FILE_NAME_VENDAS):
            try:
                st.session_state.vendas = pd.read_excel(FILE_NAME_VENDAS).to_dict(orient="records")
            except Exception as e:
                st.error(f"Erro ao ler arquivo de vendas: {e}")
                st.session_state.vendas = []
        else:
            st.session_state.vendas = []

    # Carregar vendedores (sempre que a página renderiza)
    lista_vendedores = carregar_lista_vendedores()

    # Opção para forçar atualização da lista sem reiniciar navegador
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Vendedores Existentes:** " + (", ".join(lista_vendedores) if lista_vendedores else "nenhum"))

    # --- Cadastro de cliente ---
    st.header("Cadastrar Cliente")
    with st.form("form_cliente"):
        nome = st.text_input("Nome do Cliente")
        telefone = st.text_input("Telefone (opcional)")
        submit_cliente = st.form_submit_button("Adicionar Cliente")
        if submit_cliente and nome:
            st.session_state.clientes.append({"nome": nome, "telefone": telefone})
            st.success(f"Cliente {nome} cadastrado com sucesso!")

    # --- Registrar venda ---
    st.header("Registrar Venda")
    if st.session_state.clientes:
        with st.form("form_venda"):
            cliente = st.selectbox("Cliente", [c["nome"] for c in st.session_state.clientes])
            produto = st.text_input("Produto / Serviço")
            valor = st.number_input("Valor Total (R$)", min_value=0.0, step=1.0, format="%.2f")
            if lista_vendedores:
                vendedor = st.selectbox("Vendedor", lista_vendedores)
            else:
                st.warning("Nenhum vendedor cadastrado. Cadastre na aba Vendedores.")
                vendedor = None

            pagamento = st.radio("Forma de Pagamento", ["À Vista", "A Prazo"])
            valor_pago = 0.0
            if pagamento == "A Prazo":
                valor_pago = st.number_input("Valor já pago (R$)", min_value=0.0, max_value=valor, step=1.0, format="%.2f")

            submit_venda = st.form_submit_button("Registrar Venda")
            if submit_venda:
                if not cliente or not produto:
                    st.warning("Preencha cliente e produto.")
                elif vendedor is None:
                    st.warning("Selecione um vendedor válido.")
                else:
                    st.session_state.vendas.append({
                        "vendedor": vendedor,
                        "cliente": cliente,
                        "produto": produto,
                        "valor_total": float(valor),
                        "pagamento": pagamento,
                        "valor_pago": float(valor if pagamento == "À Vista" else valor_pago),
                        "valor_a_receber": 0.0 if pagamento == "À Vista" else float(valor - valor_pago)
                    })
                    salvar_vendas_excel()
                    st.success(f"Venda registrada para {cliente} e salva em {FILE_NAME_VENDAS}")
    else:
        st.info("Cadastre um cliente antes de registrar vendas.")

    # --- Histórico de vendas ---
    st.header("Histórico de Vendas")
    if st.session_state.vendas:
        df_vendas = pd.DataFrame(st.session_state.vendas)
        st.dataframe(df_vendas)

        total = df_vendas["valor_total"].sum()
        total_pago = df_vendas["valor_pago"].sum()
        st.write(f"**Total em vendas: R$ {total:.2f}**")
        st.write(f"**Total já recebido: R$ {total_pago:.2f}**")
        st.write(f"**Total a receber: R$ {total - total_pago:.2f}**")

        # Apagar vendas
        st.subheader("Apagar Vendas")
        opcoes = [
            f"{i} - {v['cliente']} | {v['produto']} | R$ {v['valor_total']}"
            for i, v in enumerate(st.session_state.vendas)
        ]
        selecionados = st.multiselect("Selecione vendas para apagar", opcoes)
        if st.button("Apagar Selecionados"):
            if selecionados:
                indices = [int(opcao.split(" - ")[0]) for opcao in selecionados]
                st.session_state.vendas = [
                    v for i, v in enumerate(st.session_state.vendas) if i not in indices
                ]
                salvar_vendas_excel()
                st.success("Venda(s) removida(s) com sucesso!")
                st.rerun()
            else:
                st.warning("Nenhuma venda selecionada.")
    else:
        st.info("Nenhuma venda registrada ainda.")
