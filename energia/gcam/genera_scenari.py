"""
Genera gli scenari GCAM per la domanda 01: "Cosa succede se l'energia costa 3, 10, 30 o 100 volte meno?"

Approccio: la "nuova fonte" è rappresentata dalla tecnologia nucleare "large reactor" di GCAM
(elettricità programmabile, senza emissioni dirette), usata come segnaposto per la fusione.
Dal 2030 al 2050 i suoi costi (capitale, manutenzione fissa e variabile, combustibile per MWh)
scendono fino a 1/F di quelli del riferimento; dopo il 2050 restano a 1/F.
La fonte è disponibile in tutte le regioni (peso di scelta del sottosettore nucleare = 1 dal 2035).

Uso: python3 genera_scenari.py PERCORSO_GCAM_CORE
Scrive in energia/gcam/scenari/ un file XML aggiuntivo e una configurazione per ogni fattore.
"""
import os, re, sys

FATTORI = [3, 10, 30, 100]
ANNI = [2025, 2030, 2035, 2040, 2045, 2050] + list(range(2055, 2101, 5))

def moltiplicatore(anno, f):
    if anno <= 2030:
        return 1.0
    if anno >= 2050:
        return 1.0 / f
    # discesa geometrica tra 2030 e 2050
    return (1.0 / f) ** ((anno - 2030) / 20)

def periodi_tecnologia(xml, inizio_tag, nome):
    k = xml.find(f'{inizio_tag} name="{nome}">', xml.find('<global-technology-database'))
    fine = xml.find('</' + inizio_tag.strip('<') + '>', k)
    seg = xml[k:fine]
    out = {}
    for m in re.finditer(r'<period year="(\d+)">(.*?)</period>', seg, re.S):
        out[int(m.group(1))] = m.group(2)
    return out

def val(blocco, tag):
    m = re.search(rf'<{tag}>([\d.eE+-]+)</{tag}>', blocco)
    return float(m.group(1)) if m else None

def main(gcam):
    xmlpath = os.path.join(gcam, 'input/gcamdata/xml/electricity_water.xml')
    xml = open(xmlpath, encoding='utf-8').read()
    regioni = sorted(set(re.findall(r'<region name="([^"]+)"', xml)))
    pt = periodi_tecnologia(xml, '<pass-through-technology', 'large reactor')
    raffr = re.findall(r'<technology name="(large reactor \([^)]*\))">', xml)
    raffr = sorted(set(raffr))
    eff = {}
    for t in raffr:
        p = periodi_tecnologia(xml, '<technology', t)
        eff[t] = {a: val(b, 'efficiency') for a, b in p.items()}

    cartella = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scenari')
    os.makedirs(cartella, exist_ok=True)
    conf_ref = open(os.path.join(gcam, 'exe/configuration_ref.xml'), encoding='utf-8').read()

    for f in FATTORI:
        r = ['<?xml version="1.0" encoding="UTF-8"?>', '<scenario>', '<world>', '<global-technology-database>',
             '<location-info sector-name="electricity" subsector-name="nuclear">',
             '<pass-through-technology name="large reactor">']
        for a in ANNI:
            b = pt.get(a)
            if b is None:
                continue
            m = moltiplicatore(a, f)
            cap, fix, var = val(b, 'capital-overnight'), val(b, 'OM-fixed'), val(b, 'OM-var')
            r.append(f'<period year="{a}">')
            if a >= 2035:
                r.append('<share-weight>1</share-weight>')
            r.append(f'<input-capital name="capital"><capital-overnight>{cap*m:.4f}</capital-overnight></input-capital>')
            r.append(f'<input-OM-fixed name="OM-fixed"><OM-fixed>{fix*m:.4f}</OM-fixed></input-OM-fixed>')
            r.append(f'<input-OM-var name="OM-var"><OM-var>{var*m:.5f}</OM-var></input-OM-var>')
            r.append('</period>')
        r += ['</pass-through-technology>', '</location-info>',
              '<location-info sector-name="elec_large reactor" subsector-name="large reactor">']
        for t in raffr:
            r.append(f'<technology name="{t}">')
            for a in ANNI:
                e = eff[t].get(a)
                if e is None:
                    continue
                m = moltiplicatore(a, f)
                # combustibile per MWh ridotto di 1/m: efficienza moltiplicata
                r.append(f'<period year="{a}"><minicam-energy-input name="nuclearFuelGenIII"><efficiency>{e/m:.5f}</efficiency></minicam-energy-input></period>')
            r.append('</technology>')
        r += ['</location-info>', '</global-technology-database>']
        for reg in regioni:
            r.append(f'<region name="{reg}"><supplysector name="electricity"><subsector name="nuclear">')
            for a in range(2035, 2101, 5):
                r.append(f'<share-weight year="{a}">1</share-weight>')
            r.append('</subsector></supplysector></region>')
        r += ['</world>', '</scenario>']
        nome = f'energia_{f}x'
        open(os.path.join(cartella, nome + '.xml'), 'w', encoding='utf-8').write('\n'.join(r))
        # configurazione: riferimento + file aggiuntivo, percorsi assoluti
        c = conf_ref.replace('../input/', os.path.join(gcam, 'input') + '/')
        c = c.replace('</ScenarioComponents>',
                      f'\t\t<Value name = "{nome}">{os.path.join(cartella, nome + ".xml")}</Value>\n\t</ScenarioComponents>')
        c = re.sub(r'(<Value name="scenarioName">)[^<]*(</Value>)', rf'\g<1>{nome}\g<2>', c)
        open(os.path.join(cartella, f'configuration_{nome}.xml'), 'w', encoding='utf-8').write(c)
        print('scritto', nome)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/jgcri/gcam-core')
