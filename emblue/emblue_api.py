


import requests
import json
from mvx.mvx_classes import *
from shared.codigo_pais import encontrar_pais

class EmblueApi:

    def __init__(self, token_auth, login_user, login_psw):
        self.token_auth = token_auth
        self.token = ''
        self.login_user = login_user
        self.login_psw = login_psw
        pass

    def http_post(self, url, content):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=utf-8',
        }
        response = requests.post(url, data=content, headers=headers)
        return response

    def set_token(self):
        content = {
            "User": self.login_user,
            "Pass": self.login_psw,
            "Token": self.token_auth
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/Emblue3Service.svc/json/Authenticate', json.dumps(content))
            if response.status_code != 200:
                return f'set_token err: {response.text}'
            
            authJson = json.loads(response.content)
            self.token = authJson['Token']
            return True
        except Exception as e:
            return "set_token ex: "+ str(e)
        
    def existe_contato(self, email):
        content = {
            "Search": email,
            "Order": "asc",
            "GroupId": "0",
            "Token": self.token
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/SearchContact?=',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            
            usuarios = list(json.loads(response.content))
            if(len(usuarios)>0):
                return int(usuarios[0]['EmailId'])
            return -1
        except Exception as e:
            return "Ex "+ str(e)

    def criar_contato(self, mvx_cliente):
        content = {
            "Email": mvx_cliente.email_cliente,
            "EditCustomFields": self.montar_campos(mvx_cliente),
            "Token": self.token
        }

        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/NewContact',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            return json.loads(response.content)['EmailId']
        except Exception as e:
            return "Ex "+ str(e)
        
    def editar_contato(self, mvx_cliente):
        content = {
            "EmailId": str(mvx_cliente.emblue_email_id),
            "EditedFields": self.montar_campos(mvx_cliente),
            "Token": self.token
        }


        try:
            response = self.http_post('https://api.embluemail.com/Services/EmBlue3Service.svc/Json/EditCustomFieldsOneContact',json.dumps(content))
            if response.status_code != 200:
                return "Err: "+ response.text
            return True
        except Exception as e:
            return "Ex "+ str(e)

    def montar_campos(self, mvx_cliente):
        campo_esqueleto = "{0}:|:{1}:|:1"

        campos = {
            'nombre': mvx_cliente.nome_cliente if len(mvx_cliente.nome_cliente) > 0 else mvx_cliente.razao_cliente,
            'CPF': mvx_cliente.doc_cliente,
            'CNPJ': mvx_cliente.cnpj,
            'sexo': mvx_cliente.sexo,
            'telefono_1': mvx_cliente.cel_cliente,
            'cumpleanios': mvx_cliente.data_nascimento,
            'pais': encontrar_pais(mvx_cliente.pais),
            'ciudad': mvx_cliente.cidade_cliente, 
            'Estado': mvx_cliente.uf_cliente,
            'Produto_Um': '',
            'DataProduto_Um': '',
            'Categoria_Um': '',
            'Departamento_Um': '',
            'Canal_Um': '',
            'Loja_Um': '',
            'ProdutoMvxCod_Um': '',
            'Produto_Dois': '',
            'DataProduto_Dois': '',
            'Categoria_Dois': '',
            'Departamento_Dois': '',
            'Canal_Dois': '',
            'Loja_Dois': '',
            'ProdutoMvxCod_Dois': '',
            'Produto_Tres': '',
            'DataProduto_Tres': '',
            'Categoria_Tres': '',
            'Departamento_Tres': '',
            'Canal_Tres': '',
            'Loja_Tres': '',
            'ProdutoMvxCod_Tres': '',
            'Produto_Quatro': '',
            'DataProduto_Quatro': '',
            'Categoria_Quatro': '',
            'Departamento_Quatro': '',
            'Canal_Quatro': '',
            'Loja_Quatro': '',
            'ProdutoMvxCod_Quatro': '',
            'Produto_Cinco': '',
            'DataProduto_Cinco': '',
            'Categoria_Cinco': '',
            'Departamento_Cinco': '',
            'Canal_Cinco': '',
            'Loja_Cinco': '',
            'ProdutoMvxCod_Cinco': ''
        }

        num_extenso = ["Zero","Um","Dois","Tres","Quatro","Cinco"]
        number = 1

        lstProdutos = list(mvx_cliente.produtos)
        lstProdutos.reverse()
        for produto in lstProdutos:
            chaves = [f"Produto_{num_extenso[number]}",
                      f"DataProduto_{num_extenso[number]}",
                      f"Categoria_{num_extenso[number]}",
                      f"Departamento_{num_extenso[number]}",
                      f"Canal_{num_extenso[number]}",
                      f"Loja_{num_extenso[number]}",
                      f"ProdutoMvxCod_{num_extenso[number]}"]
            campos.update({
                chaves[0]: produto.nome,
                chaves[1]: produto.data,
                chaves[2]: produto.desc_linha,
                chaves[3]: produto.desc_setor,
                chaves[4]: produto.canal,
                chaves[5]: produto.empresa_nome,
                chaves[6]: produto.cod_produto,
            })
            number += 1
        
        campos_formatado = list(map(lambda x: campo_esqueleto.format(x,campos[x]), campos.keys()))
        return "|||".join(campos_formatado)
        
        

    