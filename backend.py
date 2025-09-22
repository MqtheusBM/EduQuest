import os
from dotenv import load_dotenv
from groq import Groq
import re

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# Pega a chave de API da Groq do ambiente
groq_api_key = os.getenv("GROQ_API_KEY")

# Inicializa o cliente da Groq
try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    print(f"Erro ao inicializar o cliente Groq: {e}")
    client = None

def formatar_alternativas(texto, tipo_questao):
    if tipo_questao.lower() == "múltipla escolha":
        # Garante que cada alternativa (a), b), c), etc.) fique em uma nova linha
        texto = re.sub(r'(?<!\n)([a-h]\))', r'\n\1', texto)
        # Remove linhas em branco duplicadas
        texto = re.sub(r'\n{3,}', r'\n\n', texto)
    return texto

def gerar_questoes(tema, curso, dificuldade, tipo_questao, num_questoes, arquivo_anexado=None):
    """
    Função principal do backend que chama a API do Llama 3 para gerar questões.
    """
    if not client:
        return "ERRO: O cliente da API da Groq não foi inicializado corretamente. Verifique sua chave de API no ficheiro .env."

    # --- Lógica para escolher o exemplo de formatação correto ---
    exemplo_formatacao = ""
    if tipo_questao == "Múltipla escolha":
        exemplo_formatacao = """
    **FORMATO OBRIGATÓRIO (Múltipla Escolha):**
    Siga esta estrutura EXATAMENTE. CADA PARTE DEVE ESTAR EM UMA NOVA LINHA.

    **1. [TÍTULO DA PERGUNTA EM NEGRITO]**
    a) [Texto da alternativa A]
    b) [Texto da alternativa B]
    c) [Texto da alternativa C]
    d) [Texto da alternativa D]

    **NUNCA coloque as alternativas na mesma linha que a pergunta ou umas com as outras.**
    """
    elif tipo_questao == "Verdadeiro ou falso":
        exemplo_formatacao = """
    **FORMATO OBRIGATÓRIO (Verdadeiro ou Falso):**
    Siga esta estrutura EXATAMENTE. CADA PARTE DEVE ESTAR EM UMA NOVA LINHA.

    **1. [AFIRMAÇÃO EM NEGRITO]**
    ( ) Verdadeiro
    ( ) Falso

    **NUNCA coloque "( ) Verdadeiro ( ) Falso" na mesma linha que a pergunta.**
    """
    elif tipo_questao == "Dissertativa":
        exemplo_formatacao = """
    **FORMATO OBRIGATÓRIO (Dissertativa):**
    Siga esta estrutura EXATAMENTE.

    **1. [PERGUNTA DISSERTATIVA EM NEGRITO]**
    """

    # --- Construção Final do Prompt ---
    prompt = f"""
    Aja como um gerador de avaliações que segue regras de formatação de forma PERFEITA.
    Sua única tarefa é criar {num_questoes} questões sobre o tema "{tema}" para o curso de {curso}.

    **REGRAS INQUEBRÁVEIS:**
    1.  **Dificuldade:** {dificuldade}.
    2.  **Tipo de Questão:** {tipo_questao}.
    3.  **Idioma:** Português do Brasil.
    4.  **INCLUA AS RESPOSTAS APENAS NO FINAL.**
    5.  **A FORMATAÇÃO É A REGRA MAIS IMPORTANTE. SIGA O EXEMPLO ABAIXO SEM NENHUM DESVIO.**
    {exemplo_formatacao}
    """

    print("Enviando prompt para o Llama 3...")

    try:
        # Chama a API da Groq para executar o Llama 3
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            # --- LINHA CORRIGIDA E ATUALIZADA ---
            model="openai/gpt-oss-120b", # Modelo Llama 3 mais recente e estável
            temperature=0.7,
            max_tokens=2048,
        )

        # Extrai e retorna o conteúdo da resposta da IA
        resposta_ia = chat_completion.choices[0].message.content
        resposta_ia = formatar_alternativas(resposta_ia, tipo_questao)
        return resposta_ia

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API da Groq: {e}")
        return f"Desculpe, ocorreu um erro ao tentar gerar as questões. Detalhes: {e}"