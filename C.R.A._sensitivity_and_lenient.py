#!/usr/bin/env python3
# Researcher attribution: Shaikh Abdullah Waseem.
# Post-hoc sensitivity only; not the primary analysis. The historical workbook is not included.
import sys, json, math, csv, argparse, importlib.util
from pathlib import Path
from collections import Counter,defaultdict
import pandas as pd
ap=argparse.ArgumentParser(description="Post-hoc A0045 and embedded-JSON sensitivity diagnostics")
ap.add_argument("workbook", nargs="?", default="C.R.O._C.R.A._raw_analysis_sheet.xlsx")
ap.add_argument("--predictions", default="C.R.O._Frozen_Predictions_workbook_matching.csv")
ap.add_argument("--outdir", default="C.R.O._sensitivity_outputs")
args=ap.parse_args(); OUT=Path(args.outdir); OUT.mkdir(parents=True, exist_ok=True)
module_path=Path(__file__).with_name("C.R.O._analyze_compositional_reliability_v2.py")
spec=importlib.util.spec_from_file_location("compositional_reliability_module", module_path)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
current=str(Path(args.workbook)); _,_,cur=mod.read_book(current)
rowid='A0045'
cur_raw=str(cur.loc[cur.Run_ID.astype(str)==rowid,'Raw_Response_Verbatim'].iloc[0])
# Exact matching response preserved in the earlier workbook, included here only for the labelled A0045 sensitivity.
old_raw='{"steps":[{"node":"IS_EVEN_LENGTH","value":false}],"final":false}' 
exp=json.loads(str(cur.loc[cur.Run_ID.astype(str)==rowid,'Expected_JSON'].iloc[0]))
prompt=str(cur.loc[cur.Run_ID.astype(str)==rowid,'Prompt_Text'].iloc[0])
print('A0045 model/phase/task/op:',cur.loc[cur.Run_ID.astype(str)==rowid,['Model_Endpoint','Phase','Task_ID','Operation_or_Graph']].iloc[0].to_dict())
print('A0045 prompt suffix:',prompt[-280:])
print('A0045 expected:',exp)
print('A0045 current raw:',cur_raw[:600].replace('\n','\\n'))
print('A0045 original raw:',old_raw[:300].replace('\n','\\n'))

# Primary as-frozen analysis using the frozen file that exactly matches the current workbook.
pred_path=Path(args.predictions)
pred=pd.read_csv(pred_path)
scored=mod.score_rows(cur)
comp_primary=mod.crossvalidated_predictions(scored,pred)
summary_primary=mod.metric_summary(comp_primary)
ci_primary=mod.cluster_bootstrap_brier(comp_primary)
print('\nAS-FROZEN PRIMARY')
print(summary_primary.to_string(index=False))
print('primary Brier diff CI',ci_primary)

# Post-hoc sensitivity only: restore A0045 to the original response preserved in rsrc.xlsx,
# keep all Model_B reset outputs and all composition outcomes exactly as collected.
sens=cur.copy()
sens.loc[sens.Run_ID.astype(str)==rowid,'Raw_Response_Verbatim']=old_raw
scored_sens=mod.score_rows(sens)
# Create a counterfactual prediction from the corrected calibration only; label non-confirmatory.
cal_sc=scored_sens[scored_sens.Phase=='CALIBRATION'].copy()
comp_rows=cur[cur.Phase=='COMPOSITION'].copy()
ps=[]
for _,r in comp_rows.iterrows():
    tid=str(r['Task_ID']); model=str(r['Model_Endpoint'])
    sub=cal_sc[(cal_sc.Model_Endpoint.astype(str)==model)&(cal_sc.Task_ID.astype(str)!=tid)]
    p_schema=(float(sub.Schema_Valid.sum())+.5)/(len(sub)+1.0)
    p=p_schema
    for op in [st['node'] for st in r['Expected']['steps']]:
        op_rows=sub[sub.Operation_or_Graph.astype(str)==op]
        valid=op_rows[op_rows.Schema_Valid==1]
        p_op=(float(valid.Exact_Task_Success.sum())+.5)/(len(valid)+1.0)
        p*=p_op
    ps.append({'Run_ID':str(r['Run_ID']),'P_Independence_Law_Sensitivity':max(.001,min(.999,p))})
p_sens=pd.DataFrame(ps)
comp_sens=mod.crossvalidated_predictions(scored_sens,p_sens.rename(columns={'P_Independence_Law_Sensitivity':'P_Independence_Law'}))
summary_sens=mod.metric_summary(comp_sens)
ci_sens=mod.cluster_bootstrap_brier(comp_sens)
print('\nPOST-HOC SENSITIVITY (RESTORE A0045 ONLY; NOT PRIMARY)')
print(summary_sens.to_string(index=False))
print('sensitivity Brier diff CI',ci_sens)
print('A0045 exact score primary vs sensitivity',int(scored.loc[scored.Run_ID.astype(str)==rowid,'Exact_Task_Success'].iloc[0]),int(scored_sens.loc[scored_sens.Run_ID.astype(str)==rowid,'Exact_Task_Success'].iloc[0]))

# How much does A0045 affect the primary probability and proper scores?
P=comp_primary[['Run_ID','Task_ID','Model_Endpoint','Structure','Exact_Task_Success','P_Independence_Law']].merge(p_sens,on='Run_ID',validate='one_to_one')
P['Delta_P_sensitivity_minus_primary']=P['P_Independence_Law_Sensitivity']-P['P_Independence_Law']
P['Affected']=P['Delta_P_sensitivity_minus_primary'].abs()>1e-12
print('rows with product-law prediction changed by restoring A0045:',int(P.Affected.sum()),'of',len(P))
print('affected by model/structure:',P[P.Affected].groupby(['Model_Endpoint','Structure']).size().to_dict())
P.to_csv(OUT/'C.R.O._posthoc_A0045_sensitivity_predictions.csv',index=False)

# Lenient diagnostic: parse any balanced JSON object embedded inside an otherwise invalid response.
def embedded_json_objects(s):
    out=[]; start=None; depth=0; quoted=False; escaped=False
    for i,ch in enumerate(s):
        if start is None:
            if ch=='{': start=i; depth=1; quoted=False; escaped=False
            continue
        if quoted:
            if escaped: escaped=False
            elif ch=='\\': escaped=True
            elif ch=='"': quoted=False
        else:
            if ch=='"': quoted=True
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:
                    chunk=s[start:i+1]
                    try:
                        obj=json.loads(chunk)
                        if isinstance(obj,dict): out.append(obj)
                    except Exception: pass
                    start=None
    return out

by_model=defaultdict(Counter); by_struct=defaultdict(Counter)
for _,r in cur[cur.Phase=='COMPOSITION'].iterrows():
    model=str(r['Model_Endpoint']); st=str(r['Structure']); raw=str(r['Raw_Response_Verbatim'] or '')
    obj_strict, schema = mod.strict_parse(raw)
    expected=json.loads(str(r['Expected_JSON']))
    embedded=[x for x in embedded_json_objects(raw) if set(x.keys())=={'steps','final'} and isinstance(x.get('steps'),list) and all(isinstance(y,dict) and set(y.keys())=={'node','value'} and isinstance(y.get('node'),str) for y in x['steps'])]
    best=embedded[-1] if embedded else None
    valid_exact=bool(best is not None and best==expected)
    c=by_model[model]; c['N']+=1;c['strict_schema']+=int(schema);c['strict_exact']+=int(schema and obj_strict==expected);c['contains_schema_object']+=int(best is not None);c['embedded_exact']+=int(valid_exact)
    cs=by_struct[(model,st)];cs['N']+=1;cs['strict_exact']+=int(schema and obj_strict==expected);cs['embedded_exact']+=int(valid_exact);cs['contains_schema_object']+=int(best is not None)
print('\nLENIENT EMBEDDED-JSON DIAGNOSTIC (EXPLORATORY; NOT PROTOCOL PRIMARY)')
for m,c in sorted(by_model.items()): print(m,dict(c))
for k,c in sorted(by_struct.items()): print(k,dict(c))
