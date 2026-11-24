# Modelli futuribili · The Long Shot

Domande sul futuro lontano, trasformate in modelli che si possono interrogare. Ogni domanda è un laboratorio: si cambiano le ipotesi e si guarda che mondo ne esce. I modelli non prevedono; mostrano quali scelte separano un futuro dall'altro.

Il sito è statico (HTML, CSS e JavaScript senza build): si apre `index.html` nel browser oppure si pubblica con GitHub Pages dalla radice del branch `main`.

## Le domande

| # | Domanda | Cartella | Stato |
| --- | --- | --- | --- |
| 01 | Cosa succede se l'energia costa 3, 10, 30 o 100 volte meno? | `energia/` | Risultati GCAM per 3, 10, 30 e 100 volte meno, più un modello esplorativo |

## Struttura

```
index.html          home con le domande
assets/tokens.css   token del design system di The Long Shot (copia di styles/tokens.css del repository TLS OS)
assets/site.css     stili del sito, registro "sito" (acceso)
energia/            domanda 01: pagina e modello (modello.js)
```

## Domanda 01 · Energia

`energia/modello.js` è un modello dinamico stilizzato del mondo, 2030–2080:

- **Prezzo:** la bolletta di casa è metà produzione e metà reti e oneri; l'industria paga 3/4 produzione. La riduzione dei costi di produzione (3–100 volte) e delle reti (1–5 volte) dà il prezzo finale. Il risultato chiave: le reti fanno da pavimento.
- **Attività sbloccate:** soglie di prezzo industriale (€/MWh) sotto le quali un'attività diventa conveniente. Sono **ordini di grandezza da verificare** con la letteratura tecnica.
- **Rimbalzo:** elasticità dei consumi al prezzo intorno a 0,6.
- **Mondo:** lavoro, disuguaglianza, clima, pressione su suolo e materiali, tensione geopolitica. I coefficienti sono **ipotesi esplicite**, non stime.

### Scenari GCAM

Il nucleo fisico (elettricità, prezzi, emissioni, clima, petrolio per 32 regioni) viene da [GCAM](https://github.com/JGCRI/gcam-core) 9.1, il modello aperto del Pacific Northwest National Laboratory.

- **Scenario di riferimento:** la configurazione standard di GCAM (`configuration_ref.xml`: SSP2, nessuna nuova politica climatica).
- **Nuova fonte:** la tecnologia nucleare `large reactor`, usata come segnaposto della fusione. Tra il 2030 e il 2050 capitale, manutenzione e combustibile per MWh scendono fino a 1/3, 1/10, 1/30, 1/100; la fonte è disponibile in tutte le regioni dal 2035. Le reti non cambiano.

File in `energia/gcam/`:

| File | Cosa fa |
| --- | --- |
| `genera_scenari.py` | Scrive i file aggiuntivi e le configurazioni in `scenari/` |
| `estrai.py` | Legge l'uscita di GCAM (`debug_db.xml`, 8–9 GB) riga per riga e salva gli indicatori in `risultati/` |
| `sintesi.py` | Riassume i risultati in `energia/gcam-dati.js`, letto dalla pagina |

Per riprodurre: compilare GCAM con `HAVE_JAVA = 0` e `DEBUG_XML_DB 1` in `reporting/source/xml_db_outputter.cpp` (così i risultati finiscono in `debug_db.xml` senza Java), generare i dati di input con `gcamdata` (`driver(write_xml=TRUE)`, serve una macchina con almeno 12 GB di memoria), poi lanciare `gcam.exe -C scenari/configuration_<scenario>.xml` per ogni scenario. Ogni scenario richiede circa un'ora su un processore.

## Design

Colori, tipografia e regole vengono dal design system di The Long Shot (`design/tokens.json`, `design/README.md` del repository TLS OS): registro "sito", campiture terracotta, oliva e notte, titoli in Playfair Display con la parola chiave in corsivo, etichette in JetBrains Mono, un solo arco per sezione.
