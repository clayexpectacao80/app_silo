import flet as ft
import json
import os
from datetime import datetime
import pandas as pd

DADOS_FILE = "movimentacoes.json"
USUARIOS_FILE = "usuarios.json"

# Verifica se os arquivos existem, senão cria vazios
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

def adicionar_movimentacao(e, page, material, tipo, quantidade, data, lote, tabela, dados_movimentacoes):
    if not material.value or not tipo.value or not quantidade.value or not lote.value:
        page.snack_bar = ft.SnackBar(ft.Text("Todos os campos são obrigatórios!"), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return

    nova_movimentacao = [material.value, tipo.value, int(quantidade.value), data.value, "", lote.value, "Pendente", "", ""]
    dados_movimentacoes.append(nova_movimentacao)
    salvar_dados(dados_movimentacoes)
    atualizar_tabela(page, tabela, dados_movimentacoes)

def abrir_popup_pagador(e, page, index, tabela, dados_movimentacoes):
    def confirmar_pagador(e):
        usuarios = carregar_usuarios()
        pagador = campo_pagador.value
        senha_pagador = campo_senha_pagador.value

        if pagador in usuarios and usuarios[pagador] == senha_pagador:
            dados_movimentacoes[index][6] = "Pendente de Assinatura"
            dados_movimentacoes[index][7] = pagador
            salvar_dados(dados_movimentacoes)
            atualizar_tabela(page, tabela, dados_movimentacoes)
            page.dialog.open = False
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário ou senha incorretos!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    campo_pagador = ft.TextField(label="Usuário (Quem paga)")
    campo_senha_pagador = ft.TextField(label="Senha", password=True)

    popup = ft.AlertDialog(
        title=ft.Text("Autenticação do Pagador"),
        content=ft.Column([campo_pagador, campo_senha_pagador]),
        actions=[ft.TextButton("Confirmar", on_click=confirmar_pagador)]
    )
    page.dialog = popup
    popup.open = True
    page.update()

def abrir_popup_recebedor(e, page, index, tabela, dados_movimentacoes):
    def confirmar_recebedor(e):
        usuarios = carregar_usuarios()
        recebedor = campo_recebedor.value
        senha_recebedor = campo_senha_recebedor.value

        if recebedor in usuarios and usuarios[recebedor] == senha_recebedor:
            dados_movimentacoes[index][6] = "Pago"
            dados_movimentacoes[index][8] = recebedor
            salvar_dados(dados_movimentacoes)
            atualizar_tabela(page, tabela, dados_movimentacoes)
            page.dialog.open = False
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário ou senha incorretos!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    campo_recebedor = ft.TextField(label="Usuário (Quem recebe)")
    campo_senha_recebedor = ft.TextField(label="Senha", password=True)

    popup = ft.AlertDialog(
        title=ft.Text("Autenticação do Recebedor"),
        content=ft.Column([campo_recebedor, campo_senha_recebedor]),
        actions=[ft.TextButton("Confirmar", on_click=confirmar_recebedor)]
    )
    page.dialog = popup
    popup.open = True
    page.update()

def atualizar_tabela(page, tabela, dados_movimentacoes, lote_filter=""):
    tabela.rows.clear()
    for index, mov in enumerate(dados_movimentacoes):
        # Se lote_filter for especificado, filtra as movimentações pelo lote
        if lote_filter and lote_filter.lower() not in mov[5].lower():
            continue
        status = ft.Text(mov[6], color="green" if mov[6] in ["Pago"] else "red")
        recebedor = ft.Text(mov[8] if mov[8] else "Ainda não recebido")
        tabela.rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(mov[0])),
            ft.DataCell(ft.Text(mov[1])),
            ft.DataCell(ft.Text(str(mov[2]))),
            ft.DataCell(ft.Text(mov[3])),
            ft.DataCell(ft.Text(mov[5])),
            ft.DataCell(status),
            ft.DataCell(ft.IconButton(ft.icons.CHECK, on_click=lambda e, idx=index: abrir_popup_pagador(e, page, idx, tabela, dados_movimentacoes))),
            ft.DataCell(ft.IconButton(ft.icons.CHECK, on_click=lambda e, idx=index: abrir_popup_recebedor(e, page, idx, tabela, dados_movimentacoes))),
            ft.DataCell(recebedor)
        ]))
    page.update()

def carregar_usuarios():
    with open(USUARIOS_FILE, "r") as f:
        return json.load(f)

def criar_novo_usuario(e, page):
    # Função para criar um novo usuário
    def confirmar_criacao_usuario(e):
        usuario = campo_usuario.value
        senha = campo_senha.value

        if usuario and senha:
            usuarios = carregar_usuarios()
            if usuario not in usuarios:
                usuarios[usuario] = senha
                with open(USUARIOS_FILE, "w") as f:
                    json.dump(usuarios, f, indent=4)
                page.snack_bar = ft.SnackBar(ft.Text(f"Usuário {usuario} criado com sucesso!"), bgcolor="green")
                page.snack_bar.open = True
                page.update()
                page.dialog.open = False
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Usuário {usuario} já existe!"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, preencha todos os campos!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # Campos para o formulário de criação de usuário
    campo_usuario = ft.TextField(label="Novo Usuário")
    campo_senha = ft.TextField(label="Senha", password=True)

    # Pop-up para confirmação da criação do usuário
    popup = ft.AlertDialog(
        title=ft.Text("Criar Novo Usuário"),
        content=ft.Column([campo_usuario, campo_senha]),
        actions=[ft.TextButton("Confirmar", on_click=confirmar_criacao_usuario)]
    )
    page.dialog = popup
    popup.open = True
    page.update()

def pagina_principal(page: ft.Page):
    page.clean()
    page.title = "Controle de Pagamentos"
    page.window_width = 900
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO
    
    dados_movimentacoes = carregar_dados()

    campo_material = ft.TextField(label="Material", width=200)
    dropdown_tipo = ft.Dropdown(label="Tipo", options=[ft.dropdown.Option("Solicitação"), ft.dropdown.Option("Entrada")], width=200)
    campo_quantidade = ft.TextField(label="Quantidade", width=150, keyboard_type="number")
    campo_data = ft.TextField(label="Data", width=150, value=datetime.now().strftime('%d/%m/%Y'))
    campo_lote = ft.TextField(label="Lote", width=150)
    campo_pesquisa_lote = ft.TextField(label="Pesquisar por Lote", width=150)

    tabela = ft.DataTable(columns=[  
        ft.DataColumn(ft.Text("Material")),
        ft.DataColumn(ft.Text("Tipo")),
        ft.DataColumn(ft.Text("Quantidade")),
        ft.DataColumn(ft.Text("Data")),
        ft.DataColumn(ft.Text("Lote")),
        ft.DataColumn(ft.Text("Status")),
        ft.DataColumn(ft.Text("Ação de Pagamento")),
        ft.DataColumn(ft.Text("Ação de Recebimento")),
        ft.DataColumn(ft.Text("Recebido por"))
    ])
    
    botao_adicionar = ft.ElevatedButton(text="Adicionar", on_click=lambda e: adicionar_movimentacao(e, page, campo_material, dropdown_tipo, campo_quantidade, campo_data, campo_lote, tabela, dados_movimentacoes))
    botao_exportar = ft.ElevatedButton(text="Exportar para Excel", on_click=lambda e: exportar_para_excel(dados_movimentacoes))
    botao_criar_usuario = ft.ElevatedButton(text="Criar Novo Usuário", on_click=lambda e: criar_novo_usuario(e, page))  # Novo botão
    
    # Função de pesquisa por lote
    def pesquisar_lote(e):
        lote_filter = campo_pesquisa_lote.value
        atualizar_tabela(page, tabela, dados_movimentacoes, lote_filter)

    campo_pesquisa_lote.on_change = pesquisar_lote

    page.add(
        ft.Column([
            ft.Text("Controle de Pagamentos", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([campo_material, dropdown_tipo, campo_quantidade]),
            ft.Row([campo_data, campo_lote]),
            ft.Row([campo_pesquisa_lote, botao_adicionar, botao_exportar, botao_criar_usuario]),  # Adicionando o botão de criar usuário
            ft.Text("Movimentações", size=20, weight=ft.FontWeight.BOLD),
            tabela
        ])
    )
    atualizar_tabela(page, tabela, dados_movimentacoes)

def main(page: ft.Page):
    pagina_principal(page)

ft.app(target=main)
