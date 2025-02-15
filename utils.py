import os
from dotenv import load_dotenv
import openai
import logging
import requests
import xml.etree.ElementTree as ET
import re
from fastapi import status, HTTPException
from typing import List
from models import ItemNotaFiscal

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")
URL_API_MEUDANFE = 'https://ws.meudanfe.com/api/v1/get/nfe/xml/'

def obter_logger_e_configuracao():
    """
    Configura o logger padrão para o nível de informação e formato especificado.

    Retorna:
        logging.Logger: Um objeto de logger com as configurações padrões.
    """
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
    )
    logger = logging.getLogger("fastapi")
    return logger

logger = obter_logger_e_configuracao()

# Reutilização da autenticaçõa para todos os serviços da API
def autenticacao(api_token: str):
    """
    Verifica a autenticidade do token da API.

    Args:
        api_token (str): O token da API a ser verificado.

    Raises:
        HTTPException: Se o token fornecido for inválido, uma exceção HTTP 401 é levantada.

    """
    if api_token != API_TOKEN:
        logger.error('O Token informado ' + api_token + " é inválido!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

# Método para converter uma informação no formato XML para JSON
def xml_to_json(xml_string):
    """
    Converte uma string XML para um dicionário JSON.

    Args:
        xml_string (str): A string contendo o XML a ser convertido.

    Returns:
        dict: Um dicionário representando a estrutura do XML em formato JSON.

    Exemplo:
        xml_string = '<root><child>valor</child></root>'
        json_dict = xml_to_json(xml_string)
        # json_dict será {'root': {'child': 'valor'}}
    """
    root = ET.fromstring(xml_string)    
    def parse_element(element):
        data = {}
        tag = element.tag.split('}')[-1] 
        if element.text and element.text.strip():
            data[tag] = element.text.strip()
        else:
            data[tag] = {child.tag.split('}')[-1]: parse_element(child) for child in element}
        return data[tag]
    return parse_element(root)

# realiza a chamada do serviço de pesquisa da NFe
def getXmlNFe(chaveNFe: str):
    """
    Obtém o XML da NFe a partir de uma chave de acesso.

    Args:
        chaveNFe (str): A chave de acesso da NFe.

    Returns:
        str: O conteúdo do XML da NFe se a resposta for bem-sucedida.
        int: O código de status HTTP se a resposta não for bem-sucedida.
    """
    response = requests.post(URL_API_MEUDANFE + chaveNFe, data={'empty'})
    # Verifica se a resposta é bem-sucedida
    if response.status_code == status.HTTP_200_OK or (response.text and response.text.strip):
        return response.text
    else:
        return 'ERROR_CODE: ' + str(response.status_code)
    
# Formata as informações para o prompt
def formatar_itens(itens: List[ItemNotaFiscal]) -> str:
    """
    Formata uma lista de itens de nota fiscal em uma string.

    Cada item é formatado em uma linha separada, com os campos separados por '|'.
    Os campos de cada item são: seq, cod_item, desc_item, qt_item, valor_un, valor_total.

    Args:
        itens (List[ItemNotaFiscal]): Lista de itens de nota fiscal a serem formatados.

    Returns:
        str: String formatada contendo todos os itens da lista.
    """
    return "\n".join(f"{item.seq}|{item.cod_item}|{item.desc_item}|{item.qt_item}|{item.valor_un}|{item.valor_total}" for item in itens)

# Remover textos retornados pela LLM fora do JSON
def extrair_json(texto: str) -> str:
    """
    Extrai um objeto JSON de uma string de texto.

    Args:
        texto (str): A string de texto que contém o objeto JSON.

    Returns:
        str: O objeto JSON extraído como uma string. Retorna uma string vazia se nenhum objeto JSON for encontrado.
    """
    match = re.search(r'\{.*\}', texto, re.DOTALL)  # Captura tudo entre { e }
    return match.group(0) if match else ""  # Retorna apenas o conteúdo encontrado