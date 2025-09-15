import streamlit as st

st.title('Bem vindo ao EduQuest!')
st.write('Inteligência Artificial que lhe ajudará você a criar as suas avaliações!!')

# Cria duas colunas: uma para a caixa de texto e outra para o botão de upload
col1, col2 = st.columns([4, 1])

with col1:
    pergunta = st.text_input('Digite quantidade de questões:')

# Exibe a pergunta enviada
if pergunta:
    st.write(f'Você perguntou: {pergunta}')

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'Selecione o curso:',
    ('Medicina', 'Engenharia', 'Direito', 'Administração', 'Pedagogia'),
)

add_selectbox = st.sidebar.selectbox(
    'Selecione o nível de dificuldade:',
    ('Fácil', 'Médio', 'Difícil'),
)

add_selectbox = st.sidebar.selectbox(
    'Selecione o tipo de questão:',
    ('Múltipla escolha', 'Verdadeiro ou falso', 'Dissertativa'),
)

st.sidebar.markdown('---')
st.sidebar.write('Desenvolvido pelo aluno [Matheus Marques](https://github.com/MqtheusBM)')