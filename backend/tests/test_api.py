import json
import pytest
import httpx
from fastapi.testclient import TestClient
import main

@pytest.fixture
def client(tmp_path, monkeypatch):
    engine=main.create_engine('sqlite:///'+str(tmp_path/'test.db'))
    monkeypatch.setattr(main,'engine',engine)
    monkeypatch.setattr(main,'Session',main.sessionmaker(bind=engine))
    monkeypatch.delenv('ALPHA_VANTAGE_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    for name in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):
        monkeypatch.delenv(name,raising=False)
    with TestClient(main.app) as client:
        yield client
    engine.dispose()

def test_no_keys_and_symbol_validation(client):
    assert client.get('/api/health').json()['status']=='ok'
    assert client.get('/api/stocks/NVDA').status_code==503
    assert client.get('/api/stocks/INVALID!').status_code==422
    assert client.post('/api/stocks/NVDA/analysis').status_code==503

def test_provider_cache(client,monkeypatch):
    calls=[]
    async def provider(function,symbol):
        calls.append(function)
        if function=='TIME_SERIES_DAILY':
            return {'Time Series (Daily)':{f'2025-01-{i:02d}':{'4. close':str(100+i)} for i in range(1,25)}}
        if function=='OVERVIEW':
            return {'Name':'Example','MarketCapitalization':'1000000000','PERatio':'20','ProfitMargin':'.2','QuarterlyRevenueGrowthYOY':'.1'}
        return {'feed':[{'title':'Example article','ticker_sentiment':[{'ticker':'NVDA','ticker_sentiment_score':'.4'}],'url':'javascript:alert(1)'}]}
    monkeypatch.setattr(main,'provider',provider)
    first=client.get('/api/stocks/nvda')
    assert first.status_code==200
    assert first.json()['symbol']=='NVDA'
    assert first.json()['news'][0]['url'] is None
    assert first.json()['indicators']['rsi14']==100
    assert client.get('/api/stocks/NVDA').json()==first.json()
    assert len(calls)==3

def test_ai_rejects_invented_sources(client,monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-key')
    async def stock(symbol):
        return {'symbol':'NVDA','name':'Example','cap':1,'pe':20,'revenue':10,'margin':20,'as_of':'2025-01-01','news':[{'id':'n1'}]}
    monkeypatch.setattr(main,'get_stock',stock)
    brief={'summary':'Summary','bullish':[{'text':'Claim','source_ids':['invented']}],'bearish':[],'uncertainties':[]}
    class Fake:
        async def post(self,*args,**kwargs):
            return httpx.Response(200,request=httpx.Request('POST','https://api.openai.com/v1/responses'),json={'output':[{'content':[{'type':'output_text','text':json.dumps(brief)}]}]})
    monkeypatch.setattr(main.app.state,'client',Fake())
    assert client.post('/api/stocks/NVDA/analysis').status_code==502
    brief['bullish'][0]['source_ids']=['n1']
    assert client.post('/api/stocks/NVDA/analysis').json()['mode']=='ai'
