from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from backend import gerar_questoes 

app = FastAPI(
    title="EduQuest API",
    description="API para gerar avaliações educacionais com IA.",
    version="1.1.0"
)

class PedidoAvaliacao(BaseModel):
    tema: str
    curso: str
    dificuldade: str
    tipo_questao: str
    num_questoes: int
    contexto: Optional[str] = ""

@app.post("/gerar-avaliacao/")
def criar_avaliacao(pedido: PedidoAvaliacao):
    print(f"API recebeu pedido. Tema preenchido? {'Sim' if pedido.tema else 'Não'} | Ficheiro anexado? {'Sim' if pedido.contexto else 'Não'}")

    resultado_gerado = gerar_questoes(
        tema=pedido.tema,
        curso=pedido.curso,
        dificuldade=pedido.dificuldade,
        tipo_questao=pedido.tipo_questao,
        num_questoes=pedido.num_questoes,
        contexto=pedido.contexto
    )

    return {"avaliacao_gerada": resultado_gerado}

@app.get("/")
def ler_raiz():
    return {"mensagem": "Bem-vindo à API do EduQuest!"}