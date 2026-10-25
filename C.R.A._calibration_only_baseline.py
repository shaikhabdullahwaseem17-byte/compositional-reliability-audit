"""Reproduce a calibration-only homogeneous-operation count baseline.
Researcher: Shaikh Abdullah Waseem. CLI/path adjustments only; estimator preserved.

For each composition run, exclude its Task_ID family from calibration data.
Estimate P(schema-valid) from all remaining calibration rows for the same
endpoint alias. Estimate one pooled q from schema-valid atomic calibration rows
for that endpoint, then predict P(exact composition success) = P(schema-valid)*q**m,
where m is the oracle-defined number of active operation nodes.
This baseline uses no composition outcomes. It is an exploratory, post-audit
comparison, not a preregistered primary predictor.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser(description="Calibration-only pooled-operation comparison")
ap.add_argument("--analysis-dir", default="C.R.O._analysis_output", help="Output directory created by the primary analysis script")
ap.add_argument("--predictions", default="C.R.O._Frozen_Predictions_workbook_matching.csv")
ap.add_argument("--outdir", default="C.R.O._calibration_only_results")
args = ap.parse_args()
ANALYSIS = Path(args.analysis_dir)
OUT = Path(args.outdir); OUT.mkdir(parents=True, exist_ok=True)
scored = pd.read_csv(ANALYSIS / 'scored_all_runs.csv')
comp = pd.read_csv(ANALYSIS / 'composition_predictions_and_outcomes.csv')
freeze = pd.read_csv(args.predictions)

# The official composition table is the audited row-level outcome source.
# P_JSON is carried from the selected frozen prediction file.
x = comp.drop(columns=['P_Independence_Law'], errors='ignore').merge(
    freeze[['Run_ID', 'P_JSON', 'P_Independence_Law']],
    on='Run_ID', how='left', validate='one_to_one'
)
if len(x) != 192 or x['P_JSON'].isna().any():
    raise RuntimeError('Composition/freeze join failed or incomplete')
x['Node_Count'] = x['Expected_Node_Sequence'].fillna('').apply(
    lambda s: 0 if not str(s).strip() else len(str(s).split(' > '))
)
cal = scored[scored['Phase'].eq('CALIBRATION')].copy()

def jeffreys(successes, n):
    return (float(successes) + 0.5) / (float(n) + 1.0)

pred = []
for _, r in x.iterrows():
    sub_all = cal[(cal['Model_Endpoint'] == r['Model_Endpoint']) & (cal['Task_ID'] != r['Task_ID'])]
    sub_valid = sub_all[sub_all['Schema_Valid'].eq(1)]
    # q pools atomic operation successes conditional on strict schema validity.
    q = jeffreys(int(sub_valid['Exact_Task_Success'].sum()), len(sub_valid))
    p_schema = float(r['P_JSON'])
    p = p_schema * (q ** int(r['Node_Count']))
    pred.append((p_schema, q, p, len(sub_all), len(sub_valid)))
x[['P_Schema_From_Freeze', 'Q_Pooled_Atomic', 'P_Calibration_PooledOp_Count',
   'Calibration_Rows_Excluding_Family', 'Schema_Valid_Calibration_Rows_Excluding_Family']] = pd.DataFrame(pred, index=x.index)

rows=[]
for subset, g in [('ALL_MODELS', x), *[(m, g) for m, g in x.groupby('Model_Endpoint', sort=True)]]:
    y = g['Exact_Task_Success'].astype(float).to_numpy()
    for name, col in [('Atom-product law', 'P_Independence_Law'),
                      ('Calibration-only pooled-operation count', 'P_Calibration_PooledOp_Count')]:
        p = np.clip(g[col].astype(float).to_numpy(), 0.001, 0.999)
        rows.append({
            'Subset': subset, 'Predictor': name, 'N': len(g),
            'Brier': float(np.mean((p-y)**2)),
            'LogLoss': float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p))),
            'MeanPredicted': float(np.mean(p)), 'ObservedRate': float(np.mean(y)),
            'CalibrationGap': float(np.mean(p)-np.mean(y))
        })
metrics = pd.DataFrame(rows)
metrics.to_csv(OUT / 'C.R.O._calibration_only_baseline_metrics.csv', index=False)
x.to_csv(OUT / 'C.R.O._calibration_only_baseline_predictions.csv', index=False)
# Cluster bootstrap over the 12 Task_ID families, preserving all rows within a family.
x['BrierDiff_ProductMinusCalibrationOnly'] = (
    (x['P_Independence_Law'] - x['Exact_Task_Success'])**2
    - (x['P_Calibration_PooledOp_Count'] - x['Exact_Task_Success'])**2
)
fam = x.groupby('Task_ID', sort=True)['BrierDiff_ProductMinusCalibrationOnly'].mean().to_numpy()
rng = np.random.default_rng(20261025)
draws = rng.choice(fam, size=(100000, len(fam)), replace=True).mean(axis=1)
boot = pd.DataFrame([{
    'N_Task_Families': len(fam),
    'Mean_Brier_Difference_Product_Minus_CalibrationOnly': float(fam.mean()),
    'CI95_Lower': float(np.quantile(draws, .025)),
    'CI95_Upper': float(np.quantile(draws, .975)),
    'Bootstrap_Replicates': 100000,
    'Seed': 20261025,
    'Interpretation': 'Negative favors atom-product law; interval including zero means no clear difference.'
}])
boot.to_csv(OUT / 'C.R.O._calibration_only_baseline_bootstrap.csv', index=False)
print(metrics.to_string(index=False))
print('\nCluster bootstrap:')
print(boot.to_string(index=False))
