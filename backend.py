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

    1. [TÍTULO DA PERGUNTA EM NEGRITO]**
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

   # --- Construção Final do Prompt com Passo de Validação e Gabarito ---
    prompt = f"""
    Sua primeira e mais importante tarefa é a VALIDAÇÃO. Aja como um especialista universitário.

    **PASSO 1: Validação do Tema vs. Curso**
    Analise o tema "{tema}" e o curso "{curso}" fornecidos.
    - Se o tema pertencer claramente ao curso, prossiga para o PASSO 2.
    - Se o tema NÃO pertencer ao curso, IGNORE O PASSO 2 e responda APENAS com a seguinte mensagem de erro, sugerindo o curso correto:
    "**ERRO DE VALIDAÇÃO:** O tema '{tema}' não parece pertencer ao curso de '{curso}'. Este tema é mais apropriado para o curso de **[Nome do Curso Correto Aqui]**."

    **PASSO 2: Geração de Questões e Gabarito (Apenas se a validação for bem-sucedida)**
    Se o tema for válido para o curso, siga estas regras INQUEBRÁVEIS:

    **REGRAS DE GERAÇÃO:**
    1.  Crie {num_questoes} questões sobre o tema.
    2.  Use a dificuldade: {dificuldade}.
    3.  Use o tipo de questão: {tipo_questao}.
    4.  A formatação é a regra mais importante. Siga o exemplo abaixo sem nenhum desvio:
        {exemplo_formatacao}
    5.  **IMPORTANTE:** Crie TODAS as questões primeiro, sem nenhuma resposta.
    6.  **Fórmulas Matemáticas:** Use SEMPRE o formato LaTeX envolto em símbolos de cifrão duplo ($$ ... $$) para fórmulas e equações, para que fiquem destacadas.
    **REGRA FINAL - GABARITO:**
    Após gerar TODAS as questões, adicione uma secção final chamada "--- GABARITO ---".
    Dentro desta secção, liste o número de cada questão e sua resposta correta.
    - Para Múltipla Escolha, indique a letra (Ex: 1. b)).
    - Para Verdadeiro ou Falso, indique a palavra (Ex: 1. Verdadeiro).
    - Para Dissertativa, forneça uma resposta-modelo curta e objetiva.
    - Use SEMPRE o formato LaTeX envolto em símbolos de cifrão duplo ($$ ... $$) para fórmulas e equações, para que fiquem destacadas.
    - Toda e qualquer expressão matemática DEVE obrigatoriamente estar entre $$ (exemplo: $$x^2$$). NUNCA escreva matemática em texto simples.
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
            temperature=0.2,
            max_tokens=2048,
        )

        # Extrai e retorna o conteúdo da resposta da IA
        resposta_ia = chat_completion.choices[0].message.content
        resposta_ia = formatar_alternativas(resposta_ia, tipo_questao)
        return resposta_ia

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API da Groq: {e}")
        return f"Desculpe, ocorreu um erro ao tentar gerar as questões. Detalhes: {e}"