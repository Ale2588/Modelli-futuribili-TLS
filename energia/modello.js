// Modello 01 · Cosa succede se l'energia costa molto meno?
// Modello dinamico stilizzato del mondo, 2030-2080. I coefficienti sono ipotesi esplicite, non stime:
// servono a vedere quali scelte separano un futuro dall'altro. Le soglie di prezzo sono ordini di grandezza da verificare.

const PREZZO_OGGI = 100; // €/MWh, ordine di grandezza del prezzo all'ingrosso in Italia

const DEFAULT = {
  riduzione: 10,      // quante volte costa meno PRODURRE energia (3, 10, 30, 100)
  reti: 1.5,          // quante volte costano meno reti, accumuli e distribuzione
  velocita: 25,       // anni perché il nuovo prezzo arrivi a metà strada
  controllo: 0.5,     // 0 = bene comune diffuso, 1 = pochi padroni di impianti e reti
  redistribuzione: 0.4, // quanto i guadagni diventano redditi, servizi e tempo per tutti
  ai: 0.5,            // quanta energia diventa calcolo e automazione del lavoro
  ambiente: 0.4,      // regole su suolo, materiali, calore e natura
  petrostati: 0.3,    // accompagnamento internazionale dei paesi che vivono di idrocarburi
  materiali: 0.5      // quanto minerali e suolo restano un vincolo
};

// Attività che diventano convenienti sotto una certa soglia di prezzo per l'industria (€/MWh).
// Ordini di grandezza indicativi: da verificare con la letteratura tecnica.
const SOGLIE = [
  { nome: 'Data center e calcolo per l\'AI', soglia: 120, nota: 'conviene già oggi: l\'energia pesa, ma non decide' },
  { nome: 'Alluminio e metalli da elettrolisi', soglia: 40, nota: 'oggi si fanno dove l\'elettricità costa poco, come l\'Islanda' },
  { nome: 'Desalinizzazione per città e agricoltura', soglia: 30, nota: 'acqua dolce a basso costo ovunque ci sia mare' },
  { nome: 'Idrogeno verde e acciaio senza carbone', soglia: 20, nota: 'l\'idrogeno da elettricità batte quello da gas' },
  { nome: 'Fertilizzanti da aria e acqua', soglia: 20, nota: 'ammoniaca senza gas naturale' },
  { nome: 'Carburanti sintetici per aerei e navi', soglia: 12, nota: 'cherosene fatto con CO₂ e idrogeno' },
  { nome: 'Cattura della CO₂ dall\'aria su larga scala', soglia: 8, nota: 'serve anche capitale: l\'energia gratis non basta' },
  { nome: 'Agricoltura al chiuso per i cereali', soglia: 3, nota: 'la luce artificiale resta carissima rispetto al sole' }
];

function prezzi(P) {
  // Bolletta di oggi = metà produzione, metà reti, accumuli e oneri (famiglie); l'industria paga più produzione.
  const fam = 0.5 / P.riduzione + 0.5 / P.reti;
  const ind = 0.75 / P.riduzione + 0.25 / P.reti;
  return { famiglie: fam, industria: ind, industriaEuro: PREZZO_OGGI * ind };
}

function mondo(P0) {
  const P = Object.assign({}, DEFAULT, P0);
  const S = P.velocita, C = P.controllo, R = P.redistribuzione, A = P.ai, G = P.ambiente, T = P.petrostati, M = P.materiali;
  const pr = prezzi(P);
  const intensita = Math.max(0, Math.min(1, (1 - pr.famiglie) / 0.95)); // 0 = come oggi, 1 = energia quasi gratis
  const k = {}; ['prezzo','accesso','pil','disuguaglianza','disoccupazione','tempo','riscaldamento','pressione','tensione','consumo'].forEach(x => k[x] = []);
  const anni = [];
  let Y = 1, warm = 1.35;
  for (let t = 0; t <= 50; t++) {
    const diff = 1 / (1 + Math.exp(-(t - S) * 5 / S));
    const E = intensita * diff;                                   // quanto dell'abbondanza è arrivata
    const pInd = 1 - (1 - pr.industria) * diff;                   // prezzo industriale relativo a oggi
    const sb = SOGLIE.filter(s => PREZZO_OGGI * pInd <= s.soglia).length / SOGLIE.length; // quota di attività sbloccate
    const acc = E * (1 - 0.75 * C * (1 - 0.6 * R));
    const U = Math.pow(Math.max(0.03, 1 - (1 - pr.famiglie) * diff), -0.6 * (1 - 0.5 * G)); // rimbalzo: elasticità 0,6
    const dump = (1 - T) * 0.3 * Math.exp(-Math.pow((t - S * 0.6) / (S * 0.35), 2)) * intensita;
    const inst = Math.min(1, (1 - T) * (0.9 * 4 * E * (1 - E) + 0.25 * E) + 0.1);
    const tens = Math.min(1, 0.2 + 0.45 * inst + 0.5 * C * E * (1 - 0.5 * R) - 0.15 * acc * (1 - C));
    const D = Math.min(0.6, A * E * 0.65);
    const nuove = (acc * 0.5 + sb * 0.5) * (1 - M) * 0.6;
    const disocc = Math.max(0, D * (1 - R) * (1 - 0.5 * nuove));
    const tempo = D * R;
    const g = 0.02 + 0.015 * acc * (1 - 0.6 * M) + 0.012 * sb + 0.025 * A * E - 0.03 * Math.max(0, tens - 0.4) - 0.02 * disocc;
    Y *= 1 + g;
    const ineq = Math.max(0.2, Math.min(0.8, 0.38 + 0.25 * C * E + 0.2 * D * (1 - R) - 0.15 * R * E));
    const em = (1 - E) * (1 + dump);
    const rim = (sb >= 7 / 8 ? 1 : 0.3) * acc * (0.3 + 0.7 * G) * 0.012;
    warm = Math.max(1.0, warm + 0.022 * em - rim);
    const press = Math.max(0, Math.min(1, 0.4 + 0.12 * (U - 1) * (1 - G) * (0.5 + 0.5 * M) - 0.2 * acc * G));
    anni.push(2030 + t);
    k.prezzo.push(pInd); k.accesso.push(acc); k.pil.push(Y); k.disuguaglianza.push(ineq); k.disoccupazione.push(disocc);
    k.tempo.push(tempo); k.riscaldamento.push(warm); k.pressione.push(press); k.tensione.push(tens); k.consumo.push(U);
  }
  const L = a => a[a.length - 1], MX = a => Math.max(...a);
  const acc = L(k.accesso), Yf = L(k.pil);
  const scarsita = [
    ['Energia', pr.famiglie],
    ['Acqua dolce', Math.pow(Yf, 0.3) / (1 + 3 * acc * (PREZZO_OGGI * pr.industria <= 30 ? 1 : 0.3))],
    ['Calcolo', 1 / (1 + 8 * intensita * (0.3 + 0.7 * A))],
    ['Materie prime', L(k.consumo) * Math.pow(Yf, 0.3) / (1 + 2.5 * acc * (1 - M))],
    ['Terra e posizione', Math.pow(Yf, 0.6) / (1 + 0.6 * acc)],
    ['Tempo e attenzione umana', Math.pow(Yf, 0.7) / (1 + 2 * L(k.tempo))],
    ['Status e beni posizionali', Math.pow(Yf, 0.8)]
  ];
  const fin = { acc, ineq: L(k.disuguaglianza), dis: L(k.disoccupazione), tempo: L(k.tempo), press: L(k.pressione), warm: L(k.riscaldamento), tensMax: MX(k.tensione) };
  let arch;
  if (intensita < 0.45 && fin.tensMax < 0.5) arch = 'pocodiverso';
  else if (fin.ineq > 0.52 && C > 0.5) arch = 'feudale';
  else if (fin.dis > 0.2) arch = 'senzalavoro';
  else if (fin.press > 0.68) arch = 'jevons';
  else if (fin.acc < 0.5) arch = 'meta';
  else if (fin.tempo > 0.18 && fin.ineq < 0.42) arch = 'tempo';
  else if (fin.ineq < 0.43) arch = 'condivisa';
  else arch = 'diseguale';
  const viaggio = fin.tensMax > 0.62 ? 'turbolento' : fin.tensMax > 0.5 ? 'teso' : 'ordinato';
  const sbloccate = SOGLIE.filter(s => pr.industriaEuro <= s.soglia).map(s => s.nome);
  return { anni, k, scarsita, fin, arch, viaggio, prezzi: pr, intensita, sbloccate };
}
if (typeof module !== 'undefined') module.exports = { mondo, prezzi, DEFAULT, SOGLIE, PREZZO_OGGI };
