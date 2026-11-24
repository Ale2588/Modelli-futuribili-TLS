"""
Riassume i risultati GCAM estratti (risultati/*.json) in un file leggero per la pagina: energia/gcam-dati.js.
Uso: python3 sintesi.py
"""
import json, os

QUI = os.path.dirname(os.path.abspath(__file__))
RIS = os.path.join(QUI, 'risultati')
SCENARI = [('riferimento', 1), ('energia_3x', 3), ('energia_10x', 10), ('energia_30x', 30), ('energia_100x', 100)]
REGIONI = [('EU-15', 'Europa occidentale (con l\'Italia)'), ('USA', 'Stati Uniti'), ('China', 'Cina'), ('India', 'India'),
           ('Middle East', 'Medio Oriente'), ('Russia', 'Russia'), ('Africa_Western', 'Africa occidentale'), ('Brazil', 'Brasile')]
FONTI = {'coal': 'Carbone', 'gas': 'Gas', 'refined liquids': 'Petrolio', 'nuclear': 'Nuova fonte e nucleare', 'solar': 'Solare',
         'wind': 'Eolico', 'hydro': 'Idroelettrico', 'biomass': 'Biomasse', 'geothermal': 'Geotermico'}
MTC_A_GTCO2 = 3.667 / 1000

def somma(serie):
    return [sum(x) for x in zip(*serie)] if serie else []

def media_pesata(valori, pesi):
    out = []
    for t in range(len(valori[0])):
        num = sum(v[t] * p[t] for v, p in zip(valori, pesi) if v[t] is not None)
        den = sum(p[t] for v, p in zip(valori, pesi) if v[t] is not None)
        out.append(num / den if den else None)
    return out

def riassumi(d):
    R = d['regioni']
    gen = {}
    for r in R.values():
        for s, ser in r['elettricita'].items():
            gen.setdefault(s, []).append(ser)
    gen = {FONTI.get(s, s): [round(x, 2) for x in somma(v)] for s, v in gen.items()}
    pesi = [somma(list(r['elettricita'].values())) for r in R.values()]
    costo_ingrosso = media_pesata([r['costo'].get('electricity', [None] * len(d['anni'])) for r in R.values()], pesi)
    costo_casa = media_pesata([r['costo'].get('elect_td_bld', [None] * len(d['anni'])) for r in R.values()], pesi)
    sett = lambda s: [round(x, 2) for x in somma([r['settori'].get(s, [0] * len(d['anni'])) for r in R.values()])]
    petrolio = somma([[(x or {}).get('offerta') or 0 for x in v] for k, v in d['mercati'].items() if k.startswith('crude oil|')])
    prezzo_petrolio = [(x or {}).get('prezzo') for x in d['mercati'].get('crude oil|USA', [])]
    reg = {}
    for code, _ in REGIONI:
        r = R.get(code)
        if not r:
            continue
        pet = [(x or {}).get('offerta') for x in d['mercati'].get('crude oil|' + code, [])]
        reg[code] = {
            'ingrosso': r['costo'].get('electricity'), 'casa': r['costo'].get('elect_td_bld'),
            'elettricita': [round(x, 3) for x in somma(list(r['elettricita'].values()))],
            'co2': [round(x * MTC_A_GTCO2, 3) for x in r['co2']], 'petrolio': pet}
    return {
        'generazione': gen,
        'costoIngrosso': costo_ingrosso, 'costoCasa': costo_casa,
        'co2': [round(x * MTC_A_GTCO2, 2) for x in somma([r['co2'] for r in R.values()])],
        'temperatura': d['temperatura'],
        'idrogeno': sett('H2 central production'), 'alluminio': sett('aluminum'), 'ammoniaca': sett('ammonia'), 'acciaio': sett('iron and steel'),
        'desal': [round(x, 2) for x in somma([r['desal'] for r in R.values()])],
        'petrolio': [round(x, 2) for x in petrolio], 'prezzoPetrolio': prezzo_petrolio,
        'regioni': reg}

def main():
    out = {'anni': None, 'scenari': {}, 'regioni': dict(REGIONI)}
    for nome, f in SCENARI:
        p = os.path.join(RIS, nome + '.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        if len(d['regioni']) < 32:
            print('saltato (incompleto)', nome); continue
        out['anni'] = d['anni']
        out['scenari'][str(f)] = riassumi(d)
        print('ok', nome)
    dest = os.path.join(QUI, '..', 'gcam-dati.js')
    open(dest, 'w').write('// Generato da gcam/sintesi.py: risultati GCAM riassunti per la pagina.\nconst GCAM = ' + json.dumps(out, separators=(',', ':')) + ';\n')
    print('scritto', os.path.normpath(dest))

if __name__ == '__main__':
    main()
