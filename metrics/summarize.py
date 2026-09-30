#!/usr/bin/env python3
"""Calcular métricas apenas a partir de run.json de execuções Jenkins reais."""
import argparse, json, statistics
from pathlib import Path
from datetime import datetime, timezone

def instant(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None: raise ValueError('Data deve ter fuso horário')
    return dt

def summarize(paths, start, end):
    if end <= start: raise ValueError('Janela de observação inválida')
    runs, seen = [], set()
    for path in paths:
        row = json.loads(Path(path).read_text())
        if row.get('schema') != 1 or not row.get('buildUrl') or not row.get('commit'):
            raise ValueError('Artefato run.json inválido')
        if row['buildUrl'] in seen: raise ValueError('Execução duplicada: ' + row['buildUrl'])
        seen.add(row['buildUrl'])
        recorded = instant(row['recordedAt'])
        if not start <= recorded <= end: raise ValueError('Execução fora da janela informada')
        attempted, succeeded, failed = [row.get(k) for k in ('productionAttempted', 'productionSucceeded', 'productionFailed')]
        if not all(type(v) is bool for v in (attempted, succeeded, failed)):
            raise ValueError('Indicadores de produção precisam ser booleanos')
        if succeeded and (not attempted or failed): raise ValueError('Indicadores inconsistentes')
        if failed and not attempted: raise ValueError('Falha de produção sem tentativa')
        if succeeded:
            if not row.get('approver') or not row.get('approvedAt') or '@sha256:' not in row.get('image', ''):
                raise ValueError('Sucesso sem aprovação/digest verificável')
            deployed = instant(row['deployedAt'])
            committed = datetime.fromtimestamp(int(row['commitEpoch']), timezone.utc)
            if deployed < committed: raise ValueError('Deploy anterior ao commit')
            if not committed <= instant(row['approvedAt']) <= deployed: raise ValueError('Aprovação fora da ordem temporal')
            row['leadHours'] = (deployed - committed).total_seconds() / 3600
        runs.append(row)
    if len(runs) < 10: raise ValueError('E6 exige pelo menos 10 execuções Jenkins; há apenas ' + str(len(runs)))
    successes = [r for r in runs if r['productionSucceeded']]
    attempts = [r for r in runs if r['productionAttempted']]
    failures = [r for r in attempts if r['productionFailed']]
    days = (end-start).total_seconds()/86400
    leads = [r['leadHours'] for r in successes]
    average = statistics.mean(leads) if leads else None
    return dict(executions=len(runs), windowStart=start.isoformat(), windowEnd=end.isoformat(),
        successfulDeployments=len(successes), productionAttempts=len(attempts), failedDeployments=len(failures),
        deploymentsPerDay=len(successes)/days,
        changeFailureRatePercent=len(failures)/len(attempts)*100 if attempts else None,
        leadMeanHours=average, leadMedianHours=statistics.median(leads) if leads else None,
        baselineHours=264, targetHours=48,
        improvementPercent=(264-average)/264*100 if average is not None else None,
        targetReached=average <= 48 if average is not None else None,
        note='Falhas de CI são separadas de falhas de mudança em produção. Laboratório não comprova desempenho de dois meses.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory'); parser.add_argument('--start', required=True); parser.add_argument('--end', required=True)
    args=parser.parse_args()
    try:
        result=summarize(sorted(Path(args.directory).rglob('run.json')), instant(args.start), instant(args.end))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, KeyError) as error:
        parser.exit(1, 'Métricas não disponíveis: ' + str(error) + '\n')
