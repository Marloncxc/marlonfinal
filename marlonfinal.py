import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
import base64


# Função para converter um arquivo em base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Função para definir o fundo da página com uma imagem
def add_bg_image(image_path):
    bin_str = get_base64(image_path)
    bg_image = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: 500px 400px;
        background-repeat: no-repeat;
        background-position: top right;
        height: 100vh;
    }}
    </style>
    """
    st.markdown(bg_image, unsafe_allow_html=True)

# Caminho da imagem de fundo
add_bg_image("C:/aula_python/2023-07-06.jpg")

st.title('CASA DA RAÇÃO')

# Arquivo CSV
csv_file = 'estoque.csv'
movimento_file = 'movimentacao.csv'

# Criar DataFrame com CSV
if os.path.exists(csv_file):
    estoque = pd.read_csv(csv_file)
else:
    estoque = pd.DataFrame(columns=['Categoria', 'Produto', 'Quantidade', 'Valor'])

if os.path.exists(movimento_file):
    movimentacao = pd.read_csv(movimento_file)
else:
    movimentacao = pd.DataFrame(columns=['Data', 'Tipo', 'Produto', 'Quantidade'])

# Sidebar: Cadastro de Produto
st.sidebar.header('CADASTRAR PRODUTO')

FORMULARIO = st.sidebar.form('Formulario', clear_on_submit=True)
nova_categoria = FORMULARIO.text_input('CATEGORIA')
novo_produto = FORMULARIO.text_input('PRODUTO')
nova_quantidade = FORMULARIO.number_input('QUANTIDADE', min_value=0, step=1)
novo_valor = FORMULARIO.number_input('VALOR', min_value=0.0, format="%.2f")

bt1 = FORMULARIO.form_submit_button('Cadastrar Produto')

if bt1:
    novo = {
        'Categoria': [nova_categoria],
        'Produto': [novo_produto],
        'Quantidade': [nova_quantidade],
        'Valor': [novo_valor]
    }
    x = pd.DataFrame(novo)
    estoque = pd.concat([estoque, x], ignore_index=True)
    estoque.to_csv(csv_file, index=False)

    nova_movimentacao = {
        'Data': [datetime.now().strftime('%Y-%m-%d')],
        'Tipo': ['Entrada'],
        'Produto': [novo_produto],
        'Quantidade': [nova_quantidade]
    }
    movimento_df = pd.DataFrame(nova_movimentacao)
    movimentacao = pd.concat([movimentacao, movimento_df], ignore_index=True)
    movimentacao.to_csv(movimento_file, index=False)

    st.success('Produto cadastrado com sucesso!')
    st.dataframe(estoque)

# Sidebar: Saída de Produtos
st.sidebar.header('SAÍDA DE PRODUTOS')

FORMULARIO_SAIDA = st.sidebar.form('Formulario_saida', clear_on_submit=True)
produto_saida = FORMULARIO_SAIDA.selectbox('SELECIONE O PRODUTO', estoque['Produto'].unique())
quantidade_saida = FORMULARIO_SAIDA.number_input('QUANTIDADE DE SAÍDA', min_value=0, step=1)

bt2 = FORMULARIO_SAIDA.form_submit_button('Registrar Saída')

if bt2:
    if quantidade_saida > 0:
        produto_atual = estoque[estoque['Produto'] == produto_saida].iloc[0]
        if produto_atual['Quantidade'] >= quantidade_saida:
            estoque.loc[estoque['Produto'] == produto_saida, 'Quantidade'] -= quantidade_saida
            estoque.to_csv(csv_file, index=False)

            nova_movimentacao_saida = {
                'Data': [datetime.now().strftime('%Y-%m-%d')],
                'Tipo': ['Saída'],
                'Produto': [produto_saida],
                'Quantidade': [quantidade_saida]
            }
            movimento_saida_df = pd.DataFrame(nova_movimentacao_saida)
            movimentacao = pd.concat([movimentacao, movimento_saida_df], ignore_index=True)
            movimentacao.to_csv(movimento_file, index=False)

            st.success(f'Saída registrada: {quantidade_saida} de {produto_saida}.')
        else:
            st.error('Quantidade em estoque insuficiente.')
    else:
        st.warning('Digite uma quantidade válida.')

# Seletor de Estatísticas e Gráficos
st.sidebar.header('VISUALIZAÇÕES')

opcao = st.sidebar.selectbox(
    'Escolha o que deseja visualizar',
    ['Estoque Total', 'Estoque Detalhado', 'Gráfico de Quantidade por Produto']
)

if opcao == 'Estoque Total':
    st.header('Estoque Total')
    st.write(f'Total de produtos cadastrados: {len(estoque)}')
    st.write(f'Quantidade total em estoque: {estoque["Quantidade"].sum()}')
    st.write(f'Valor total do estoque: R$ {(estoque["Valor"] * estoque["Quantidade"]).sum():.2f}')

elif opcao == 'Estoque Detalhado':
    produto_stats = estoque.groupby('Produto').agg(
        Quantidade_Itens=('Quantidade', 'sum'),
        Valor_Unitário=('Valor', 'mean'),
        Valor_Total=('Valor', lambda x: (x * estoque.loc[x.index, 'Quantidade']).sum())
    ).reset_index()
    st.header('Estoque Detalhado')
    st.dataframe(produto_stats)

elif opcao == 'Gráfico de Quantidade por Produto':
    produto_counts = estoque.groupby('Produto')['Quantidade'].sum()
    plt.figure(figsize=(7, 5))
    produto_counts.plot(kind='bar', color='skyblue')
    plt.title('Quantidade por Produto')
    plt.xlabel('Produto')
    plt.ylabel('Quantidade')
    plt.xticks(rotation=45)
    st.pyplot(plt)
    plt.clf()

# Relatório Diário
st.sidebar.header('RELATÓRIO DIÁRIO')

data_relatorio = st.sidebar.date_input('Selecione uma data', datetime.now())

if st.sidebar.button('Gerar Relatório'):
    relatorio_diario = movimentacao[movimentacao['Data'] == data_relatorio.strftime('%Y-%m-%d')]
    if not relatorio_diario.empty:
        st.subheader(f'Relatório de Movimentação para {data_relatorio.strftime("%d/%m/%Y")}')
        st.dataframe(relatorio_diario)
    else:
        st.warning('Não há movimentações para esta data.')