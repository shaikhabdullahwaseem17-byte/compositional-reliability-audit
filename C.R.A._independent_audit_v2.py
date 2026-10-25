#!/usr/bin/env python3
# Researcher attribution: Shaikh Abdullah Waseem.
# Independent oracle/scoring audit. Read-only: does not edit the workbook.
import json, csv, math, argparse
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
ap=argparse.ArgumentParser(description="Independent oracle and strict-scoring audit")
ap.add_argument("workbook", nargs="?", default="C.R.O._C.R.A._raw_analysis_sheet.xlsx")
ap.add_argument("--outdir", default="C.R.O._independent_audit_outputs")
args=ap.parse_args()
OUT=Path(args.outdir); OUT.mkdir(parents=True, exist_ok=True)
WB_PATH=Path(args.workbook)
def get_rows(name, rng=None):
    df=pd.read_excel(WB_PATH, sheet_name=name, dtype=object, engine="openpyxl")
    df=df.where(pd.notna(df), None)
    return df.to_dict(orient="records")
trials=get_rows('Trial_Data')
gold=get_rows('Gold_Oracle')
task_rows=get_rows('Task_Bank')
tasks={str(r['Task_ID']):r for r in task_rows}
g_by={str(r['Run_ID']).strip():r for r in gold}
t_by={str(r['Run_ID']).strip():r for r in trials}

def strict_parse(raw):
    if raw is None or not str(raw).strip(): return None,False
    try: obj=json.loads(str(raw).strip())
    except Exception: return None,False
    if not isinstance(obj,dict) or set(obj.keys())!={'steps','final'} or not isinstance(obj['steps'],list): return obj,False
    for s in obj['steps']:
        if not isinstance(s,dict) or set(s.keys())!={'node','value'} or not isinstance(s.get('node'),str): return obj,False
    return obj,True

def op_eval(op, xs, ch, threshold):
    if op=='FILTER_CHAR': return [s for s in xs if str(ch).lower() in str(s).lower()]
    if op=='SORT_ALPHA': return sorted(xs)
    if op=='UPPERCASE_ITEMS': return [s.upper() for s in xs]
    if op=='REVERSE_LIST': return list(reversed(xs))
    if op=='COUNT_MATCH_GE_THRESHOLD': return sum(str(ch).lower() in str(s).lower() for s in xs) >= int(threshold)
    if op=='IS_EVEN_LENGTH': return len(xs)%2==0
    raise ValueError(op)

def expected_row(r):
    xs=json.loads(str(r['Input_List_JSON']))
    ch=str(r['Target_Character']); thr=int(r['Threshold'])
    phase=str(r['Phase']); st=str(r['Structure']); op=str(r['Operation_or_Graph'])
    steps=[]
    if phase=='CALIBRATION':
        val=op_eval(op,xs,ch,thr)
        steps=[{'node':op,'value':val}]
        final=val
    elif st=='PARALLEL_AND':
        keys=[('FILTER_CHAR','filter'),('SORT_ALPHA','sort'),('UPPERCASE_ITEMS','uppercase'),('REVERSE_LIST','reverse')]
        vals={}
        for operation,key in keys:
            value=op_eval(operation,xs,ch,thr)
            steps.append({'node':operation,'value':value}); vals[key]=value
        final=vals
    elif st=='SEQUENTIAL_CHAIN':
        curr=xs
        for operation in ['FILTER_CHAR','UPPERCASE_ITEMS','SORT_ALPHA','REVERSE_LIST']:
            curr=op_eval(operation,curr,ch,thr)
            steps.append({'node':operation,'value':curr})
        final=curr
    elif st=='CONDITIONAL':
        cond=op_eval('COUNT_MATCH_GE_THRESHOLD',xs,ch,thr)
        steps.append({'node':'COUNT_MATCH_GE_THRESHOLD','value':cond})
        operation='SORT_ALPHA' if cond else 'REVERSE_LIST'
        curr=op_eval(operation,xs,ch,thr); steps.append({'node':operation,'value':curr})
        curr=op_eval('UPPERCASE_ITEMS',curr,ch,thr); steps.append({'node':'UPPERCASE_ITEMS','value':curr})
        final=curr
    elif st=='NESTED_CONDITIONAL':
        cond=op_eval('COUNT_MATCH_GE_THRESHOLD',xs,ch,thr)
        steps.append({'node':'COUNT_MATCH_GE_THRESHOLD','value':cond})
        operation='FILTER_CHAR' if cond else 'SORT_ALPHA'
        curr=op_eval(operation,xs,ch,thr); steps.append({'node':operation,'value':curr})
        ev=op_eval('IS_EVEN_LENGTH',curr,ch,thr); steps.append({'node':'IS_EVEN_LENGTH','value':ev})
        operation2='UPPERCASE_ITEMS' if ev else 'REVERSE_LIST'
        curr=op_eval(operation2,curr,ch,thr); steps.append({'node':operation2,'value':curr})
        final=curr
    else: raise ValueError((phase,st,op))
    return {'steps':steps,'final':final}

assert len(trials)==336 and len(gold)==336
assert len(t_by)==336 and len(g_by)==336 and set(t_by)==set(g_by)
oracle_mismatches=[]; input_mismatches=[]; scores=[]; failures=[]
for r in trials:
    rid=str(r['Run_ID']).strip(); g=g_by[rid]
    if str(r['Phase'])=='COMPOSITION':
        # Composition inputs should match the relevant frozen task-bank row.
        task=tasks[str(r['Task_ID'])]
        if (json.loads(str(r['Input_List_JSON']))!=json.loads(str(task['Input_List_JSON'])) or
            str(r['Target_Character'])!=str(task['Target_Character']) or int(r['Threshold'])!=int(task['Threshold'])):
            input_mismatches.append((rid,'composition input/target/threshold differs from Task_Bank'))
    exp=expected_row(r); oracle=json.loads(str(g['Expected_JSON']))
    if exp!=oracle: oracle_mismatches.append((rid,str(r['Phase']),str(r['Structure']),exp,oracle))
    obj,schema=strict_parse(r.get('Raw_Response_Verbatim'))
    seq_ok=bool(schema and [x['node'] for x in obj['steps']]==[x['node'] for x in exp['steps']])
    step_values_ok=bool(schema and seq_ok and all(a['value']==e['value'] for a,e in zip(obj['steps'],exp['steps'])))
    final_ok=bool(schema and obj['final']==exp['final'])
    exact=bool(schema and seq_ok and step_values_ok and final_ok)
    scores.append({'Run_ID':rid,'Phase':str(r['Phase']),'Task_ID':str(r['Task_ID']),'Model':str(r['Model_Endpoint']),'Structure':str(r['Structure']),'Op':str(r['Operation_or_Graph']),'Schema':int(schema),'Sequence':int(seq_ok),'StepValues':int(step_values_ok),'Final':int(final_ok),'Exact':int(exact),'Expected':exp,'Parsed':obj,'Raw':str(r.get('Raw_Response_Verbatim') or '')})
    if str(r['Phase'])=='COMPOSITION' and not exact:
        category='STRICT_JSON_FAILURE' if not schema else ('NODE_SEQUENCE_FAILURE' if not seq_ok else ('STEP_VALUE_FAILURE' if not step_values_ok else 'FINAL_FIELD_FAILURE'))
        first=None
        if schema:
            for i,(a,e) in enumerate(zip(obj['steps'],exp['steps'])):
                if a!=e:
                    first={'index':i+1,'expected':e,'actual':a};break
            if first is None and obj['final']!=exp['final']:
                first={'index':'final','expected':exp['final'],'actual':obj['final']}
        failures.append({'Run_ID':rid,'Task_ID':str(r['Task_ID']),'Model':str(r['Model_Endpoint']),'Structure':str(r['Structure']),'category':category,'first':first,'exp':exp,'actual':obj,'raw_prefix':str(r.get('Raw_Response_Verbatim') or '')[:140].replace('\n','\\n')})

print('ROWS',len(trials),'UNIQUE_IDS',len(t_by),'ORACLE_ROWS',len(g_by),'MISSING_RAW',sum(not str(r.get('Raw_Response_Verbatim') or '').strip() for r in trials))
print('COMPOSITION_INPUT_MISMATCHES',len(input_mismatches))
print('INDEPENDENT_ORACLE_MISMATCHES',len(oracle_mismatches))
if oracle_mismatches:
    for x in oracle_mismatches[:5]: print('ORACLE_DIFF',x[:3])
by=defaultdict(Counter)
for s in scores:
    if s['Phase']=='COMPOSITION':
        c=by[s['Model']];
        for k in ['Schema','Sequence','StepValues','Final','Exact']: c[k]+=s[k]
        c['N']+=1
print('COMPOSITION BY MODEL')
for model,c in sorted(by.items()): print(model,dict(c),{k:round(c[k]/c['N'],4) for k in ['Schema','Sequence','StepValues','Final','Exact']})
print('BY MODEL x STRUCTURE')
by2=defaultdict(Counter)
for s in scores:
    if s['Phase']=='COMPOSITION':
        c=by2[(s['Model'],s['Structure'])]; c['N']+=1; c['Schema']+=s['Schema']; c['Exact']+=s['Exact']; c['Sequence']+=s['Sequence']; c['StepValues']+=s['StepValues']; c['Final']+=s['Final']
for k,c in sorted(by2.items()): print(k,dict(c))
print('CALIBRATION BY MODEL')
cal=defaultdict(Counter)
for s in scores:
    if s['Phase']=='CALIBRATION':
        c=cal[s['Model']]; c['N']+=1; c['Schema']+=s['Schema']; c['Exact']+=s['Exact']
for m,c in sorted(cal.items()): print(m,dict(c))
print('CALIBRATION BY MODEL x OP')
calop=defaultdict(Counter)
for s in scores:
    if s['Phase']=='CALIBRATION':
        c=calop[(s['Model'],s['Op'])]; c['N']+=1;c['Schema']+=s['Schema'];c['Exact']+=s['Exact']
for k,c in sorted(calop.items()): print(k,dict(c))
print('COMPOSITION FAILURE INVENTORY')
for x in failures:
    if x['Model']=='Model_B': print(x['Run_ID'],x['Task_ID'],x['Structure'],x['category'],'first_mismatch=',str(x['first'])[:220])
print('FAILURE CATEGORIES',dict(Counter(x['category'] for x in failures)))
print('MODEL_B FAILURE CATEGORIES',dict(Counter(x['category'] for x in failures if x['Model']=='Model_B')))
# Save compact row-level independent scores and failure inventory.
with open(OUT/'C.R.O._independent_row_scores.csv','w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['Run_ID','Phase','Task_ID','Model','Structure','Operation_or_Graph','Schema_Valid','Node_Sequence_Correct','Step_Values_Correct','Final_Correct','Exact_Task_Success'])
 for s in scores:w.writerow([s['Run_ID'],s['Phase'],s['Task_ID'],s['Model'],s['Structure'],s['Op'],s['Schema'],s['Sequence'],s['StepValues'],s['Final'],s['Exact']])
with open(OUT/'C.R.O._independent_failure_inventory.csv','w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['Run_ID','Task_ID','Model','Structure','Failure_Category','First_Mismatch_Index','Expected_First_Mismatch_JSON','Actual_First_Mismatch_JSON','Raw_Prefix'])
 for x in failures:
  mm=x['first'] or {};w.writerow([x['Run_ID'],x['Task_ID'],x['Model'],x['Structure'],x['category'],mm.get('index'),json.dumps(mm.get('expected'),ensure_ascii=False),json.dumps(mm.get('actual'),ensure_ascii=False),x['raw_prefix']])
