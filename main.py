

from mvx.mvx_service import *
from shared.log import *
from mvx.mvx_classes import *
from itertools import groupby
from emblue.emblue_service import *
from periodos import *
from falhaService import *
import time

def init():
    log("Iniciando o script")
    try:
        while(True):
            periodoservice = PeriodoService()
            datas = periodoservice.prox()
            if(datas == None):
                log("Todas os peridos foram importados na emblue")
                quit()

            dateNow = datetime.now()
            hr = dateNow.hour

            hrini = 7
            hrfin = 6
            if hr >= hrfin and hr <= hrini:
                log(f"Tarefa abortada devido ao horario. Periodo de extracao entre {hrini}h ate as {hrfin}h")
                quit()

            if tarefa(datas) != False:
                periodoservice.salvar()
                log(f"Porcentagem enviada: {periodoservice.porcentagem()}")
            
            time.sleep(5)

    except Exception as e:
        log("Excecao ao executar o script")
        log(str(e))

def tarefa(datas):
    service = MvxService()
    falhas = FalhaService()

    log(f"Periodo em execucao: {datetime.strftime(datas[0],'%d/%m/%Y')} ate {datetime.strftime(datas[1],'%d/%m/%Y')}")


    skipTouched = False
    erro_busca_mov = 0

    #busca todas as empresas
    empresaLst = service.empresas()
    if isinstance(empresaLst,str):
        log("falha para buscar as empresas")
        log(empresaLst)
        quit()


    # filtra empresas por:
    # 1. Tem CNPJ
    # 2. CNPJ Distinto
    empresasComCnjp = list(filter(lambda x: len(x["CNPJ"])>0, empresaLst))
    empresasPorCnpj = groupby(empresasComCnjp,lambda x: x["CNPJ"])
    mvx_empresas = []
    for key, group in empresasPorCnpj:
        model = MvxEmpresa(list(group).pop())
        mvx_empresas.append(model)

    # busca movimentos de cnpj
    total_empresas = len(mvx_empresas)
    contagem_empresas_consultadas = 0
    for mvx_emp_lojas in mvx_empresas:
        cnpj = mvx_emp_lojas.cnpj

        if erro_busca_mov > 12:
            log("Houve mais do que 12 falhas para buscar os movimentos. Reiniciando em um minuto")
            time.sleep(60)
            return False

        log("Consultando a empresa: "+ cnpj)
        
        movs = service.movimentos(cnpj,datas[0],datas[1])
        if isinstance(movs,str):
            log(f"Não foi possivel buscar os movimentos da empresa {cnpj} ")
            falhas.addEmpresa(cnpj,datas[0],datas[1])
            erro_busca_mov += 1
            continue

        movs.reverse()#.sort(key= lambda mov: datetime.strptime(mov['dt_update'], '%d/%m/%Y %H:%M:%S'),reverse=True)
        
        for mov in movs:

            mvxCliente = service.encontrar_cliente(cnpj,mov['codigo_cliente'])
            if(isinstance(mvxCliente,str)):
                log(mvxCliente)
                falhas.addCliente(mov['codigo_cliente'],datas[0],datas[1], 'mvx_encontrar')
            elif mvxCliente.tipo == 'c':

                #Se o cliente possuir mais de 5 produtos então fechou
                if mvxCliente.qtd_produtos() < 5:
                    produto = service.encontrar_produto(cnpj,mov['cod_produto'])
                    if(isinstance(produto,str)):
                        log(f"Falha para encontrar o produto {mov['cod_produto']}")
                        log(produto)
                    else:
                        mvx_produto = MvxProdutoVendido(produto,mvx_emp_lojas.empresa,mov['dt_update'])
                        mvxCliente.addProduto(mvx_produto)
        
        
        contagem_empresas_consultadas += 1
        log("Consultas " + str(contagem_empresas_consultadas) + '/' + str(total_empresas))
        log("Requisicoes ate aqui. Clientes:" + str(service.contagem_req_clientes) + ' | Produtos:' + str(service.contagem_req_produtos))
    
    service.salvar_em_memoria(False)

    #filtra clientes para atualizar:
    mvx_clientes = list(filter(lambda x: len(x.email_cliente) > 0 and (skipTouched or x.touched) and x.tipo == 'c', service.LISTA_MVXCLIENTES)) #
    usuarios_integrados = 0
    usuarios_nao_integrados = 0
    
    emblue = EmblueService("TOKEN_AQUI","EMAIL_AQUI","SENHA_AQUI")
    if isinstance(emblue.token_res, str):
        log("Erro no token da emblue")
        log(emblue.token_res)
        quit()

    for mvx_cliente in mvx_clientes:
        res = emblue.atualizar_contato(mvx_cliente)
        if res == True:
            usuarios_integrados += 1
            log(f'Usuarios integrados na emblue: {usuarios_integrados}/{len(mvx_clientes)}')
        else:
            usuarios_nao_integrados += 1
            log(f'Falha de integração na emblue: {usuarios_nao_integrados} - cod: {mvx_cliente.cod_cliente}')
            falhas.addCliente(mvx_cliente.cod_cliente,datas[0],datas[1], 'emblue_enviar')

    service.salvar_em_memoria(True)


init()


