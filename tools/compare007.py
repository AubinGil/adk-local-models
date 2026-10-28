"""Brief 007 reproducible comparison. Run with the isolated native-compare Python."""
import asyncio, hashlib, importlib.metadata as md, json, sys, socket, datetime
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1]/'src')]
import httpx
from openai import AsyncOpenAI
from google.adk.integrations.openai import OpenAILlm
from adk_local_models import OpenAICompatibleLlm
from tests.fake_server import FakeServer
from tests.requests import fixed_requests, KNOBS
ROOT=Path('runs/007-native-compare')
active=None
counts={}
original_send=httpx.AsyncClient.send
original_raw=httpx.Response.aiter_raw

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8')

async def send(client,request,*a,**kw):
    host=request.url.host
    if host not in ('127.0.0.1','localhost'): raise RuntimeError('Non-local endpoint forbidden')
    if request.url.port in (8038,11434,8080):
        port=request.url.port
        counts[port]=counts.get(port,0)+1
        if counts[port]>12: raise RuntimeError('Live request cap')
    rec={'method':request.method,'url':str(request.url),'request':request.content,'reply':bytearray(),
         'headers':dict(request.headers)}
    active['exchanges'].append(rec)
    wanted_stream=kw.get('stream',False)
    kw['stream']=True
    try:
        response=await original_send(client,request,*a,**kw)
    finally:
        rec['request']=request.content
        rec['headers']=dict(request.headers)
    rec['status']=response.status_code
    rec['response_headers']=dict(response.headers)
    response.extensions['comparison']=rec
    if not wanted_stream: await response.aread()
    return response
async def raw(response,*a,**kw):
    async for chunk in original_raw(response,*a,**kw):
        rec=response.extensions.get('comparison')
        if rec is not None: rec['reply'].extend(chunk)
        yield chunk
httpx.AsyncClient.send=send
httpx.Response.aiter_raw=raw

def save(path,record):
    for i,ex in enumerate(record['exchanges'],1):
        folder=path/f'exchange-{i}'
        folder.mkdir(parents=True,exist_ok=True)
        for key in ('request','reply'):
            data=bytes(ex.pop(key))
            (folder/f'{key}.bin').write_bytes(data)
            ex[key+'_sha256']=hashlib.sha256(data).hexdigest()
            ex[key+'_length']=len(data)
        dump(folder/'exchange.json',ex)
    dump(path/'outcome.json',record)

async def make(kind,url,model,profile,knobs=False):
    if kind=='local':
        return OpenAICompatibleLlm(base_url=url,model=model,profile=profile,extra_body=KNOBS[profile],timeout=60),None
    async def hook(request):
        # Native class has no arbitrary extra_body field; explicit transport shim.
        if knobs and request.method=='POST':
            body=json.loads(request.content); body.update(KNOBS[profile])
            data=json.dumps(body,separators=(',',':')).encode()
            request._content=data; request.stream=httpx.ByteStream(data)
            request.headers['Content-Length']=str(len(data))
    client=AsyncOpenAI(base_url=url,api_key='comparison-placeholder',max_retries=0,timeout=60,
        http_client=httpx.AsyncClient(trust_env=False,event_hooks={'request':[hook]},headers={'Accept-Encoding':'identity'}))
    return OpenAILlm(model=model,base_url=url,client=client),client

async def run(path,model,request,stream):
    global active
    active={'exchanges':[],'responses':[],'stream':stream}
    try:
        async for r in model.generate_content_async(request.model_copy(deep=True),stream=stream):
            active['responses'].append(r.model_dump(mode='json',exclude_none=True))
    except Exception as e: active['exception']={'type':type(e).__name__,'message':str(e)}
    save(path,active)
    return active

async def fake():
    summary={}
    body=json.loads(Path('tests/fixtures/text.json').read_text(encoding='utf-8'))
    body['usage']['completion_tokens_details']={'reasoning_tokens':2}
    dump(ROOT/'fixtures/reasoning.json',body)
    for label,reason in [('length','length'),('filtered','content_filter')]:
        variant=json.loads(json.dumps(body)); variant['choices'][0]['finish_reason']=reason
        dump(ROOT/f'fixtures/{label}.json',variant)
    for profile in KNOBS:
        for kind in ('local','native'):
            for name,req in fixed_requests().items():
                for stream in (False,True):
                    fixture=('tool' if name=='tools' else 'text')+('.sse' if stream else '.json')
                    with FakeServer(fixture) as server:
                        model,client=await make(kind,server.base_url,'fixture-model',profile)
                        key=f'{profile}/{kind}/{name}-'+('stream' if stream else 'plain')
                        result=await run(ROOT/'fake'/key,model,req,stream)
                        summary[key]={'responses':result['responses'],'exception':result.get('exception')}
                        if client: await client.close()
            for case,fixture,stream in [('http500','error.json',False),('malformed','malformed.json',False),('truncated','truncated.sse',True),('bad-arguments','bad-arguments.json',False),('reasoning',str((ROOT/'fixtures/reasoning.json').resolve()),False),('length',str((ROOT/'fixtures/length.json').resolve()),False),('filtered',str((ROOT/'fixtures/filtered.json').resolve()),False),('refused',None,False)]:
                with FakeServer(fixture or 'text.json') as server:
                    url=server.base_url
                    if fixture is None:
                        with socket.socket() as s: s.bind(('127.0.0.1',0)); url=f'http://127.0.0.1:{s.getsockname()[1]}/v1'
                    model,client=await make(kind,url,'fixture-model',profile)
                    result=await run(ROOT/'fake'/profile/kind/case,model,fixed_requests()['text'],stream)
                    summary[f'{profile}/{kind}/{case}']={'responses':result['responses'],'exception':result.get('exception')}
                    if client: await client.close()
    dump(ROOT/'fake-summary.json',summary)

async def runner(path,model):
    global active
    from google.adk.agents import LlmAgent
    from google.adk.agents.run_config import RunConfig
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    calls=[]
    def weather(city:str)->dict:
        """Get weather for a city."""
        calls.append({'city':city,'result':{'temperature':20}})
        return {'temperature':20}
    agent=LlmAgent(name='local',model=model,tools=[weather],instruction='Be concise. Use weather once for the requested city, then answer from its result. Do not call weather again after receiving its result.',generate_content_config=types.GenerateContentConfig(temperature=0,top_p=0.9,max_output_tokens=128))
    sessions=InMemorySessionService()
    await sessions.create_session(app_name='compare007',user_id='user',session_id='plain')
    r=Runner(agent=agent,app_name='compare007',session_service=sessions)
    active={'exchanges':[],'events':[],'tool_executions':calls}
    try:
        async for e in r.run_async(user_id='user',session_id='plain',new_message=types.Content(role='user',parts=[types.Part(text='Weather in Paris?')]),run_config=RunConfig(max_llm_calls=2)):
            active['events'].append(e.model_dump(mode='json',exclude_none=True))
    except Exception as e: active['exception']={'type':type(e).__name__,'message':str(e)}
    session=await sessions.get_session(app_name='compare007',user_id='user',session_id='plain')
    active['session_events']=[e.model_dump(mode='json',exclude_none=True) for e in session.events]
    save(path,active)

async def live():
    global active
    summary=json.loads((ROOT/'live-summary.json').read_text()) if (ROOT/'live-summary.json').exists() else {}
    if (ROOT/'manifest.json').exists():
        counts.update({int(k):v for k,v in json.loads((ROOT/'manifest.json').read_text())['live_request_counts'].items()})
    selected=sys.argv[sys.argv.index('--profile')+1] if '--profile' in sys.argv else None
    for profile,url,modelname in [('vllm','http://localhost:8038/v1','nemotron-3.5-bolt-e4b'),('ollama','http://127.0.0.1:11434/v1','gemma4:e4b'),('llama_server','http://localhost:8080/v1',None)]:
        if selected and profile!=selected: continue
        probe=ROOT/'live'/profile/('probe-2' if (ROOT/'live'/profile/'probe').exists() else 'probe')
        active={'exchanges':[]}
        try:
            async with httpx.AsyncClient(timeout=3,trust_env=False) as c:
                response=await c.get(url+'/models'); response.raise_for_status(); models=response.json()
            advertised=[m['id'] for m in models['data']]
            summary[profile]={'advertised':advertised}
        except Exception as e:
            active['exception']={'type':type(e).__name__,'message':str(e)}
            save(probe,active); summary[profile]={'skipped':active['exception']}; continue
        save(probe,active)
        if modelname is None:
            summary[profile]['skipped']='No previously authorized served model; probe only'; continue
        if modelname not in advertised:
            summary[profile]['skipped']='Previously selected model absent'; continue
        for kind in ('local','native'):
            model,client=await make(kind,url,modelname,profile,knobs=True)
            if kind=='local': model._identity={'models':models,'server':response.headers.get('server'),'reply_sha256':hashlib.sha256(response.content).hexdigest()}
            for name in ('text','tools'):
                for stream in (False,True):
                    await run(ROOT/'live'/profile/kind/(name+('-stream' if stream else '-plain')),model,fixed_requests()[name],stream)
            if kind=='native': await runner(ROOT/'live'/profile/'native'/'runner',model)
            if client: await client.close()
        summary[profile]['http_requests']=counts.get(response.request.url.port,0)
        dump(ROOT/'live-summary.json',summary)
    dump(ROOT/'live-summary.json',summary)
    if (ROOT/'manifest.json').exists():
        manifest=json.loads((ROOT/'manifest.json').read_text()); manifest['live_request_counts']={str(k):v for k,v in counts.items()}
        dump(ROOT/'manifest.json',manifest)

if __name__=='__main__':
    asyncio.run(fake() if '--fake' in sys.argv else live())
