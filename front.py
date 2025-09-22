import streamlit as st
import requests # Importamos a biblioteca para fazer requisições HTTP
import json     # Importamos para formatar os dados para a API

# --- FUNÇÃO PARA CARREGAR O CSS EXTERNO ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS '{file_name}' não encontrado. Certifique-se que ele está na mesma pasta.")

# --- APLICA O CSS ---
load_css('style.css')


# --- INTERFACE PRINCIPAL ---
st.title('Bem vindo ao EduQuest!')
st.write('Inteligência Artificial que lhe ajudará você a criar as suas avaliações!!')

# --- Barra Lateral (Sidebar) com as configurações ---
st.sidebar.title("Configurações da Avaliação")
curso_selecionado = st.sidebar.text_input ('Digite o nome do curso:')
dificuldade_selecionada = st.sidebar.selectbox(
    'Selecione o nível de dificuldade:',
    ('Fácil', 'Médio', 'Difícil'),
)
tipo_questao_selecionado = st.sidebar.selectbox(
    'Selecione o tipo de questão:',
    ('Múltipla escolha', 'Verdadeiro ou falso', 'Dissertativa'),
)

st.sidebar.markdown('---')
st.sidebar.write('Desenvolvedor: \n\n [Matheus Marques](https://github.com/MqtheusBM)')


# --- Inputs principais para o conteúdo e quantidade ---
tema_avaliacao = st.text_area('Qual é o tema principal ou os tópicos que devem ser abordados na avaliação?')
col1, col2 = st.columns([2, 2])
with col1:
    num_questoes = st.number_input('Digite a quantidade de questões:', min_value=1, max_value=50, value=5)
with col2:
    uploaded_file = st.file_uploader("Ou anexe um arquivo de referência (PDF, PPTX, DOCX).", type=['pdf', 'pptx', 'docx'])


# --- Botão para gerar a avaliação (MODIFICADO PARA USAR A API) ---
st.markdown("---")
if st.button('Gerar Avaliação'):
    if tema_avaliacao:
        # 1. URL da nossa API FastAPI
        api_url = "http://127.0.0.1:8000/gerar-avaliacao/"

        # 2. Dados que vamos enviar para a API (no formato do Pydantic model)
        dados_para_api = {
            "tema": tema_avaliacao,
            "curso": curso_selecionado,
            "dificuldade": dificuldade_selecionada,
            "tipo_questao": tipo_questao_selecionado,
            "num_questoes": num_questoes,
        }

        # Exibe uma mensagem de carregamento
        with st.spinner('Aguarde...estamos a criar a sua avaliação!'):
            try:
                # 3. Faz a requisição POST para a API
                response = requests.post(api_url, data=json.dumps(dados_para_api))

                # 4. Verifica se a requisição foi bem-sucedida
                if response.status_code == 200:
                    resultado = response.json()
                    st.markdown(resultado['avaliacao_gerada'])
                else:
                    st.error(f"Erro ao contactar a API. Código de status: {response.status_code}")
                    st.error(f"Detalhes: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Verifique se o servidor FastAPI (uvicorn) está em execução.")

    else:
        st.error("Por favor, descreva o tema ou os tópicos da avaliação antes de gerar.")


# --- Aviso de Isenção de Responsabilidade no final da página ---
st.write("O EduQuest pode cometer erros. Por isso, cheque as respostas.")