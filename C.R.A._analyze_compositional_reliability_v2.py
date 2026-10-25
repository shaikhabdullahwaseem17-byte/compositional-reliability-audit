#!/usr/bin/env python3
"""
Analysis pipeline for the Compositional AI Reliability Law study.
Researcher: Shaikh Abdullah Waseem. Attribution added for this reproduction copy; analysis logic preserved.
Requires: pandas, openpyxl, numpy, scikit-learn.
Usage:
  python analyze_compositional_reliability.py WORKBOOK.xlsx --phase freeze
  [archive Frozen_Predictions.csv before running composition trials]
  python analyze_compositional_reliability.py WORKBOOK.xlsx --phase analyze --predictions Frozen_Predictions.csv

The script never fabricates missing data and never edits the workbook.
"""
import argparse, json, math, hashlib, csv, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss

OPS = ["FILTER_CHAR","SORT_ALPHA","UPPERCASE_ITEMS","REVERSE_LIST","COUNT_MATCH_GE_THRESHOLD","IS_EVEN_LENGTH"]

def strict_parse(raw):
    if raw is None or (isinstance(raw,float) and np.isnan(raw)): return None, False
    s = str(raw).strip()
    if not s: return None, False
    try:
        obj=json.loads(s)
    except Exception:
        return None, False
    if not isinstance(obj,dict) or set(obj.keys()) != {"steps","final"}: return obj, False
    if not isinstance(obj.get("steps"),list): return obj, False
    for st in obj["steps"]:
        if not isinstance(st,dict) or set(st.keys()) != {"node","value"} or not isinstance(st.get("node"),str):
            return obj, False
    return obj, True

def equal_json(a,b):
    # Python equality handles lists and dictionaries; dictionary key ordering is irrelevant.
    return a == b

def jeffreys(successes, n):
    return (float(successes)+0.5)/(float(n)+1.0)

def read_book(path):
    xl=pd.ExcelFile(path)
    trials=pd.read_excel(path,sheet_name="Trial_Data",dtype=object)
    gold=pd.read_excel(path,sheet_name="Gold_Oracle",dtype=object)
    # Ensure IDs are strings (spreadsheet tools sometimes infer unexpected types).
    for df in (trials,gold):
        df["Run_ID"]=df["Run_ID"].astype(str).str.strip()
        df["Task_ID"]=df["Task_ID"].astype(str).str.strip()
    merged=trials.merge(gold, on=["Run_ID","Phase","Task_ID","Model_Endpoint"], how="left", validate="one_to_one")
    if merged["Expected_JSON"].isna().any():
        bad=merged.loc[merged["Expected_JSON"].isna(),"Run_ID"].head(10).tolist()
        raise ValueError(f"Gold oracle missing for run IDs: {bad}")
    merged["Expected"] = merged["Expected_JSON"].apply(lambda x: json.loads(str(x)))
    return trials, gold, merged

def score_rows(merged):
    scored=[]
    for _,r in merged.iterrows():
        parsed, schema = strict_parse(r.get("Raw_Response_Verbatim",""))
        gold=r["Expected"]
        exp_steps=gold["steps"]
        actual_steps=parsed.get("steps",[]) if isinstance(parsed,dict) and isinstance(parsed.get("steps"),list) else []
        seq_correct = schema and [s.get("node") for s in actual_steps] == [s["node"] for s in exp_steps]
        values_correct = schema and seq_correct and all(equal_json(a.get("value"), e["value"]) for a,e in zip(actual_steps,exp_steps))
        final_correct = schema and equal_json(parsed.get("final"), gold["final"])
        exact = bool(schema and seq_correct and values_correct and final_correct)
        # For each atomic record, operation success is conditional on a schema-valid response.
        op = str(r.get("Operation_or_Graph",""))
        atomic_op_correct = None
        if str(r.get("Phase","")) == "CALIBRATION" and schema:
            atomic_op_correct = bool(exact)
        scored.append({
            "Run_ID":r["Run_ID"],"Phase":r["Phase"],"Queue_Order":r.get("Queue_Order"),
            "Task_ID":r["Task_ID"],"Structure":r["Structure"],"Replicate":r.get("Replicate"),
            "Model_Endpoint":r["Model_Endpoint"],"Operation_or_Graph":op,
            "Schema_Valid":int(schema),"Node_Sequence_Correct":int(bool(seq_correct)),
            "Node_Values_Correct":int(bool(values_correct)),"Final_Correct":int(bool(final_correct)),
            "Exact_Task_Success":int(exact),"Atomic_Operation_Correct_If_SchemaValid":atomic_op_correct,
            "Raw_Response_Verbatim":r.get("Raw_Response_Verbatim",""),"Expected_Node_Sequence":r.get("Expected_Node_Sequence",""),
            "Expected_Final_JSON":r.get("Expected_Final_JSON",""),"Notes":r.get("Notes","")
        })
    return pd.DataFrame(scored)

def frozen_predictions(merged, scored):
    cal=merged[merged["Phase"]=="CALIBRATION"].copy()
    comp=merged[merged["Phase"]=="COMPOSITION"].copy()
    comp_sc=scored[scored["Phase"]=="COMPOSITION"].set_index("Run_ID")
    # Strict requirements: no composition responses may exist yet and every calibration row must have a response.
    if comp["Raw_Response_Verbatim"].fillna("").astype(str).str.strip().ne("").any():
        raise ValueError("Freeze blocked: at least one composition raw-output cell is already filled. Predictions must be frozen before composition outputs are collected.")
    missing=cal["Raw_Response_Verbatim"].fillna("").astype(str).str.strip().eq("")
    if missing.any():
        examples=cal.loc[missing,"Run_ID"].head(12).tolist()
        raise ValueError(f"Freeze blocked: {int(missing.sum())} calibration responses missing. Examples: {examples}")
    # Need a fully scored calibration set for every endpoint / operation type.
    cal_sc=scored[scored["Phase"]=="CALIBRATION"].copy()
    predictions=[]
    for _,cr in comp.iterrows():
        target_task=str(cr["Task_ID"]); model=str(cr["Model_Endpoint"])
        # Exclude the entire target task family from all atomic calibration.
        sub_cal=cal_sc[(cal_sc["Model_Endpoint"].astype(str)==model) & (cal_sc["Task_ID"].astype(str)!=target_task)]
        if len(sub_cal)==0:
            raise ValueError(f"No calibration data to estimate probabilities for {cr['Run_ID']}")
        p_schema=jeffreys(sub_cal["Schema_Valid"].sum(),len(sub_cal))
        expected=cr["Expected"]
        p_ops={}
        used_nodes=[st["node"] for st in expected["steps"]]
        for op in set(used_nodes):
            op_rows=sub_cal[(sub_cal["Operation_or_Graph"].astype(str)==op)]
            # The score is conditional on schema-valid calibration outputs.
            valid=op_rows[op_rows["Schema_Valid"]==1]
            n=len(valid)
            s=int(valid["Exact_Task_Success"].sum())
            p_ops[op]=jeffreys(s,n)
        p_ind=p_schema
        for op in used_nodes:
            p_ind *= p_ops[op]
        predictions.append({
            "Run_ID":cr["Run_ID"],"Task_ID":target_task,"Model_Endpoint":model,
            "Structure":cr["Structure"],"Replicate":cr["Replicate"],
            "P_JSON":p_schema,"Active_Node_Sequence":" > ".join(used_nodes),
            "P_Independence_Law":float(np.clip(p_ind,0.001,0.999)),
            "Node_Types_Used":" | ".join(used_nodes),
            "Calibration_Task_Families":int(sub_cal["Task_ID"].nunique()),
            "Calibration_Rows":int(len(sub_cal)),
            "Prediction_Frozen_UTC":datetime.now(timezone.utc).isoformat(timespec="seconds")
        })
    return pd.DataFrame(predictions)

def logit(p):
    p=np.clip(np.asarray(p,dtype=float),0.001,0.999)
    return np.log(p/(1-p))

def crossvalidated_predictions(scored, frozen):
    comp=scored[scored["Phase"]=="COMPOSITION"].merge(frozen[["Run_ID","P_Independence_Law"]],on="Run_ID",how="left",validate="one_to_one")
    if comp["P_Independence_Law"].isna().any():
        raise ValueError("Frozen prediction file is missing composition Run_ID rows.")
    # Out-of-template structure-specific baseline and count-only baseline.
    gold_counts = comp.groupby("Run_ID")["Expected_Node_Sequence"].first()
    # Node count from sequence field; nodes not containing " > " count as one.
    comp["Expected_Node_Count"] = comp["Expected_Node_Sequence"].fillna("").apply(lambda x: 0 if not str(x).strip() else len(str(x).split(" > ")))
    comp["P_Structure_BaseRate"] = np.nan
    comp["P_Count_BaseRate"] = np.nan
    comp["P_Global_BaseRate"] = np.nan
    comp["P_GraphCorrected_CV"] = np.nan
    for heldout in comp["Task_ID"].unique():
        train=comp[comp["Task_ID"]!=heldout].copy()
        test_idx=comp.index[comp["Task_ID"]==heldout]
        for idx in test_idx:
            r=comp.loc[idx]
            tr=train[(train["Model_Endpoint"]==r["Model_Endpoint"]) & (train["Structure"]==r["Structure"])]
            comp.loc[idx,"P_Structure_BaseRate"]=jeffreys(tr["Exact_Task_Success"].sum(),len(tr))
            trc=train[(train["Model_Endpoint"]==r["Model_Endpoint"]) & (train["Expected_Node_Count"]==r["Expected_Node_Count"])]
            comp.loc[idx,"P_Count_BaseRate"]=jeffreys(trc["Exact_Task_Success"].sum(),len(trc)) if len(trc)>0 else jeffreys(train["Exact_Task_Success"].sum(),len(train))
            trg=train[train["Model_Endpoint"]==r["Model_Endpoint"]]
            comp.loc[idx,"P_Global_BaseRate"]=jeffreys(trg["Exact_Task_Success"].sum(),len(trg))
        # Graph-corrected predictor: train only on other input families.
        # Features are pre-specified: logit(P_ind), operation-node count, graph structure, and endpoint.
        train_idx=comp.index[comp["Task_ID"]!=heldout]
        test_idx2=comp.index[comp["Task_ID"]==heldout]
        train2=comp.loc[train_idx].copy()
        test2=comp.loc[test_idx2].copy()
        if len(train2)>20 and train2["Exact_Task_Success"].nunique()>1:
            Xtr=pd.concat([
                pd.DataFrame({"logit_pind":logit(train2["P_Independence_Law"].values),"node_count":train2["Expected_Node_Count"].values},index=train2.index),
                pd.get_dummies(train2["Structure"],prefix="structure",dtype=float),
                pd.get_dummies(train2["Model_Endpoint"],prefix="model",dtype=float)
            ],axis=1).fillna(0)
            Xte=pd.concat([
                pd.DataFrame({"logit_pind":logit(test2["P_Independence_Law"].values),"node_count":test2["Expected_Node_Count"].values},index=test2.index),
                pd.get_dummies(test2["Structure"],prefix="structure",dtype=float),
                pd.get_dummies(test2["Model_Endpoint"],prefix="model",dtype=float)
            ],axis=1).fillna(0)
            Xtr,Xte=Xtr.align(Xte,join="left",axis=1,fill_value=0)
            try:
                clf=LogisticRegression(C=1.0,max_iter=2000,solver="liblinear",random_state=20261023)
                clf.fit(Xtr,train2["Exact_Task_Success"].astype(int))
                pred=clf.predict_proba(Xte)[:,1]
                comp.loc[test_idx2,"P_GraphCorrected_CV"]=np.clip(pred,0.001,0.999)
            except Exception:
                pass
    return comp

def metric_summary(comp):
    out=[]
    y=comp["Exact_Task_Success"].astype(float).to_numpy()
    predictor_cols=["P_Independence_Law","P_Structure_BaseRate","P_Count_BaseRate","P_Global_BaseRate","P_GraphCorrected_CV"]
    for col in predictor_cols:
        p=comp[col].astype(float).to_numpy()
        mask=np.isfinite(p)&np.isfinite(y)
        if mask.sum()==0: continue
        yp=y[mask]; pp=np.clip(p[mask],0.001,0.999)
        out.append({"Predictor":col,"N":int(mask.sum()),"Brier":float(np.mean((pp-yp)**2)),
                    "LogLoss":float(-np.mean(yp*np.log(pp)+(1-yp)*np.log(1-pp))),
                    "MeanPredicted":float(np.mean(pp)),"ObservedRate":float(np.mean(yp))})
    return pd.DataFrame(out)

def cluster_bootstrap_brier(comp, n_boot=5000, seed=20261023):
    """Fast cluster bootstrap: resample whole Task_ID groups, not individual rows."""
    rng=np.random.default_rng(seed)
    task_losses=[]
    for tid, block in comp.groupby("Task_ID", sort=True):
        y=block["Exact_Task_Success"].astype(float).to_numpy()
        p1=np.clip(block["P_Independence_Law"].astype(float).to_numpy(),0.001,0.999)
        p0=np.clip(block["P_Structure_BaseRate"].astype(float).to_numpy(),0.001,0.999)
        task_losses.append(float(np.mean((p1-y)**2)-np.mean((p0-y)**2)))
    task_losses=np.asarray(task_losses,dtype=float)
    if len(task_losses)<2:
        return float("nan"),float("nan"),float("nan")
    # The planned design is balanced: each Task_ID contributes the same number of composition rows.
    # Sampling task-level loss differences is therefore equivalent to resampling intact task clusters.
    draws=rng.choice(task_losses,size=(n_boot,len(task_losses)),replace=True).mean(axis=1)
    return float(np.quantile(draws,.025)),float(np.quantile(draws,.975)),float(np.mean(task_losses))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("workbook")
    ap.add_argument("--phase",choices=["freeze","analyze"],required=True)
    ap.add_argument("--predictions",default="Frozen_Predictions.csv")
    ap.add_argument("--outdir",default="reliability_analysis_output")
    args=ap.parse_args()
    outdir=Path(args.outdir); outdir.mkdir(parents=True,exist_ok=True)
    _,_,merged=read_book(args.workbook)
    scored=score_rows(merged)
    if args.phase=="freeze":
        # If audit metadata columns are present, validate them. If they were removed,
        # continue but explicitly warn that row-level source/timing cannot be audited.
        cal_meta=merged[merged["Phase"]=="CALIBRATION"].copy()
        if "Run_Date_Time" in cal_meta.columns and "Exact_Model_Version" in cal_meta.columns:
            for col in ["Run_Date_Time", "Exact_Model_Version"]:
                bad=cal_meta[col].isna() | cal_meta[col].astype(str).str.strip().eq("")
                if bad.any():
                    raise SystemExit(f"Freeze blocked: {int(bad.sum())} calibration rows lack {col}.")
            for endpoint, block in cal_meta.groupby("Model_Endpoint"):
                versions=block["Exact_Model_Version"].astype(str).str.strip().unique()
                if len(versions)!=1:
                    raise SystemExit(f"Freeze blocked: endpoint {endpoint} has inconsistent Exact_Model_Version entries: {versions.tolist()}")
        else:
            print("WARNING: Run_Date_Time and/or Exact_Model_Version columns are absent. Predictions can be frozen, but row-level timing/source auditing is unavailable; disclose this limitation.")
        preds=frozen_predictions(merged,scored)
        out=Path(args.predictions)
        preds.to_csv(out,index=False)
        digest=hashlib.sha256(out.read_bytes()).hexdigest()
        freeze_time=datetime.now(timezone.utc).isoformat(timespec='seconds')
        meta=out.with_suffix(".sha256.txt")
        meta.write_text(f"Prediction file: {out.name}\nSHA-256: {digest}\nFrozen UTC: {freeze_time}\n"
                        f"Rows: {len(preds)}\nThis file must be archived before composition collection.\n",encoding="utf-8")
        print(f"FROZEN {len(preds)} composition predictions to {out}")
        print(f"SHA-256: {digest}")
        print(f"Frozen UTC: {freeze_time}")
        print(f"Metadata: {meta}")
        return
    pred_path=Path(args.predictions)
    if not pred_path.exists():
        raise SystemExit("Frozen prediction file not found. Run --phase freeze before composition collection.")
    sidecar=pred_path.with_suffix(".sha256.txt")
    if not sidecar.exists():
        raise SystemExit(f"Prediction integrity sidecar not found: {sidecar}. Do not analyse without the frozen-file digest.")
    sidecar_text=sidecar.read_text(encoding="utf-8")
    declared=None
    for line in sidecar_text.splitlines():
        if line.startswith("SHA-256:"):
            declared=line.split(":",1)[1].strip()
            break
    actual=hashlib.sha256(pred_path.read_bytes()).hexdigest()
    if not declared or declared != actual:
        raise SystemExit("Frozen prediction hash does not match its SHA-256 sidecar. The prediction file may have changed.")
    frozen=pd.read_csv(pred_path)
    # Validate row-level source/timing only when both metadata columns exist.
    metadata_auditable = ("Run_Date_Time" in merged.columns and "Exact_Model_Version" in merged.columns)
    if metadata_auditable:
        for phase_name in ["CALIBRATION", "COMPOSITION"]:
            block=merged[merged["Phase"]==phase_name].copy()
            for col in ["Run_Date_Time", "Exact_Model_Version"]:
                bad=block[col].isna() | block[col].astype(str).str.strip().eq("")
                if bad.any():
                    raise SystemExit(f"Analysis blocked: {int(bad.sum())} {phase_name} rows lack {col}.")
            for endpoint, eblock in block.groupby("Model_Endpoint"):
                versions=eblock["Exact_Model_Version"].astype(str).str.strip().unique()
                if len(versions)!=1:
                    raise SystemExit(f"Analysis blocked: endpoint {endpoint} has inconsistent model/version labels: {versions.tolist()}")
        # The sidecar freezes a UTC timestamp. Composition rows must be after it.
        frozen_utc=None
        for line in sidecar_text.splitlines():
            if line.startswith("Frozen UTC:"):
                frozen_utc=line[len("Frozen UTC:"):].strip()
                break
        if not frozen_utc:
            raise SystemExit("Frozen UTC timestamp missing from prediction sidecar.")
        freeze_dt=pd.to_datetime(frozen_utc,utc=True,errors="coerce")
        comp_rows_time=merged[merged["Phase"]=="COMPOSITION"].copy()
        comp_times=pd.to_datetime(comp_rows_time["Run_Date_Time"],utc=True,errors="coerce")
        if pd.isna(freeze_dt) or comp_times.isna().any():
            raise SystemExit("Analysis blocked: freeze or run timestamps are not parseable. Use ISO 8601 timestamps with timezone offsets.")
        if not (comp_times > freeze_dt).all():
            raise SystemExit("Analysis blocked: one or more composition timestamps are not strictly after the frozen-prediction timestamp.")
    else:
        print("WARNING: row-level timestamp/model-version audit skipped because metadata columns are absent. Report this limitation; the freeze sidecar still records when predictions were frozen.")
    # Check every composition run has an archived prediction.
    comp_ids=set(merged.loc[merged["Phase"]=="COMPOSITION","Run_ID"].astype(str))
    pred_ids=set(frozen["Run_ID"].astype(str))
    if comp_ids != pred_ids:
        missing=sorted(comp_ids-pred_ids)[:10]; extra=sorted(pred_ids-comp_ids)[:10]
        raise SystemExit(f"Prediction row IDs do not exactly match the workbook. Missing={missing}; extra={extra}")
    scored.to_csv(outdir/"scored_all_runs.csv",index=False)
    comp = crossvalidated_predictions(scored, frozen)
    comp.to_csv(outdir/"composition_predictions_and_outcomes.csv",index=False)
    summary=metric_summary(comp)
    summary.to_csv(outdir/"prediction_metric_summary.csv",index=False)
    ci_lo,ci_hi,mean_diff=cluster_bootstrap_brier(comp)
    report=[]
    report.append("COMPOSITIONAL AI RELIABILITY LAW — ANALYSIS REPORT")
    report.append("No result should be reported until data collection and manual audit are complete.")
    report.append(f"Generated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    report.append(f"Planned workbook rows: {len(merged)}")
    report.append(f"Rows with raw outputs: {int(merged['Raw_Response_Verbatim'].fillna('').astype(str).str.strip().ne('').sum())}")
    report.append(f"Exact task success among composition rows: {comp['Exact_Task_Success'].mean():.4f}")
    report.append("\nPredictive score comparison (lower is better):")
    report.append(summary.to_string(index=False))
    report.append(f"\nTask_ID-cluster bootstrap for Brier difference (product law minus structure-specific baseline): mean={mean_diff:.5f}, 95% percentile CI=[{ci_lo:.5f}, {ci_hi:.5f}]")
    report.append("\nSuccess by graph structure:")
    report.append(comp.groupby(["Model_Endpoint","Structure"])["Exact_Task_Success"].agg(["mean","count"]).to_string())
    report.append("\nSchema validity by graph structure:")
    report.append(comp.groupby(["Model_Endpoint","Structure"])["Schema_Valid"].agg(["mean","count"]).to_string())
    report.append("\nInterpretation guardrails:")
    report.append("- Negative Brier difference favours the atom-product law; positive values mean the structure-specific baseline scored better.")
    report.append("- Intervals resample only 12 task families and may be wide. Do not call the result universal.")
    if not ("Run_Date_Time" in merged.columns and "Exact_Model_Version" in merged.columns):
        report.append("- Row-level run timestamps/model-version labels were not retained in the workbook; the timing/source audit is limited. The calibration substitution note must be disclosed.")
    report.append("- Audit at least 10% of scores and reconcile all code/parser issues before writing conclusions.")
    report_path=outdir/"analysis_report.txt"
    report_path.write_text("\n".join(report),encoding="utf-8")
    print("\n".join(report))
    print(f"\nDetailed output: {outdir}")

if __name__=="__main__":
    main()
