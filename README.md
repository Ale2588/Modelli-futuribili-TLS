# Modelli futuribili · The Long Shot

Domande sul futuro lontano, trasformate in modelli che si possono interrogare. Ogni domanda è un laboratorio: si cambiano le ipotesi e si guarda che mondo ne esce. I modelli non prevedono; mostrano quali scelte separano un futuro dall'altro.

Il sito è statico (HTML, CSS e JavaScript senza build): si apre `index.html` nel browser oppure si pubblica con GitHub Pages dalla radice del branch `main`.

## Le domande

| # | Domanda | Cartella | Stato |
| --- | --- | --- | --- |
| 01 | Cosa succede se l'energia costa 3, 10, 30 o 100 volte meno? | `energia/` | Modello esplorativo; integrazione con GCAM in corso |

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

### Prossimo passo: GCAM

Il nucleo fisico (energia, suolo, acqua, emissioni per 32 regioni) verrà sostituito dai risultati di [GCAM](https://github.com/JGCRI/gcam-core), il modello aperto del Pacific Northwest National Laboratory, con una nuova fonte elettrica a costo 3, 10, 30 e 100 volte inferiore. Le modifiche locali a GCAM e i file degli scenari andranno in `energia/gcam/`.

## Design

Colori, tipografia e regole vengono dal design system di The Long Shot (`design/tokens.json`, `design/README.md` del repository TLS OS): registro "sito", campiture terracotta, oliva e notte, titoli in Playfair Display con la parola chiave in corsivo, etichette in JetBrains Mono, un solo arco per sezione.
