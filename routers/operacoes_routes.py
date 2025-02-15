from fastapi import APIRouter
from utils import obter_logger_e_configuracao, xml_to_json, getXmlNFe
from models import NomeGrupo


logger = obter_logger_e_configuracao()

router = APIRouter()

# Metódo da API para consulta dos dados da NFe 
@router.get("/v1/nfe",
            summary="Consulta dados completo da NFe",
            tags=[NomeGrupo.consultas])
def consultaNfe(chaveNFe: str):
    logger.info('chaveNFe->' + chaveNFe)
    # Faz a requisição POST com body vazio
    response =  getXmlNFe(chaveNFe)

    # Verifica se a resposta é bem-sucedida
    if response and response.strip:
        return xml_to_json(response)
    else:
        return {"resultado": response.status_code}