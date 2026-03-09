import os
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    print(f"Erro ao inicializar o cliente Groq: {e}")
    client = None

def formatar_alternativas(texto, tipo_questao):
    if tipo_questao.lower() == "múltipla escolha":
        texto = re.sub(r'(?<!\n)([a-h]\))', r'\n\1', texto)
        texto = re.sub(r'\n{3,}', r'\n\n', texto)
    return texto

def gerar_questoes(tema, curso, dificuldade, tipo_questao, num_questoes, contexto):
    if not client:
        return "ERRO: O cliente da API da Groq não foi inicializado corretamente. Verifique sua chave de API no ficheiro .env."
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
    instrucao_documento = ""
    texto_validacao = ""
    texto_geracao = ""
    if contexto.strip():
        instrucao_documento = f"""
        \n\n=========================================
        **MATERIAL DE REFERÊNCIA OBRIGATÓRIO:**
        {contexto}
        =========================================
        """
    if tema.strip() and contexto.strip():
        # CENÁRIO 3: Tem Tema e Ficheiro
        texto_validacao = f'Analise se o tema "{tema}" e o material de referência estão adequados para o curso de "{curso}".'
        texto_geracao = f'Crie {num_questoes} questões ESPECIFICAMENTE sobre o tema "{tema}", baseando-se EXCLUSIVAMENTE no material de referência acima. Se a resposta não estiver no texto, não faça a pergunta.'

    elif contexto.strip():
        # CENARIO 2: Só Ficheiro
        texto_geracao = f'Analise o material de referência fornecido. Verifique se ele  se enquadra de forma geral no curso de "{curso}".'

    else:
        # CENARIO 1: Só Tema
        texto_validacao = f'Crie {num_questoes} questões gerais sobre o tema "{tema}".'

    prompt = f"""
    Sua tarefa é agir como um professor universitário e criar avaliações precisas.

    **PASSO 1: Validação**
    {texto_validacao}
    Se não houver relação nenhuma com o curso, responda APENAS:
    "**ERRO DE VALIDAÇÃO:** O tema ou documento fornecido não parece pertencer ao curso de '{curso}'."

    {instrucao_documento}

    **PASSO 2: Geração de Questões (Apenas se a validação for bem-sucedida)**
    {texto_geracao}
    
    **REGRAS OBRIGATÓRIAS:**
    1. Nível de dificuldade: {dificuldade}.
    2. Tipo de questão: {tipo_questao}.
    3. Siga a formatação abaixo estritamente, sem exceções:
    {exemplo_formatacao}
    4. Fórmulas Matemáticas: Use o formato LaTeX entre duplo cifrão ($$ ... $$).

    **GABARITO:**
    No final, adicione uma seção "--- GABARITO ---" e liste as respostas corretas.
    """

    print("A enviar prompt dinâmico para o LLM...")

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-120b", 
            temperature=0.2,
            max_tokens=2048,
        )
        resposta_ia = chat_completion.choices[0].message.content
        resposta_ia = formatar_alternativas(resposta_ia, tipo_questao)
        return resposta_ia

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API da Groq: {e}")
        return f"Desculpe, ocorreu um erro ao tentar gerar as questões. Detalhes: {e}"