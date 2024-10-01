
from datetime import datetime, timedelta

class MvxEmpresa:
    def __init__(self, empresa, lojas = []):
        self.lojas = lojas
        self.empresa = empresa
        self.cnpj = empresa['CNPJ']

    def addLoja(self, loja):
        self.lojas.append(loja)


class MvxProdutoVendido:
    def __init__(self,produto, empresa, dataCompra):
        self.cod_produto = produto['cod_produto'] if produto != None else ''
        self.nome = produto['nome'] if produto != None else ''
        self.desc_linha = produto['desc_linha'] if produto != None else ''
        self.desc_setor = produto['desc_setor'] if produto != None else ''
        self.cnpj = empresa['CNPJ'] if empresa != None else ''
        self.empresa_nome = empresa['nome_portal'] if empresa != None else ''
        self.data = dataCompra if dataCompra != None else ''
        self.canal = ('Virtual' if produto['loja_virtual'] == 'S' else 'Fisica') if produto != None else ''



class MvxCliente:
    def __init__(self, cliente):
        self.cod_cliente = cliente['cod_cliente'] if cliente != None else ''
        self.nome_cliente = cliente['nome_cliente'] if cliente != None else ''
        self.razao_cliente = cliente['razao_cliente'] if cliente != None else ''
        self.cnpj = cliente['doc_cliente'] if cliente != None and cliente['tipo_cliente'] == 'J' else ''
        self.doc_cliente = cliente['doc_cliente'] if cliente != None and cliente['tipo_cliente'] != 'J' else ''
        self.sexo = cliente['sexo'] if cliente != None else ''
        self.email_cliente = cliente['email_cliente'] if cliente != None else ''
        self.cel_cliente = cliente['cel_cliente'] if cliente != None else ''
        self.data_nascimento = cliente['data_nascimento'] if cliente != None else ''
        self.cidade_cliente = cliente['cidade_cliente'] if cliente != None else ''
        self.uf_cliente = cliente['uf_cliente'] if cliente != None else ''
        self.pais = cliente['pais'] if cliente != None else ''
        self.produtos = []
        self.emblue_email_id = 0
        self.tipo = cliente['tipo_cadastro'].lower() if cliente != None else ''
        self.touched = False

    def addProduto(self, produtoVendido):
        if produtoVendido.cod_produto in list(map(lambda x: x.cod_produto,self.produtos)):
            return
        
        self.produtos.append(produtoVendido)
        self.touched = True

        sorted = list(self.produtos)
        sorted.sort(key= lambda x : datetime.strptime(x.data, '%d/%m/%Y %H:%M:%S'))
        if len(sorted) > 5:
            self.produtos = sorted[-5:]

        

    def to_json(self):
        thisDic = self.__dict__.copy()
        thisDic.update({ 'produtos': [p.__dict__ for p in self.produtos]})
        return thisDic
    
    def qtd_produtos_atuais(self,quantidade):
        dataDeCorte = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        prods = list(filter(lambda p: datetime.strptime(p.data, "%d/%m/%Y %H:%M:%S") >= dataDeCorte,self.produtos))
        return len(prods) >= quantidade
    
    def qtd_produtos(self):
        if self.produtos is None:
            return 0
        return len(self.produtos)

