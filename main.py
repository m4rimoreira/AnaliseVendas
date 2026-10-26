from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DADOS = BASE / 'dados' / 'vendas_ficticias.csv'
SAIDA = BASE / 'resultados'
SAIDA.mkdir(exist_ok=True)

def gerar_dados(n=800, seed=42):
    rng = np.random.default_rng(seed)
    produtos = ['Notebook', 'Mouse', 'Teclado', 'Monitor', 'Headset']
    precos = {'Notebook': 3200, 'Mouse': 90, 'Teclado': 220, 'Monitor': 980, 'Headset': 260}
    p = rng.choice(produtos, n, p=[.16,.28,.22,.16,.18])
    q = rng.integers(1, 5, n)
    datas = pd.Timestamp('2025-01-01') + pd.to_timedelta(rng.integers(0,365,n),unit='D')
    df = pd.DataFrame({'data': datas, 'produto':p, 'quantidade':q,
                       'regiao':rng.choice(['Nordeste','Sudeste','Sul','Norte','Centro-Oeste'],n)})
    df['preco_unitario'] = [precos[x] for x in p]
    df['faturamento'] = df['quantidade'] * df['preco_unitario']
    DADOS.parent.mkdir(exist_ok=True)
    df.to_csv(DADOS,index=False)
    return df

def analisar(df):
    df['data'] = pd.to_datetime(df['data'])
    mensal = df.groupby(df['data'].dt.to_period('M'))['faturamento'].sum()
    produtos = df.groupby('produto')['faturamento'].sum().sort_values(ascending=False)
    regioes = df.groupby('regiao')['faturamento'].sum().sort_values(ascending=False)
    resumo = pd.DataFrame({'indicador':['Faturamento total','Pedidos','Ticket médio','Itens vendidos'],
                           'valor':[df.faturamento.sum(),len(df),df.faturamento.mean(),df.quantidade.sum()]})
    resumo.to_csv(SAIDA/'indicadores.csv',index=False)
    mensal.rename_axis('mes').reset_index().assign(mes=lambda d:d.mes.astype(str)).to_csv(SAIDA/'vendas_mensais.csv',index=False)
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    mensal.index=mensal.index.astype(str)
    mensal.plot(ax=axs[0],marker='o',title='Faturamento mensal')
    produtos.plot(kind='bar',ax=axs[1],title='Faturamento por produto')
    axs[0].tick_params(axis='x',rotation=55)
    axs[1].tick_params(axis='x',rotation=35)
    fig.tight_layout();fig.savefig(SAIDA/'grafico_vendas.png',dpi=160);plt.close(fig)
    print(resumo.to_string(index=False));print('\nReceita por região:\n',regioes)
    print('\nResultados em:',SAIDA)

if __name__=='__main__':
    df=pd.read_csv(DADOS) if DADOS.exists() else gerar_dados()
    analisar(df)
