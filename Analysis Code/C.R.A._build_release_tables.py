#!/usr/bin/env python3
"""Rebuild the public aggregate result tables from the private study workbook.

This script writes derived aggregate CSV/JSON files only. It never copies the
workbook or raw model responses into the release directory.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PRIMARY=HERE/"C.R.A._analyze_compositional_reliability_v2.py"
if not PRIMARY.exists():
    PRIMARY=HERE/"C.R.O._analyze_compositional_reliability_v2.py"

def load_primary():
    spec=importlib.util.spec_from_file_location("cra_primary",PRIMARY)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def score(y,p):
    y=np.asarray(y,dtype=float); p=np.clip(np.asarray(p,dtype=float),.001,.999)
    return float(np.mean((p-y)**2)),float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))

def main():
    ap=argparse.ArgumentParser(description="Rebuild aggregate release tables from a private workbook")
    ap.add_argument("workbook",help="Private analyzed workbook; never copied")
    ap.add_argument("--predictions",required=True,help="Selected workbook-matching prediction freeze")
    ap.add_argument("--outdir",default="release_results")
    a=ap.parse_args()
    wb=Path(a.workbook); predpath=Path(a.predictions); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    if not wb.is_file() or not predpath.is_file(): raise SystemExit("Workbook or selected prediction file not found.")
    m=load_primary(); trials,gold,merged=m.read_book(wb); scored=m.score_rows(merged); frozen=pd.read_csv(predpath)
    m.validate_frozen_predictions(merged,scored,frozen)
    comp=m.crossvalidated_predictions(scored,frozen)
    if len(merged)!=336 or len(comp)!=192: raise SystemExit("Unexpected row count; release tables were not written.")
    # Per-operation calibration.
    rows=[]
    for (model,op),g in scored[scored.Phase.eq("CALIBRATION")].groupby(["Model_Endpoint","Operation_or_Graph"],sort=True):
        sn=int(g.Schema_Valid.sum()); es=int(g.loc[g.Schema_Valid.eq(1),"Exact_Task_Success"].sum())
        rows.append(dict(Model=model,Operation=op,Rows=len(g),Schema_Valid_N=sn,Schema_Valid_Rate=sn/len(g),
          Exact_Success_N_AllRows=int(g.Exact_Task_Success.sum()),Exact_Success_Rate_AllRows=float(g.Exact_Task_Success.mean()),
          Exact_Given_Schema_N=es,Exact_Given_Schema_Denominator=sn,
          Exact_Given_Schema_Rate=es/sn if sn else np.nan,Jeffreys_P_Op_Used=(es+.5)/(sn+1)))
    pd.DataFrame(rows).to_csv(out/"calibration_by_operation.csv",index=False)
    # Component outcomes.
    rows=[]
    for model,g in scored[scored.Phase.eq("COMPOSITION")].groupby("Model_Endpoint",sort=True):
        r={"Model":model,"N":len(g)}
        for col,label in [("Schema_Valid","Strict_Schema_Valid"),("Node_Sequence_Correct","Node_Sequence_Correct"),
                          ("Node_Values_Correct","Step_Values_Correct"),("Final_Correct","Final_Correct"),("Exact_Task_Success","Exact_Success")]:
            r[label+"_N"]=int(g[col].sum()); r[label+"_Rate"]=float(g[col].mean())
        rows.append(r)
    pd.DataFrame(rows).to_csv(out/"composition_component_metrics.csv",index=False)
    # Predictors, overall and by endpoint.
    predictors=["P_Independence_Law","P_Structure_BaseRate","P_Count_BaseRate","P_Global_BaseRate","P_GraphCorrected_CV"]
    rows=[]
    for subset,g in [("ALL_MODELS",comp),*list(comp.groupby("Model_Endpoint",sort=True))]:
        y=g.Exact_Task_Success.to_numpy(float)
        for col in predictors:
            b,ll=score(y,g[col].to_numpy(float)); mean=float(np.mean(np.clip(g[col].to_numpy(float),.001,.999)))
            rows.append(dict(Subset=subset,Predictor=col,N=len(g),Brier=b,LogLoss=ll,MeanPredicted=mean,
                             ObservedRate=float(y.mean()),CalibrationGap=mean-float(y.mean())))
    pd.DataFrame(rows).to_csv(out/"predictor_metrics_by_model.csv",index=False)
    # Endpoint x graph-structure metrics.
    rows=[]
    for (model,structure),g in comp.groupby(["Model_Endpoint","Structure"],sort=True):
        y=g.Exact_Task_Success.to_numpy(float)
        r=dict(Model=model,Structure=structure,N=len(g),Exact_Successes=int(y.sum()),
               Exact_Success_Rate=float(y.mean()),Schema_Valid_Rate=float(g.Schema_Valid.mean()),
               Mean_P_Independence=float(g.P_Independence_Law.mean()))
        for col in predictors:
            b,ll=score(y,g[col].to_numpy(float)); r[col+"_Brier"]=b; r[col+"_LogLoss"]=ll
        rows.append(r)
    pd.DataFrame(rows).to_csv(out/"outcomes_and_scores_by_model_structure.csv",index=False)
    # Bootstrap differences; family means are the resampling units.
    rows=[]
    for model,g in [("ALL_MODELS",comp),*list(comp.groupby("Model_Endpoint",sort=True))]:
        fam=[]
        for _,block in g.groupby("Task_ID",sort=True):
            y=block.Exact_Task_Success.to_numpy(float)
            p=block.P_Independence_Law.to_numpy(float); q=block.P_Structure_BaseRate.to_numpy(float)
            fam.append(float(np.mean((p-y)**2)-np.mean((q-y)**2)))
        fam=np.asarray(fam); rng=np.random.default_rng(20261023)
        draws=rng.choice(fam,size=(5000,len(fam)),replace=True).mean(axis=1)
        rows.append(dict(Model=model,Task_Clusters=len(fam),Mean_Brier_Diff_Product_minus_Structure=float(fam.mean()),
          Cluster_Bootstrap_95CI_L=float(np.quantile(draws,.025)),Cluster_Bootstrap_95CI_U=float(np.quantile(draws,.975)),
          Interpretation="Positive means the atom-product law has worse Brier score; negative means it has better Brier score.",
          Bootstrap_Replicates=5000,Seed=20261023))
    pd.DataFrame(rows).to_csv(out/"task_cluster_bootstrap_brier_diff.csv",index=False)
    integrity=dict(source_workbook_public=False,source_workbook_sha256=digest(wb),trial_rows=len(trials),gold_rows=len(gold),
      unique_trial_run_ids=int(trials.Run_ID.astype(str).nunique()),unique_gold_run_ids=int(gold.Run_ID.astype(str).nunique()),
      missing_raw_responses=int(merged.Raw_Response_Verbatim.fillna("").astype(str).str.strip().eq("").sum()),
      phase_counts={str(k):int(v) for k,v in merged.Phase.value_counts().sort_index().items()},
      model_counts={str(k):int(v) for k,v in merged.Model_Endpoint.value_counts().sort_index().items()},
      frozen_rows=len(frozen),frozen_sha256=digest(predpath),frozen_predictions_recomputed_from_calibration=True,
      row_level_run_timestamp_and_exact_model_version_columns_present=("Run_Date_Time" in merged.columns and "Exact_Model_Version" in merged.columns),
      composition_exact_successes=int(comp.Exact_Task_Success.sum()),composition_exact_success_rate=float(comp.Exact_Task_Success.mean()))
    (out/"integrity_checks.json").write_text(json.dumps(integrity,indent=2)+"\n",encoding="utf-8")
    print("Generated five aggregate CSV tables and integrity_checks.json.")
    print("Workbook SHA-256 (private input):",digest(wb))
    print("Selected freeze SHA-256:",digest(predpath))
    print("Composition exact successes:",int(comp.Exact_Task_Success.sum()),"/",len(comp))
    print("Atom-product Brier:",f"{score(comp.Exact_Task_Success,comp.P_Independence_Law)[0]:.6f}")

if __name__=="__main__": main()
