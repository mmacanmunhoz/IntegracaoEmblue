
from mvx.mvx_api import *
from mvx.mvx_classes import *
from mvx.mvx_util import mvx_sanitize_json
from datetime import datetime, timedelta
import json


class MvxService:

    def __init__(self):
        self.LISTA_MVXCLIENTES = []
        self.LISTA_MVXPRODUTOS = []
        self.contagem_req_clientes = 0
        self.contagem_req_produtos = 0
        self.carregar_em_memoria()


    def empresas(self):
        try:
            response = buscar_empresas()
            print(response.status_code)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            return list(json.loads(jsonBytes)['ResponseData'])
        except Exception as e:
            return 'EX: ' + str(e)
        
    def lojas(self, cnpj):
        try:
            response = buscar_lojas(cnpj)
            print(response.status_code)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            return list(json.loads(jsonBytes)['ResponseData'])
        except Exception as e:
            return 'EX: ' + str(e)
        
    def movimentos(self, cnpj,data_ini, data_fin):
        try:
            response = buscar_movimentos(cnpj,data_ini,data_fin)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            movs = list(json.loads(jsonBytes)['ResponseData'])
            return movs
        except Exception as e:
            return 'EX: ' + str(e)
        
    def movimentosDeOntem(self, cnpj):
        data_ini = datetime.today().date() - timedelta(days=1)
        data_fin = datetime.today().date() - timedelta(seconds=-1)
        return self.movimentos(cnpj,data_ini,data_fin)



    def encontrar_cliente(self,cnpj, codCliente):

        encontrado = next(filter(lambda c: c.cod_cliente == codCliente ,self.LISTA_MVXCLIENTES), None)
        if encontrado != None:
            return encontrado

        try:
            self.contagem_req_clientes += 1
            response = buscar_cliente(cnpj,codCliente)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            reqs = list(json.loads(jsonBytes)['ResponseData'])
            if len(reqs) > 0:
                mvx_cliente = MvxCliente(reqs[0])
                self.LISTA_MVXCLIENTES.append(mvx_cliente)
                return mvx_cliente
        
            return 'Not found'
        except Exception as e:
            return 'EX: ' + str(e)

    def encontrar_produto(self, cnpj, cod):
       
        encontrado = next(filter(lambda c: c['cod_produto'] == cod ,self.LISTA_MVXPRODUTOS), None)
        if encontrado != None:
            return encontrado

        try:
            self.contagem_req_produtos += 1
            response = buscar_produto(cnpj,cod)
            if response.status_code != 200:
                return 'ERR: '+ response.text
            
            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content)
            jsonBytes = jsonStr.encode()
            
            reqs = list(json.loads(jsonBytes)['ResponseData'])
            if len(reqs) > 0:
                prod = reqs[0]
                self.LISTA_MVXPRODUTOS.append(prod)
                return prod
        
            return 'Not found'
        except Exception as e:
            return 'EX: ' + str(e)

    def buscar_todos_os_clientes(self,cnpj, data_i, data_f):
        
        try:
            response = buscar_todos_os_cliente(cnpj,data_i, data_f)
            if response.status_code != 200:
                return 'ERR: '+ response.text

            content = response.content.decode()
            jsonStr = mvx_sanitize_json(content).replace("\\\",","\",").replace("\\","\\\\").replace("\\\\\"","\\\"")
            jsonBytes = jsonStr.encode()
            
            clienteLst = list(json.loads(jsonBytes)['ResponseData'])
            
            clientes = list(filter(lambda x: x['tipo_cadastro'].lower() == 'c',clienteLst))
            creal = 0
            for c in clientes:
                encontrado = next(filter(lambda x: x.cod_cliente == c['cod_cliente'] ,self.LISTA_MVXCLIENTES), None)
                if encontrado == None:
                    mvx_cliente = MvxCliente(c)
                    self.LISTA_MVXCLIENTES.append(mvx_cliente)
                    creal += 1
        
            return (creal,len(clientes))
        except Exception as e:
            return (0,'EX: ' + str(e))
    

    def carregar_em_memoria(self):
        clientesBytes = None
        with open('data/clientes.json', 'rb') as file:
            clientesBytes = file.readline()

        clientesTemp = list(json.loads(clientesBytes))
        self.LISTA_MVXCLIENTES = list([])
        for ct in clientesTemp:
            mvx_cliente = MvxCliente(None)
            mvx_cliente.__dict__.update(ct)
            prods = []
            for prod in ct['produtos']:
                mvx_prod = MvxProdutoVendido(None,None,None)
                mvx_prod.__dict__.update(prod)
                prods.append(mvx_prod)
            mvx_cliente.produtos = prods
            self.LISTA_MVXCLIENTES.append(mvx_cliente)
        
        produtosBytes = None
        with open('data/produtos.json', 'rb') as file:
            produtosBytes = file.readline()
            
        self.LISTA_MVXPRODUTOS = list(json.loads(produtosBytes))

    def salvar_em_memoria(self, alterarTouched):
        for cliente in self.LISTA_MVXCLIENTES:
            produtosOrdenados = sorted(cliente.produtos, key=parse_date)
            cliente.produtos = produtosOrdenados[-5:]
            if alterarTouched:
                cliente.touched = False

        cliente_serializado = [cliente.to_json() for cliente in self.LISTA_MVXCLIENTES]
        lst_cliente_json = json.dumps(cliente_serializado,ensure_ascii=False)
        with open('data/clientes.json', 'wb') as file:
            file.write(lst_cliente_json.encode())
        
        lst_produtos_json = json.dumps(self.LISTA_MVXPRODUTOS,ensure_ascii=False)
        with open('data/produtos.json', 'wb') as file:
            file.write(lst_produtos_json.encode())




def parse_date(item):
    return datetime.strptime(item.data, "%d/%m/%Y %H:%M:%S")