from pydantic import BaseModel, Field
from typing import List
from enum import Enum


# Metódo da API para vinculação dos itens do SPED com os itens do XML
class ItemNotaFiscal(BaseModel):
    """
    Classe que representa um item de nota fiscal.

    Atributos:
        seq (int): Sequencial do item.
        cod_item (str): Código do produto.
        desc_item (str): Descrição do Item.
        qt_item (float): Quantidade.
        valor_un (float): Valor unitário.
        valor_total (float): Valor Total do Item.
    """

    seq: int = Field(description="Sequencial do item")
    cod_item: str = Field(description="Código do produto")
    desc_item: str = Field(description="Descrição do Item")
    qt_item: float = Field(description="Quantidade")
    valor_un: float = Field(description="Valor unitário")
    valor_total: float = Field(description="Valor Total do Item")


class Vinculacao(BaseModel):
    """
    Classe Vinculacao representa a vinculação entre itens de duas listas distintas.

    Atributos:
        lista_01_seq (int): Sequencial do item no EFD.
        lista_02_seq (int): Sequencial do item no XML.
        regra_vinculo (str): Forma como foi vinculado o item da lista 01 com o item da lista 02 (Regra 00 | Regra 01 | Regra 02 | Regra 03).
    """

    lista_01_seq: int = Field(description="Sequencial do item no EFD")
    lista_02_seq: int = Field(description="Sequencial do item no XML")
    regra_vinculo: str = Field(
        description="Forma como foi vinculado o item da lista 01 com o item da lista 02 (Regra 00 | Regra 01 | Regra 02 | Regra 03)"
    )


class VinculacaoReq(BaseModel):
    """
    Classe VinculacaoReq

    Atributos:
        chv_nfe (str): Chave da nota fiscal.
        itens_efd (List[ItemNotaFiscal]): Lista de itens do SPED.
    """

    chv_nfe: str = Field(description="Chave da nota fiscal")
    itens_efd: List[ItemNotaFiscal] = Field(description="Lista de itens do SPED")
    # itens_xml: List[ItemNotaFiscal] = Field(description="Lista de itens da Lista de Itens do XML")


class VinculacaoRet(BaseModel):
    """
    Classe VinculacaoRet

    Atributos:
        chv_nfe (str): Chave da nota fiscal.
        itens_vinculados (List[Vinculacao]): Lista de itens com a vinculação entre SPED e XML.
    """

    chv_nfe: str = Field(description="Chave da nota fiscal")
    itens_vinculados: List[Vinculacao] = Field(
        description="Lista de itens com a vinculação entre SPED e XML"
    )


class NomeGrupo(str, Enum):
    consultas = "Consultas Básicas"
    llm = "Operações com IA"
