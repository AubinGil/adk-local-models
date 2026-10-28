"""Field-level wire diffs and independent saved-byte verification."""
import hashlib,json
from pathlib import Path
R=Path('runs/007-native-compare')
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for k in sorted(a.keys()|b.keys()):
            p=path+'/'+k
            if k not in a: out.append({'path':p,'local':'<absent>','native':b[k]})
            elif k not in b: out.append({'path':p,'local':a[k],'native':'<absent>'})
            else: out+=diff(a[k],b[k],p)
        return out
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return [item for i,(x,y) in enumerate(zip(a,b)) for item in diff(x,y,path+'/'+str(i))]
    if a!=b: return [{'path':path,'local':a,'native':b}]
    return []
all_diffs={}
for local in (R/'fake').glob('*/local/*/outcome.json'):
    native=local.parent.parent.parent/'native'/local.parent.name/'outcome.json'
    if not native.exists(): continue
    l=load(local);n=load(native)
    def post(p,o):
        for i,e in enumerate(o['exchanges'],1):
            if e['method']=='POST': return load(p.parent/f'exchange-{i}/request.bin')
    a,b=post(local,l),post(native,n)
    if a is not None and b is not None: all_diffs[str(local.parent.relative_to(R/'fake'))]=diff(a,b)
(R/'wire-diffs.json').write_text(json.dumps(all_diffs,indent=2)+'\n')
live_diffs={}
for local in (R/'live').glob('*/local/*/outcome.json'):
    native=local.parent.parent.parent/'native'/local.parent.name/'outcome.json'
    if not native.exists(): continue
    a=load(local.parent/'exchange-1/request.bin'); b=load(native.parent/'exchange-1/request.bin')
    live_diffs[str(local.parent.relative_to(R/'live'))]=diff(a,b)
(R/'live-wire-diffs.json').write_text(json.dumps(live_diffs,indent=2)+'\n')
errors=[]; total=0
for p in R.rglob('exchange.json'):
    e=load(p)
    for k in ('request','reply'):
        data=(p.parent/(k+'.bin')).read_bytes();total+=1
        if hashlib.sha256(data).hexdigest()!=e[k+'_sha256'] or len(data)!=e[k+'_length']: errors.append(str(p)+':'+k)
    if e.get('status')==200 and e['reply_length']==0: errors.append(str(p)+':empty success')

fixture_checks=0
metadata_checks=0
for p in (R/'fake').glob('*/*/*/outcome.json'):
    o=load(p); label=p.parent.name
    fixture=None
    if '-' in label and label.rsplit('-',1)[-1] in ('plain','stream'):
        fixture=Path('tests/fixtures')/ (('tool' if label.startswith('tools-') else 'text')+('.sse' if label.endswith('stream') else '.json'))
    else:
        mapping={'http500':'error.json','malformed':'malformed.json','truncated':'truncated.sse','bad-arguments':'bad-arguments.json'}
        if label in mapping: fixture=Path('tests/fixtures')/mapping[label]
        elif label in ('reasoning','length','filtered'): fixture=R/'fixtures'/(label+'.json')
    for i,e in enumerate(o['exchanges'],1):
        if fixture and e['method']=='POST':
            fixture_checks+=1
            if (p.parent/f'exchange-{i}/reply.bin').read_bytes()!=fixture.read_bytes(): errors.append(str(p)+':fixture mismatch')
for p in R.rglob('outcome.json'):
    o=load(p); posts=[e for e in o['exchanges'] if e['method']=='POST']
    if not posts: continue
    for response in o.get('responses',[]):
        meta=response.get('custom_metadata') or {}
        if meta.get('reply_complete'):
            metadata_checks+=1
            if any(meta[k]!=posts[-1][k] for k in ('request_sha256','reply_sha256')): errors.append(str(p)+':adapter metadata mismatch')
final_comparisons=0
for profile in ('vllm','ollama','llama_server'):
    for kind in ('local','native'):
        for name in ('text','tools','history'):
            finals=[]
            for mode in ('plain','stream'):
                o=load(R/'fake'/profile/kind/f'{name}-{mode}'/'outcome.json')
                f=o['responses'][-1]
                finals.append({k:f.get(k) for k in ('content','finish_reason','usage_metadata')})
            final_comparisons+=1
            if finals[0]!=finals[1]: errors.append(f'{profile}/{kind}/{name}:final mismatch')
(R/'verification.json').write_text(json.dumps({'files_verified':total,'fixture_replies_verified':fixture_checks,'adapter_final_metadata_verified':metadata_checks,'plain_stream_final_comparisons':final_comparisons,'errors':errors},indent=2)+'\n')
assert not errors,errors
print('Verified',total,'wire files,',fixture_checks,'fixture replies,',metadata_checks,'adapter metadata records')

summary={}
for p in R.glob('fake/*/*/*/outcome.json'):
    o=load(p); rs=o.get('responses',[]); last=rs[-1] if rs else {}
    summary[str(p.parent.relative_to(R/'fake'))]={'response_count':len(rs),'partial_values':[x.get('partial') for x in rs],'tool_calls_on_partials':sum(1 for x in rs if x.get('partial') for part in (x.get('content') or {}).get('parts',[]) if part.get('function_call')),'final_finish_reason':last.get('finish_reason'),'final_usage':last.get('usage_metadata'),'final_error':last.get('error_code'),'exception_type':(o.get('exception') or {}).get('type')}
(R/'response-comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
