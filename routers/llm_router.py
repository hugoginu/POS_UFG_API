from fastapi import APIRouter
from utils import obter_logger_e_configuracao, getXmlNFe, formatar_itens, extrair_json
from models import Vinculacao, VinculacaoReq, VinculacaoRet
from langchain_community.chat_models import ChatOpenAI
import json

logger = obter_logger_e_configuracao()

MODEL_GPT = "gpt-4o-mini"
CABECALHO = """Seq|Código do Item|Descrição|Quantidade|Valor UN|Valor Total"""
PROMPT_VINCULACAO = """
	Realize a vinculação dos itens da lista 01: <dadosEfd>[itens_efd]</dadosEfd> 
    com os da lista 02: <dadosXml>[itens_xml]</dadosXml>. 
    As informações na lista 01 e 02 estão separadas por pipe |, sendo a primeira linha o cabeçalho descritivo do que é cada informação.
    Para vinculação considere as seguintes regras: 
    <regra 01>
        Faça a vinculação pela similaridade considerando apenas o campo 'Descrição' da lista 01 com a lista 02.
        Não pode existir outra ocorrência com a mesma similaridade.
    </regra 01>
    <regra 02>
        Faça a vinculação pela aproximação do 'Valor Total', considerando o percentual da diferença entre o valor da lista 01 com o valor da lista 02.
        Para calcular o percentual, siga as instruções do <exemplo>
        <exemplo>Subtraia o valor total do item 2 do valor total do item 1 (100 - 99), desconsidere o sinal de negativo, 
        e divida o resultado pelo valor total do item 1 (1 / 100 = 0,01) e multiplique por 100 (0,01 x 100 = 1). 
        </exemplo>
        Se resultado for menor que 2 (2%) faça a vincuação, desde que não tenha outro item com uma aproximação menor ou igual.
    </regra 02>
    <regra 03>
        Passo 1: Verifique se a lista 01 possui a mesma quantidade de itens da lista 02. Caso as listas tenham quantidade diferentes,
        selecione a lista que possui mais itens e faça o seguinte:
            - Para fins de calculo na etapa 2, some o valor total dos itens que possuirem a mesma descrição, e considere esse valor para o passo 2,
            por exemplo, o item 01 possui um valor de 100 e o item 02 um valor de 50, para o passo 2, considere para esses dois itens o valor de 150. 
       Passo 2: Aplique a regra 02 desconsideração a margem de aproximação de 5%, vinculando os itens pelo valor mais aproximado. Para desempate aplique a regra 01.     
    </regra 03>
    Para realizar a vinculação execute as seguintes etapas:
    <etapa 1>
        Para cada item da lista 01 aplique a regra 01 para todos os itens da lista 02 que ainda não tenham sido vinculados.
        Ao realizar a vinculação, retire da lista 01 e da lista 02 o item que vinculado.
        Caso a lista 01 ou lista 02 tenha apenas um item sem resolução, realize a vinculação desses itens e considere como resolução a Regra 00.
    </etapa 1>
    <etapa 2>
        Para cada item da lista 01 que não tenha sido resolvido na regra 01, aplique a regra 02 para todos os itens da lista 02 que ainda não tenham sido vinculados.
        Ao realizar a vinculação, retire da lista 01 e da lista 02 o item que foi vinculado.
        Caso a lista 01 ou lista 02 tenha apenas um item resolução, realize a vinculação desses itens e considere como resolução a Regra 00.
    </etapa 2>
    <etapa 3>
        Para cada item da lista 01 que não tenha sido resolvido nas etapas anteriores, aplique a regra 03 para todos os itens da lista 02 que ainda não tenham sido vinculados.
        Ao realizar a vinculação, retire da lista 01 e da lista 02 o item que vinculado.
        Caso a lista 01 ou lista 02 tenha apenas um item resolução, realize a vinculação desses itens e considere como resolução a Regra 00.
    </etapa 3>
    <etapa 4>
        Execute a etapa 3 até que todos os itens da lista 1 e da lista 2 tenham vinculação. 
    </etapa 4>

    Finalizada as vinculações, gere a resposta em JSON com os atributos conforme exemplo
    <exemplo>
        {
            "vinculacao": [
                {
                    "lista_01_seq": 1,
                    "lista_02_seq": 2,
                    "regra_vinculo": "Regra 01"
                },
                {
                    "lista_01_seq": 2,
                    "lista_02_seq": 1,
                    "regra_vinculo": "Regra 00"
                }
            ]
        }
    </exemplo>
    A resposta deve contar apenas o JSON  e nada mais.
"""

router = APIRouter()

@router.get("/v1/nfe/itens", 
             summary="Extrai os Itens da NFe no formato do SPED")
def getItesNFe(chaveNFe: str):
    """
    Extrai informações dos itens de uma Nota Fiscal Eletrônica (NF-e) a partir de seu XML.
    Parâmetros:
    chaveNFe (str): A chave de acesso da NF-e.
    Retorna:
    str: Uma lista de dicionários contendo as informações dos itens da NF-e no formato:
         Seq|Código|Descrição|Quantidade|Valor UN|Valor Total
    O formato do XML deve seguir o esquema da NF-e, onde os itens estão dentro da tag <det>.
    """
    logger.info('chv_nfe -> ' + chaveNFe)

    xml = getXmlNFe(chaveNFe)

    prompt = """
        Com base arquivo XML contendo uma Nota Fiscal Eletrônica (NF-e) delimitado pelo marcador <arquivo_xml>. 
        Sua tarefa é extrair as informações de cada item da NF-e e retornar uma lista de dicionários com os seguintes campos:
            Seq (nItem)
            Código (cProd)
            Descrição (xProd)
            Quantidade (qCom)
            Valor UN (vUnCom)
            Valor Total (vProd)
        O XML segue o esquema da NF-e e os itens estão dentro da tag <det>. 
        Utilize parsing XML para encontrar os valores corretos. 
        Certifique-se de ignorar namespaces, se houver, e validar se os campos extraídos estão presentes no XML.
        Retorne a saída no seguinte formato: Seq|Código|Descrição|Quantidade|Valor UN|Valor Total        
        A saída deve ser somente as informações extraídas <arquivo_xml> informado e nada mais. 
        Não quero código de exemplo, quero as informações extraídas e somente isso.
        <arquivo_xml>
    """ + xml + "</arquivo_xml>"
    
    # Configurar o model

    llm = ChatOpenAI(temperature=0, model=str(MODEL_GPT))

	# Enviar o prompt diretamente para o modelo
    resposta = llm.predict(prompt)
    resposta = resposta.replace('```plaintext', '')
    resposta = resposta.replace('```', '')
    logger.info('resposta ->' + resposta)

    return resposta

@router.post("/v1/vinculacao", 
             response_model=VinculacaoRet,
             summary="Vincula Itens da Nota Fiscal do SPED com os itens do XML da NFe")
def analisar_vinculacao(req: VinculacaoReq):
    """
    Analisa a vinculação de itens entre EFD e XML de uma NFe.
    Args:
        req (VinculacaoReq): Objeto contendo a chave da NFe e os itens do EFD.
    Returns:
        VinculacaoRet: Objeto contendo a chave da NFe e os itens vinculados.
    Processamento:
        1. Loga a chave da NFe.
        2. Formata os itens do EFD e obtém os itens do XML da NFe.
        3. Substitui os placeholders no prompt com os itens do EFD e XML.
        4. Configura e envia o prompt para o modelo de linguagem.
        5. Extrai a resposta do modelo e converte para JSON.
        6. Mapeia os dados JSON para objetos de vinculação.
        7. Retorna um objeto contendo a chave da NFe e os itens vinculados.
    """
    logger.info('chv_nfe -> ' + req.chv_nfe)
    itens_efd = CABECALHO + '\n' + formatar_itens(req.itens_efd)
    itens_xml = CABECALHO + getItesNFe(req.chv_nfe)
    logger.info('itens_efd -> ' + itens_efd)

    prompt = PROMPT_VINCULACAO
    prompt = prompt.replace('[itens_efd]', itens_efd)
    prompt = prompt.replace('[itens_xml]', itens_xml)
    
    # Configurar o modelo (você pode trocar 'gpt-4' se tiver acesso)
    llm = ChatOpenAI(temperature=0, model=str(MODEL_GPT))

	# Enviar o prompt diretamente para o modelo
    resposta = llm.predict(prompt)

    json_str = extrair_json(resposta)
    
    dados = json.loads(json_str)  # Converte para dicionário
    itens_vinculados = [Vinculacao(**item) for item in dados["vinculacao"]]  # Mapeia para objetos

    ret = VinculacaoRet
    ret.chv_nfe = req.chv_nfe
    ret.itens_vinculados = itens_vinculados

    return ret

# Prompt de vinculação dos itens
