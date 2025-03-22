import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime




DADOS_FILE = "movimentacoes.json"
USUARIOS_FILE = "usuarios.json"

if not os.path.exists(DADOS_FILE):
    with open(DADOS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump({}, f)

def carregar_dados():
    with open(DADOS_FILE, "r") as f:
        return json.load(f)

def salvar_dados(dados_movimentacoes):
    with open(DADOS_FILE, "w") as f:
        json.dump(dados_movimentacoes, f, indent=4)

def exportar_para_excel(dados_movimentacoes):
    df = pd.DataFrame(dados_movimentacoes, columns=["Material", "Tipo", "Quantidade", "Data", "Colaborador", "Lote", "Status", "Pago por", "Recebido por"])
    df.to_excel("movimentacoes.xlsx", index=False)
    st.success("Exportado para Excel com sucesso!")

def carregar_usuarios():
    with open(USUARIOS_FILE, "r") as f:
        return json.load(f)

def criar_novo_usuario():
    st.subheader("Criar Novo Usuário")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Criar Usuário"):
        usuarios = carregar_usuarios()
        if usuario in usuarios:
            st.error("Usuário já existe!")
        else:
            usuarios[usuario] = senha
            with open(USUARIOS_FILE, "w") as f:
                json.dump(usuarios, f, indent=4)
            st.success("Usuário criado com sucesso!")

def autenticar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    return usuarios.get(usuario) == senha

def main():
    st.title("Controle de Pagamentos")
    dados_movimentacoes = carregar_dados()
    
    with st.sidebar:
        st.header("Menu")
        opcao = st.radio("Escolha uma opção:", ["Registrar Movimentação", "Visualizar Movimentações", "Criar Usuário", "Exportar para Excel"])
    
    if opcao == "Registrar Movimentação":
        st.subheader("Registrar Nova Movimentação")
        material = st.text_input("Material")
        tipo = st.selectbox("Tipo", ["Solicitação", "Entrada"])
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        data = st.text_input("Data", value=datetime.now().strftime('%d/%m/%Y'))
        lote = st.text_input("Lote")
        
        if st.button("Adicionar Movimentação"):
            if material and tipo and quantidade and lote:
                nova_movimentacao = [material, tipo, int(quantidade), data, "", lote, "Pendente", "", ""]
                dados_movimentacoes.append(nova_movimentacao)
                salvar_dados(dados_movimentacoes)
                st.success("Movimentação adicionada com sucesso!")
            else:
                st.error("Todos os campos são obrigatórios!")
    
    elif opcao == "Visualizar Movimentações":
        st.subheader("Movimentações Registradas")
        lote_filter = st.text_input("Filtrar por Lote")
        
        dados_filtrados = [mov for mov in dados_movimentacoes if lote_filter.lower() in mov[5].lower()] if lote_filter else dados_movimentacoes

        for idx, mov in enumerate(dados_filtrados):
            # Definir cor do status
            if mov[6] == "Pendente":
                status_color = "red"  # 🔴 Vermelho
            elif mov[6] == "Pendente de Assinatura":
                status_color = "orange"  # 🟠 Laranja
            else:
                status_color = "green"  # 🟢 Verde
            
            # Exibir os itens diretamente com a cor correspondente
            st.markdown(f"<p style='color:{status_color}; font-weight:bold;'>{mov[0]} - {mov[5]} ({mov[6]})</p>", unsafe_allow_html=True)

            if mov[6] == "Pendente":
                pagador = st.text_input(f"Usuário (Quem paga) - {idx}", key=f"pagador_{idx}")
                senha_pagador = st.text_input(f"Senha", type="password", key=f"senha_pagador_{idx}")
                if st.button(f"Confirmar Pagamento {idx}"):
                    if autenticar_usuario(pagador, senha_pagador):
                        mov[6] = "Pendente de Assinatura"
                        mov[7] = pagador
                        salvar_dados(dados_movimentacoes)
                        st.success("Pagamento registrado, aguardando recebedor!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")

            elif mov[6] == "Pendente de Assinatura":
                recebedor = st.text_input(f"Usuário (Quem recebe) - {idx}", key=f"recebedor_{idx}")
                senha_recebedor = st.text_input(f"Senha", type="password", key=f"senha_recebedor_{idx}")
                if st.button(f"Confirmar Recebimento {idx}"):
                    if autenticar_usuario(recebedor, senha_recebedor):
                        mov[6] = "Pago"
                        mov[8] = recebedor
                        salvar_dados(dados_movimentacoes)
                        st.success("Pagamento concluído!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")

    elif opcao == "Criar Usuário":
        criar_novo_usuario()
    
    elif opcao == "Exportar para Excel":
        exportar_para_excel(dados_movimentacoes)
        with open("movimentacoes.xlsx", "rb") as f:
            st.download_button("Baixar Excel", f, file_name="movimentacoes.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
