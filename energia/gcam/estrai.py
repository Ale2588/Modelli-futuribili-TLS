"""
Estrae da un'uscita di GCAM (debug_db.xml, scritto senza Java) gli indicatori usati dalla domanda 01.
Uso: python3 estrai.py debug_db.xml hector-outputstream.csv uscita.json

Il file è indentato con un elemento per riga: lo legge riga per riga tenendo solo il contesto
(regione, settore, sottosettore), così la memoria resta minima anche con file da diversi GB.
"""
import json, sys, csv, re
from collections import defaultdict

ANNI = list(range(2025, 2101, 5))
SETTORI_COSTO = {'electricity', 'elect_td_bld', 'elect_td_ind', 'H2 central production', 'refining'}
SETTORI_OUTPUT = {'iron and steel', 'aluminum', 'ammonia', 'cement', 'elect_td_bld', 'elect_td_ind', 'elect_td_trn', 'H2 central production'}
BENI = {'crude oil', 'natural gas', 'coal', 'regional oil'}
RX_TAG = re.compile(r'<([A-Za-z0-9_-]+)')
RX_NAME = re.compile(r'name="([^"]*)"')
RX_YEAR = re.compile(r'(?:year|vintage)="(\d+)"')
RX_VAL = re.compile(r'>([^<]*)<')

def dd():
    return defaultdict(float)

def nuova_regione():
    return {'costo': defaultdict(dict), 'elettricita': defaultdict(dd), 'settori': defaultdict(dd),
            'co2': dd(), 'desal': dd(), 'petrolio': dd(), 'cropland': dd()}

def estrai(path):
    reg = defaultdict(nuova_regione)
    mercati = defaultdict(dict)
    r = ss = sub = res = None
    in_co2 = in_out = in_ag = False
    mk = None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.lstrip()
            if s.startswith('</'):
                if s.startswith('</region'): r = None
                elif s.startswith('</supplysector'): ss = None; sub = None
                elif s.startswith('</subsector'): sub = None
                elif s.startswith(('</resource', '</renewresource', '</unlimited-resource')): res = None
                elif s.startswith('</CO2>'): in_co2 = False
                elif s.startswith('</output-primary'): in_out = False
                elif s.startswith('</AgProductionTechnology'): in_ag = False
                elif s.startswith('</market>'): mk = None
                continue
            m = RX_TAG.match(s)
            if not m:
                continue
            t = m.group(1)
            if t == 'market':
                mk = {'y': int(RX_YEAR.search(s).group(1))}
                continue
            if mk is not None:
                if t in ('MarketGoodOrFuel', 'MarketRegion', 'price', 'supply'):
                    v = RX_VAL.search(s).group(1).strip()
                    mk[t] = v
                    if t == 'supply' and mk.get('MarketGoodOrFuel') in BENI:
                        try:
                            mercati[mk['MarketGoodOrFuel'] + '|' + mk.get('MarketRegion', '')][mk['y']] = {'prezzo': float(mk.get('price', 'nan')), 'offerta': float(v)}
                        except ValueError:
                            pass
                continue
            if t == 'region':
                r = RX_NAME.search(s).group(1); continue
            if r is None:
                continue
            if t == 'supplysector':
                ss = RX_NAME.search(s).group(1); sub = None
            elif t == 'subsector':
                sub = RX_NAME.search(s).group(1)
            elif t in ('resource', 'renewresource', 'unlimited-resource'):
                res = RX_NAME.search(s).group(1)
            elif t == 'CO2':
                n = RX_NAME.search(s); in_co2 = bool(n and n.group(1) == 'CO2')
            elif t == 'output-primary':
                in_out = True
            elif t == 'AgProductionTechnology':
                in_ag = True
            elif t == 'cost':
                if ss in SETTORI_COSTO and sub is None:
                    y = RX_YEAR.search(s)
                    if y: reg[r]['costo'][ss][int(y.group(1))] = float(RX_VAL.search(s).group(1))
            elif t == 'physical-output':
                y = RX_YEAR.search(s)
                if not y: continue
                y = int(y.group(1)); v = float(RX_VAL.search(s).group(1))
                if res in ('crude oil', 'unconventional oil') and ss is None:
                    reg[r]['petrolio'][y] += v
                elif in_out and ss:
                    if ss == 'electricity' and sub:
                        reg[r]['elettricita'][sub][y] += v
                    elif ss.endswith('_desalinated water'):
                        reg[r]['desal'][y] += v
                    if ss in SETTORI_OUTPUT:
                        reg[r]['settori'][ss][y] += v
            elif t == 'emissions':
                if in_co2:
                    y = RX_YEAR.search(s)
                    if y: reg[r]['co2'][int(y.group(1))] += float(RX_VAL.search(s).group(1))
            elif t == 'land-allocation':
                if in_ag:
                    y = RX_YEAR.search(s)
                    if y: reg[r]['cropland'][int(y.group(1))] += float(RX_VAL.search(s).group(1))
    return reg, mercati

def temperatura(path_csv):
    t = {}
    with open(path_csv) as f:
        righe = (x for x in f if not x.startswith('#'))
        for x in csv.DictReader(righe):
            if x['spinup'] == '0' and x['variable'] == 'global_tas':
                y = int(float(x['year']))
                if y in ANNI:
                    t[y] = float(x['value'])
    return t

def serializza(reg, mercati, temp):
    out = {'anni': ANNI, 'regioni': {}, 'mercati': {}, 'temperatura': [temp.get(y) for y in ANNI]}
    for r, d in reg.items():
        out['regioni'][r] = {
            'costo': {s: [d['costo'][s].get(y) for y in ANNI] for s in d['costo']},
            'elettricita': {s: [round(d['elettricita'][s].get(y, 0), 5) for y in ANNI] for s in d['elettricita']},
            'settori': {s: [round(d['settori'][s].get(y, 0), 5) for y in ANNI] for s in d['settori']},
            **{k: [round(d[k].get(y, 0), 5) for y in ANNI] for k in ('co2', 'desal', 'petrolio', 'cropland')}
        }
    for m, v in mercati.items():
        out['mercati'][m] = [v.get(y) for y in ANNI]
    return out

if __name__ == '__main__':
    reg, mer = estrai(sys.argv[1])
    temp = temperatura(sys.argv[2])
    json.dump(serializza(reg, mer, temp), open(sys.argv[3], 'w'))
    print('regioni', len(reg), 'mercati', len(mer), 'temperatura', len(temp))
