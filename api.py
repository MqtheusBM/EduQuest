from fastapi import FastAPI
from pydantic import BaseModel
from backend import gerar_questoes # Importamos nossa lógica já existente

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="EduQuest API",
    description="API para gerar avaliações educacionais com IA.",
    version="1.0.0"
)

# Define um "modelo" de dados para a requisição que vamos receber
# Isso garante que os dados que chegam na API estão no formato correto
class PedidoAvaliacao(BaseModel):
    tema: str
    curso: str
    dificuldade: str
    tipo_questao: str
    num_questoes: int

# Define o nosso primeiro "endpoint" (o URL que o frontend vai chamar)
# @app.post significa que este endpoint aceita requisições do tipo POST
@app.post("/gerar-avaliacao/")
def criar_avaliacao(pedido: PedidoAvaliacao):
    """
    Recebe os detalhes de uma avaliação e retorna as questões geradas.
    """
    print(f"API recebeu um pedido para o tema: {pedido.tema}")

    # Usa a função que já tínhamos no backend.py para fazer o trabalho
    resultado_gerado = gerar_questoes(
        tema=pedido.tema,
        curso=pedido.curso,
        dificuldade=pedido.dificuldade,
        tipo_questao=pedido.tipo_questao,
        num_questoes=pedido.num_questoes
    )

    # Retorna o resultado como uma resposta JSON
    return {"avaliacao_gerada": resultado_gerado}

# Endpoint raiz para um teste rápido
@app.get("/")
def ler_raiz():
    return {"mensagem": "Bem-vindo à API do EduQuest!"}