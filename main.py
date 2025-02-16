"""
Este módulo configura e inicializa a aplicação FastAPI para o projeto "Trabalho do Grupo 18".
A aplicação inclui:
- Título, resumo, descrição, versão, termos de serviço e informações de licença.
- Dependência de autenticação para todas as rotas.
- Inclusão de dois roteadores: `operacoes_routes` e `llm_router`.
Autores:
- Hugo Ginú
- Pedro Moacir de Carvalho
- Rafael Peixoto
Licença:
- Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.html)
"""

from fastapi import FastAPI, Depends
from utils import autenticacao
from routers import llm_router, operacoes_routes

app = FastAPI(
    title="Trabalho do Grupo 18",
    summary="API desenvolvida para avaliação da disciplina de API do Curso de Pós-Graduação em Sistemas e Agentes Inteligentes da Universidade Federal de Goiás",
    description="Hugo Ginú <br>Pedro Moacir de Carvalho <br>Rafael Peixoto",
    version="1.0.0",
    terms_of_service="https://agentes.inf.ufg.br/",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    dependencies=[Depends(autenticacao)],
)

app.include_router(operacoes_routes.router, prefix="/operacoes")
app.include_router(llm_router.router, prefix="/llm")
