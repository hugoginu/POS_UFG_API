# POS_UFG_API
Repositório criado para armazenar as atividades desenvolvidas na disciplina de API da Pós em Agentes Inteligentes da UFG.


## Orientações para executar a API

Sugestão de versão do python: 3.10 ou superior

- Crie um ambiente virtual: `python -m venv venv`
- Ative o ambiente virtual (no Windows): `venv\Scripts\activate`
- Ative o ambiente virtual (no Linux): `source venv/bin/activate`
- Instale as bibliotecas: `pip install -r requirements.txt`
- Copie o arquivo `.env.sample` para `.env` e preencha as variáveis de ambiente
- Executar a API em ambiente de desenvolvimento: `fastapi dev main.py`
- Executar a API em ambiente de produção: `fastapi run main.py`

Para teste da solução use os seguintes exemplos:

api_token: 1234567890
chaveNFe: 31240161365557000110550010009047751102632318

v1/vinculacao/Request body:

{
  "chv_nfe": "31240161365557000110550010009047751102632318",
  "itens_efd": [
    {
      "seq": 1,
      "cod_item": "000001",
      "desc_item": "MANTEIGA AVIAÇÃO TABL.S/S C/12",
      "qt_item": 24,
      "valor_un": 150.00,
      "valor_total": 3600.0
    },
	{
      "seq": 2,
      "cod_item": "000002",
      "desc_item": "MANTEIGA AVIAÇÃO TABL.S/S C/24",
      "qt_item": 114,
      "valor_un": 292.95,
      "valor_total": 7030.8
    }
  ],
  "itens_xml": [
    {
      "seq": 1,
      "cod_item": "000001",
      "desc_item": "MANTEIGA AVIAÇÃO TABLETE C/24",
      "qt_item": 114,
      "valor_un": 292.95,
      "valor_total": 7030.8
    },
    {
      "seq": 2,
      "cod_item": "000001",
      "desc_item": "MANTEIGA AVIAÇÃO TABLETE C/12",
      "qt_item": 24,
      "valor_un": 150.00,
      "valor_total": 3600.0
    }
  ]
}
