// Static demo: shared code of the pages. Data come from data/*.js (window.DEMO),
// written by scripts/export_static.py; script files instead of JSON so that the pages also open
// from file://. The order-up-to simulation is a port of workbench.inventory.simulate, the
// re-pricing of retail.demo.reprice; policy.html?selftest compares both with the Python results.

const DEMO = (window.DEMO = window.DEMO || {});
const NAMES = { naive: 'P-naive', normal: 'P-normal', quantile: 'P-quantile' };
const PARAM = { naive: 'buffer', normal: 'α', quantile: 'τ' };
const COLORS = { naive: '#2a78d6', normal: '#eb6834', quantile: '#1baf7a' };
const POLICIES = ['naive', 'normal', 'quantile'];

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

const loaded = {};
function load(src) {  // a data script, once
  if (!loaded[src]) {
    loaded[src] = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src; s.onload = resolve;
      s.onerror = () => reject(new Error(`cannot load ${src} (run scripts/export_static.py)`));
      document.head.appendChild(s);
    });
  }
  return loaded[src];
}

function param(name, fallback = '') {
  return new URLSearchParams(location.search).get(name) ?? fallback;
}

function nav(active) {
  const links = [['index.html', 'Overview'], ['forecast.html', 'Forecast'], ['policy.html', 'Policy'],
                 ['decision.html', 'Decision']];
  document.getElementById('nav').innerHTML = links.map(([href, label]) =>
    `<a href="${href}"${label === active ? ' class="active"' : ''}>${label}</a>`).join(' ');
}

function fail(err) {
  const main = document.querySelector('main');
  main.insertAdjacentHTML('afterbegin', `<p class="worse">${err.message || err}</p>`);
}

const fmt1 = v => v === null || v === undefined || Number.isNaN(v) ? '—' : Number(v.toFixed(1)).toString();
const pct = v => (100 * v).toFixed(1) + ' %';
const gbp = v => '£' + Math.round(v).toLocaleString('en-GB');
const num = v => (v === null || v === undefined ? NaN : v);

// inverse of the standard normal cdf (Acklam's rational approximation, |rel. error| < 1.2e-9)
function normPpf(p) {
  const a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2, 1.383577518672690e2,
             -3.066479806614716e1, 2.506628277459239];
  const b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1,
             -1.328068155288572e1];
  const c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838, -2.549732539343734,
             4.374664141464968, 2.938163982698783];
  const d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996, 3.754408661907416];
  const lo = 0.02425;
  if (p <= 0) return -Infinity;
  if (p >= 1) return Infinity;
  if (p < lo) {
    const q = Math.sqrt(-2 * Math.log(p));
    return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
           ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
  }
  if (p > 1 - lo) return -normPpf(1 - p);
  const q = p - 0.5, r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q /
         (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}

// order-up-to levels of one product per week (NaN = no order), as workbench.inventory.Lab.levels
function levels(code, policy, value, lead) {
  const s = DEMO.sim[code], k = lead + 1;
  if (policy === 'naive') return s.mu.map(m => (Number.isNaN(num(m)) ? 0 : k * m * (1 + value)));
  if (policy === 'normal') {
    const z = normPpf(value);
    return s.mu.map((m, j) => {
      const v = k * num(m) + z * (s.sigma[j] ?? 0) * Math.sqrt(k);
      return Number.isNaN(v) ? 0 : Math.max(v, 0);
    });
  }
  const idx = DEMO.meta.grids.quantile.indexOf(value);
  if (idx < 0) throw new Error(`τ ${value} is not on the exported grid`);
  return DEMO[`levels-L${lead}`][code].map(row => num(row ? row[idx] : null));
}

// workbench.inventory.simulate for one product: lost sales, review every week, start stock S_0
function simulate(demand, level, lead) {
  const m = demand.length, d = demand.map(v => (Number.isNaN(num(v)) ? 0 : v));
  const pipeline = new Array(m + lead + 1).fill(0);
  let onHand = Number.isNaN(level[0]) ? 0 : level[0];
  const out = { order: [], start: [], end: [], served: [], short: [], avg: [] };
  for (let i = 0; i < m; i++) {
    onHand += pipeline[i];
    let onOrder = 0;
    for (let j = i + 1; j < pipeline.length; j++) onOrder += pipeline[j];
    const s = level[i];
    const order = Number.isNaN(s) ? 0 : Math.max(s - (onHand + onOrder), 0);
    if (lead === 0) onHand += order; else pipeline[i + lead] += order;
    const start = onHand, served = Math.min(Math.max(onHand, 0), d[i]);
    onHand -= served;
    out.order.push(order); out.start.push(start); out.end.push(onHand);
    out.served.push(served); out.short.push(d[i] - served); out.avg.push((start + onHand) / 2);
  }
  return out;
}

// totals of an aggregate (retail.demo.aggregate) at these costs, as retail.demo.reprice
function reprice(agg, margin, holding, writedown, weeksPerYear = 52) {
  const dem = agg.served + agg.short;
  const t = {
    fill_rate: dem > 0 ? agg.served / dem : NaN,
    cycle_service: 1 - agg.stockouts / agg.weeks,
    stockout_weeks: agg.stockouts,
    avg_stock_value: (1 - margin) * agg.A,
    holding_cost: holding * (1 - margin) / weeksPerYear * agg.H,
    lost_margin: margin * agg.S,
    write_down: writedown * (1 - margin) * agg.E,
  };
  t.total_cost = t.holding_cost + t.lost_margin + t.write_down;
  return t;
}

// a range input that steps through the values of a grid; returns () => the selected value
function gridSlider(input, values, start) {
  input.min = 0; input.max = values.length - 1; input.step = 1;
  let best = 0;
  values.forEach((v, i) => { if (Math.abs(v - start) < Math.abs(values[best] - start)) best = i; });
  input.value = best;
  const out = input.nextElementSibling;
  const show = () => { if (out) out.textContent = values[+input.value]; };
  input.addEventListener('input', show); show();
  return () => values[+input.value];
}

function th(label, key, cls = 'num') {
  return `<th class="${cls}" title="${(HELP[key] || '').replace(/"/g, '&quot;')}">${label}</th>`;
}

// column help, as in the workbench (workbench/help.py)
const HELP = {
  week: 'Calendar week (Monday).',
  demand: 'Units actually sold in the week (cleaned demand); empty for weeks after the data.',
  mean: 'Mean forecast (expected units).',
  'q0.1': '10 % quantile: demand is expected to be below this value in 1 week out of 10.',
  median: 'Median forecast: demand is equally likely to be above or below.',
  'q0.9': '90 % quantile: demand is expected to exceed this value in 1 week out of 10.',
  'q0.975': '97.5 % quantile: demand is expected to exceed this value in 1 week out of 40.',
  policy: 'Order policy with its parameter. P-naive: 4-week mean x (1 + buffer); P-normal: moving average + z x sigma; P-quantile: tau-quantile of the forecast sample paths.',
  fill_rate: 'Fill rate: share of the demand that was served from stock. Higher = fewer lost sales.',
  cycle_service: 'Cycle service level: share of product-weeks without any stock-out.',
  stockout_weeks: 'Number of product-weeks in which some demand could not be served.',
  avg_stock_value: 'Average value of the stock on hand, at unit cost, summed over the products: the capital tied up in stock. Lower is better at the same fill rate.',
  holding: 'Holding cost: stock value x holding rate per year, over the simulated weeks.',
  lost_margin: 'Lost margin: units not sold for lack of stock x margin per unit.',
  write_down: 'Write-down: share of the unit cost written off for seasonal products left in stock at the end (set by the slider).',
  total_cost: 'Total cost = holding + lost margin + write-down. Lower is better.',
  stock_code: 'Product id (stock code) of the shop.',
  description: 'Product name (the most frequent description in the invoices).',
  segment: 'ABC class (A = top 80 % of revenue) and Syntetos-Boylan class (smooth, erratic, intermittent, lumpy).',
  category: 'Product category, assigned from keywords in the description.',
  revenue: 'Revenue of the product over all weeks (Dec 2009 - Nov 2011), in pounds.',
  on_hand: 'Units in stock at the start of the week, after this week\'s deliveries.',
  on_order: 'Units ordered earlier that have not arrived yet.',
  position: 'Inventory position = on hand + on order: what is available before this order.',
  order_up_to: 'Order-up-to level S: the target for the position. P-quantile: the tau-quantile of the demand over lead time + 1 week.',
  order: 'Units to order now = S - position (0 if the position is already above S).',
  unit_cost: 'Unit cost = (1 - margin) x price, in pounds.',
  order_value: 'Order x unit cost, in pounds: the money this order ties up.',
};
