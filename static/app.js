'use strict';

const $ = id => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const COLORS = { temperature: '#cc6545', rainfall: '#147c89', ink: '#183d47', muted: '#526c76', grid: '#e0e9ed' };
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const SNAPSHOT_MODE = document.querySelector('meta[name="climate-mode"]')?.content === 'snapshot';
let config;
let currentResult;
let currentName;
let currentQuery;
let activeRequest;
let datasetComparison;
let importSequence = 0;
let windowRequest;

function apiPath(name) {
  return SNAPSHOT_MODE ? `demo/${name}.json` : `api/${name}`;
}

function node(tag, attrs = {}, text = '') {
  const el = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  if (text) el.textContent = text;
  return el;
}

function number(value, digits = 2) {
  return Number(value).toLocaleString('en', { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

function signed(value, digits = 2) {
  return `${value > 0 ? '+' : value < 0 ? '−' : ''}${number(Math.abs(value), digits)}`;
}

function coordinates(lat, lon) {
  return `${number(Math.abs(lat), 4)}° ${lat < 0 ? 'S' : 'N'}, ${number(Math.abs(lon), 4)}° ${lon < 0 ? 'W' : 'E'}`;
}

function selectedLocation() {
  const preset = config.presets[$('location').value];
  const latitude = preset ? preset.latitude : Number($('latitude').value);
  const longitude = preset ? preset.longitude : Number($('longitude').value);
  return { latitude, longitude, name: preset ? preset.name : 'Custom location' };
}

function updateLocation() {
  if (!config) return;
  $('custom-coordinates').hidden = $('location').value !== 'custom';
  for (const id of ['latitude', 'longitude']) $(id).disabled = $('location').value !== 'custom';
  const place = selectedLocation();
  $('coordinate-caption').textContent = coordinates(place.latitude, place.longitude);
  const cx = (place.longitude + 180) / 360 * 240;
  const cy = (90 - place.latitude) / 180 * 112;
  for (const id of ['location-dot', 'location-ring']) {
    $(id).setAttribute('cx', Math.max(0, Math.min(240, cx)));
    $(id).setAttribute('cy', Math.max(0, Math.min(112, cy)));
  }
}

function getQuery() {
  const place = selectedLocation();
  return { place, params: new URLSearchParams({ latitude: place.latitude, longitude: place.longitude, start: $('start').value, end: $('end').value, variable: document.querySelector('input[name=variable]:checked').value }) };
}

async function explore(event) {
  if (event) event.preventDefault();
  globalThis.ClimateStory?.pause();
  ++importSequence;
  if (!config) {
    $('status').hidden = false;
    $('status').textContent = 'The configuration is still loading. Your choices are kept. Choose Explore this place when it is ready.';
    return;
  }
  $('end').setCustomValidity('');
  if (Number($('end').value) - Number($('start').value) < 9) {
    $('end').setCustomValidity('Choose a period of at least 10 complete years.');
    $('end').reportValidity();
    return;
  }
  if (!$('explore-form').reportValidity()) return;
  if (activeRequest) activeRequest.abort();
  const request = new AbortController();
  activeRequest = request;
  const query = getQuery();
  $('status').hidden = false;
  $('status').textContent = `Loading ${SNAPSHOT_MODE ? 'frozen' : 'NASA'} data for ${query.place.name.replace(', Iran', '')}… This can take up to 40 seconds.`;
  $('error').hidden = true;
  $('results').hidden = true;
  $('results').setAttribute('aria-busy', 'true');
  $('explore-button').disabled = true;
  try {
    const path = SNAPSHOT_MODE ? `demo/${$('location').value}${$('window').value === 'full45' ? '' : `-${$('window').value}`}-${query.params.get('variable')}.json` : `api/climate?${query.params}`;
    const response = await fetch(path, { signal: request.signal });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The data service returned an error. Please try again.');
    if (activeRequest !== request) return;
    currentResult = result;
    currentName = query.place.name;
    currentQuery = query.params.toString();
    $('results').hidden = false;
    render(result, query.place.name);
    $('import-status').hidden = true;
    persistWork();
    $('status').hidden = true;
    $('results').hidden = false;
    $('results').setAttribute('aria-busy', 'false');
  } catch (error) {
    if (error.name === 'AbortError') return;
    $('status').hidden = true;
    $('error').hidden = false;
    $('error-text').textContent = error.message === 'Failed to fetch' ? SNAPSHOT_MODE ? 'The saved demonstration could not be reached. Check your connection and try again.' : 'The local app is not reachable. Restart the server, then try again.' : error.message;
    $('results').setAttribute('aria-busy', 'false');
  } finally {
    if (activeRequest === request) $('explore-button').disabled = false;
  }
}

function render(result, name) {
  const temperature = result.variable === 'temperature';
  const color = COLORS[result.variable];
  document.documentElement.style.setProperty('--plot', color);
  document.documentElement.style.setProperty('--plot-wash', `${color}24`);
  const t = result.trend;
  const unit = temperature ? '°C' : 'mm';
  $('result-location').textContent = name;
  $('chart-title').textContent = `A longer view of ${temperature ? 'temperature' : 'precipitation'}`;
  $('chart-subtitle').textContent = `${t.first_year}–${t.last_year} · ${t.years} complete years · ${temperature ? 'Annual mean temperature at 2 m' : 'Approximate annual precipitation'}`;
  // Use an HTML element for the unit rather than inline markup from any data.
  $('slope-value').replaceChildren(document.createTextNode(signed(t.slope_per_decade)));
  const unitEl = document.createElement('em');
  unitEl.textContent = temperature ? '°C / decade' : 'mm/year / decade';
  $('slope-value').append(unitEl);
  $('confidence-interval').textContent = `Ordinary OLS 95% slope interval: ${signed(t.ci95_per_decade[0])} to ${signed(t.ci95_per_decade[1])} ${temperature ? '°C' : 'mm/year'} per decade`;
  const evidence = t.evidence;
  $('evidence-tag').classList.toggle('unclear', evidence === 'unclear');
  $('evidence-tag').textContent = evidence === 'unclear' ? 'Ordinary interval includes zero' : 'Ordinary interval excludes zero';
  const direction = evidence === 'positive' ? 'increase' : 'decrease';
  $('evidence-text').textContent = evidence === 'unclear'
    ? 'The confidence interval includes zero. This record does not give clear evidence of a linear trend under this model. That does not prove there was no change.'
    : `The fitted line shows an ${direction === 'increase' ? 'increase' : 'estimated decrease'} of ${number(Math.abs(t.slope_per_decade))} ${temperature ? '°C' : 'mm of annual precipitation'} per decade. The 95% slope interval excludes zero under the model assumptions.`;
  const p = t.p_value < 0.001 ? '< 0.001' : `= ${number(t.p_value, 3)}`;
  $('chart-summary').textContent = `Ordinary OLS two-sided p ${p}. R² = ${number(t.r_squared, 2)}. Estimated fitted change across the period: ${signed(t.fitted_change)} ${temperature ? '°C' : 'mm/year'}.`;
  const correlation = t.lag1_residual_correlation;
  $('correlation-warning').hidden = correlation === null || Math.abs(correlation) <= 0.3;
  $('correlation-warning').textContent = `Neighboring annual residuals may be related (lag-one correlation ${number(correlation || 0, 2)}). The simple interval may be too narrow. Treat the trend evidence with extra care.`;
  $('coverage-note').hidden = result.excluded_years.length === 0;
  $('coverage-note').textContent = `Years excluded because one or more months are missing: ${result.excluded_years.join(', ')}. Missing months are left blank in the monthly view.`;
  renderAnnual(result);
  renderChecks(result);
  renderMonthly(result);
  const source = result.provenance;
  $('source-description').textContent = `${source.provider} · ${source.sources.join(', ') || 'See original response'} · ${coordinates(result.location.latitude, result.location.longitude)}. ${result.metadata.aggregation}. ${source.spatial_resolution.description}`;
  $('retrieval-description').textContent = `${source.delivery}. Retrieved ${new Date(source.fetched_at).toLocaleString('en-GB', { timeZone: 'UTC', dateStyle: 'medium', timeStyle: 'short' })} UTC. API ${source.api_version || 'version not provided'}.`;
  $('source-link').href = source.request_url;
  $('download-csv').href = '#sources';
  $('table-unit').textContent = result.metadata.unit;
  $('table-caption').textContent = `${name}: ${result.metadata.name.toLowerCase()}, ${t.first_year}–${t.last_year}`;
  const fragment = document.createDocumentFragment();
  for (const row of result.annual) {
    const tr = document.createElement('tr');
    for (const text of [row.year, number(row.value)]) {
      const td = document.createElement('td'); td.textContent = text; tr.append(td);
    }
    fragment.append(tr);
  }
  $('table-body').replaceChildren(fragment);
  renderDatasetComparison();
  renderWindows();
}

function matchingComparison() {
  if (!currentResult || !datasetComparison || currentResult.variable !== 'temperature') return null;
  return datasetComparison.rows.find(row => {
    const [latitude, longitude] = row.requested_coordinates;
    return Math.abs(latitude - currentResult.location.latitude) < .00001 && Math.abs(longitude - currentResult.location.longitude) < .00001 && row.power_payload_sha256 === currentResult.provenance.payload_sha256;
  });
}

function renderDatasetComparison() {
  updateViewLink();
  if (!currentResult) return;
  const row = matchingComparison();
  const matchingPeriod = currentResult.period.start === 1981 && currentResult.period.end === 2025;
  const available = row && matchingPeriod;
  $('dataset-comparison').hidden = !available;
  if (!available) {
    $('dataset-reading').textContent = !datasetComparison ? 'The frozen source comparison is unavailable. The main NASA analysis above is still usable.' : currentResult.variable !== 'temperature' ? 'Precipitation has no second-source comparison in this prototype. Temperature checks must not be treated as rainfall validation.' : !matchingPeriod ? 'The saved source comparison covers 1981–2025. Choose that exact period to compare rates; other periods are not mixed into this result.' : 'This location or source snapshot does not match the saved comparison. The evaluation page documents the five frozen preset records.';
    return;
  }
  $('dataset-reading').textContent = 'Compare two temperature products over the same complete years. The GISTEMP value is from our frozen comparison; it has a different spatial support from the POWER point request.';
  $('source-compare-caption').textContent = `${row.name}, ${row.years[0]}–${row.years.at(-1)}. Both rates use ${row.years.length} complete years.`;
  const rows = [
    ['NASA POWER / MERRA-2', '0.5° latitude × 0.625° longitude', currentResult.trend.slope_per_decade],
    ['NASA GISTEMP v4, land-only', `2° cell centered at ${row.gistemp_cell_center.join(', ')}; 250 km station smoothing`, row.gistemp_slope_c_per_decade],
  ];
  $('source-compare-body').replaceChildren(...rows.map(values => {
    const tr = document.createElement('tr');
    for (const value of values) { const td = document.createElement('td'); td.textContent = typeof value === 'number' ? signed(value, 3) : value; tr.append(td); }
    return tr;
  }));
  $('source-disagreement').hidden = row.name !== 'Toronto, Canada';
  $('source-disagreement').textContent = 'Toronto shows a substantial source difference. Nearby POWER requests also change the rate. Our audit checks aggregation and spatial sensitivity, but does not establish which source is correct or explain the cause.';
}

function updateViewLink() {
  if (!globalThis.ClimateViewLinks) return;
  $('view-link-controls').hidden = !SNAPSHOT_MODE;
  if (!SNAPSHOT_MODE) return;
  const selection = ClimateViewLinks.match(currentResult, config, datasetComparison);
  $('copy-view-link').disabled = !selection;
  $('view-link-help').textContent = selection
    ? 'Opens this public example. Notes are not included. The link does not freeze the app version or source data. Download your investigation for the exact frozen evidence.'
    : 'A view link is available only when the displayed analysis matches a frozen public preset, period, and source snapshot. Download your investigation to share this evidence.';
  $('view-link-status').textContent = '';
  $('view-link-fallback').hidden = true;
  $('view-link-url').value = '';
}

function renderChecks(result) {
  const checks = result.checks;
  const unit = result.metadata.unit;
  $('checks-summary').textContent = !checks.hac_available
    ? 'Calendar years are missing, so dependence-adjusted intervals are withheld. The ordinary interval is shown with its independence assumption.'
    : checks.interval_conclusions_agree
      ? 'The displayed intervals agree about whether they include zero. They share the same data, and their uncertainty assumptions can still be wrong.'
      : 'The displayed intervals disagree about whether they include zero. The statistical conclusion depends on the error assumptions or lag choice.';
  const intervals = checks.intervals;
  const values = intervals.flatMap(r => r.ci95_per_decade);
  const low = Math.min(0, ...values), high = Math.max(0, ...values);
  const pad = Math.max((high - low) * .12, result.variable === 'temperature' ? .03 : 1);
  const width = Math.max(220, Math.min(760, $('interval-chart').parentElement.clientWidth || 760));
  const compact = width < 500;
  const left = compact ? 135 : 225, right = width-15, top = 25, step = compact ? 43 : 33;
  const bottom = top + intervals.length * step;
  const x = value => left + (value - low + pad) / (high - low + 2 * pad) * (right - left);
  const parts = [node('title', { id: 'interval-title' }, 'Trend interval comparison'), node('desc', { id: 'interval-description' }, `Rates in ${unit} per decade. ${intervals.map(r => `${r.method}${r.lag === null ? '' : ` (${r.lag} years)`}: ${number(r.ci95_per_decade[0])} to ${number(r.ci95_per_decade[1])}`).join('. ')}. All intervals are conditional; none guarantees real-world coverage.`)];
  parts.push(node('line', { x1: x(0), x2: x(0), y1: 12, y2: bottom, stroke: COLORS.ink, 'stroke-dasharray': '3 3' }));
  parts.push(node('text', { x: x(0), y: 9, 'text-anchor': 'middle' }, 'Zero'));
  for (const tick of [low-pad, (low+high)/2, high+pad]) {
    parts.push(node('text', { x: x(tick), y: bottom+18, 'text-anchor': 'middle' }, signed(tick)));
  }
  const rows = document.createDocumentFragment();
  intervals.forEach((row, i) => {
    const y = top+i*step;
    const label = row.lag === null ? row.method : row.method.includes('automatic') ? `Newey-West, auto lag ${row.lag}` : `Newey-West, lag ${row.lag}`;
    if (compact && row.lag !== null) {
      parts.push(node('text', { x: 0, y: y-3 }, 'Newey-West'));
      parts.push(node('text', { x: 0, y: y+11 }, row.method.includes('automatic') ? `auto lag ${row.lag}` : `lag ${row.lag}`));
    } else parts.push(node('text', { x: 0, y: y+4 }, label));
    parts.push(node('line', { x1: x(row.ci95_per_decade[0]), x2: x(row.ci95_per_decade[1]), y1: y, y2: y, stroke: i === 0 ? COLORS.muted : COLORS[result.variable], 'stroke-width': 3 }));
    for (const bound of row.ci95_per_decade) parts.push(node('line', { x1: x(bound), x2: x(bound), y1: y-5, y2: y+5, stroke: COLORS.ink }));
    parts.push(node('circle', { cx: x(row.slope_per_decade), cy: y, r: 4, fill: COLORS.ink }));
    const tr = document.createElement('tr');
    for (const text of [label, signed(row.ci95_per_decade[0]), signed(row.ci95_per_decade[1]), row.evidence === 'unclear' ? 'No' : 'Yes, conditionally']) {
      const td = document.createElement('td'); td.textContent = text; tr.append(td);
    }
    rows.append(tr);
  });
  parts.push(node('text', { x: compact ? 0 : left, y: bottom+39, class: 'axis-title' }, compact ? `${unit} per decade` : `${unit} per decade · dot: rate · bar: conditional interval`));
  $('interval-chart').setAttribute('viewBox', `0 0 ${width} ${bottom+52}`);
  $('interval-chart').replaceChildren(...parts);
  $('interval-body').replaceChildren(rows);
  $('robust-slope').textContent = `Robust slope (Theil-Sen): ${signed(checks.theil_sen_slope_per_decade)} ${unit} per decade. This checks sensitivity to extreme values; it does not correct temporal dependence.`;
  const influence = checks.leave_one_out;
  $('influence-reading').textContent = `Removing one year at a time gives rates from ${signed(influence.minimum_slope_per_decade)} to ${signed(influence.maximum_slope_per_decade)} ${unit} per decade. This is a sensitivity range, not a confidence interval.`;
  $('period-caption').textContent = `${unit} per decade. Date checks use the same dataset.`;
  const periods = document.createDocumentFragment();
  for (const row of checks.periods) {
    const tr = document.createElement('tr');
    for (const text of [row.label, row.available ? `${row.first_year}–${row.last_year} (${row.years})` : `${row.years} complete years`, row.available ? signed(row.slope_per_decade) : 'Too few years']) {
      const td = document.createElement('td'); td.textContent = text; tr.append(td);
    }
    periods.append(tr);
  }
  $('period-body').replaceChildren(periods);
  $('check-messages').replaceChildren(...checks.messages.map(message => { const li = document.createElement('li'); li.textContent = message; return li; }));
  $('check-messages').hidden = checks.messages.length === 0;
}

function renderAnnual(result, renderWidth) {
  const svg = $('annual-chart');
  const data = result.annual;
  const line = result.trend.line;
  const width = renderWidth || Math.max(300, Math.min(900, $('chart-container').clientWidth || 900));
  const height = width < 500 ? 280 : 320, left = 54, right = 18, top = 34, bottom = 42;
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  const color = COLORS[result.variable];
  const all = [...data.map(d => d.value), ...line.flatMap(d => [d.low, d.high])];
  const min = Math.min(...all), max = Math.max(...all);
  const padding = Math.max((max - min) * 0.13, result.variable === 'temperature' ? 0.3 : 10);
  const yMin = result.variable === 'rainfall' ? Math.max(0, min - padding) : min - padding;
  const yMax = max + padding;
  const x = year => left + (year - result.period.start) / (result.period.end - result.period.start) * (width - left - right);
  const y = value => height - bottom - (value - yMin) / (yMax - yMin) * (height - top - bottom);
  const parts = [node('title', { id: 'annual-chart-title' }, `${currentName}: annual ${result.metadata.name.toLowerCase()}`), node('desc', { id: 'annual-chart-description' }, `${result.trend.years} complete years from ${result.trend.first_year} to ${result.trend.last_year}. Estimated trend ${signed(result.trend.slope_per_decade)} ${result.metadata.unit} per decade. The annual data are also available in the table below.`)];
  parts.push(node('text', { x: left, y: 14, class: 'axis-title' }, result.metadata.unit));
  for (let i = 0; i <= 4; i++) {
    const value = yMin + (yMax - yMin) * i / 4;
    parts.push(node('line', { x1: left, x2: width - right, y1: y(value), y2: y(value), stroke: COLORS.grid, 'stroke-width': 1 }));
    parts.push(node('text', { x: left - 11, y: y(value) + 4, 'text-anchor': 'end' }, number(value, result.variable === 'temperature' ? 1 : 0)));
  }
  const years = new Set([result.period.start, result.period.end]);
  const step = result.period.end - result.period.start > 25 ? (width < 500 ? 20 : 10) : (width < 500 ? 10 : 5);
  const edgeGap = width < 500 ? 8 : 3;
  for (let year = Math.ceil(result.period.start / step) * step; year < result.period.end - 2; year += step) {
    if (year - result.period.start >= edgeGap && result.period.end - year >= edgeGap) years.add(year);
  }
  for (const year of years) parts.push(node('text', { x: x(year), y: height - 15, 'text-anchor': 'middle' }, String(year)));
  const path = (rows, prop) => rows.map((d, i) => `${i === 0 ? 'M' : 'L'}${x(d.year).toFixed(2)},${y(d[prop]).toFixed(2)}`).join(' ');
  const band = `${path(line, 'high')} ${[...line].reverse().map(d => `L${x(d.year).toFixed(2)},${y(d.low).toFixed(2)}`).join(' ')} Z`;
  parts.push(node('path', { d: band, fill: color, 'fill-opacity': 0.13 }));
  // Break the observed line across missing years.
  let d = '';
  data.forEach((row, i) => { d += `${i && row.year === data[i - 1].year + 1 ? 'L' : 'M'}${x(row.year)},${y(row.value)} `; });
  parts.push(node('path', { d, fill: 'none', stroke: color, 'stroke-width': 2.1, 'stroke-linejoin': 'round' }));
  parts.push(node('path', { d: path(line, 'value'), fill: 'none', stroke: COLORS.ink, 'stroke-width': 1.6, 'stroke-dasharray': '6 5' }));
  data.forEach(row => {
    const point = node('circle', { cx: x(row.year), cy: y(row.value), r: 3.5, class: 'observation', fill: color });
    parts.push(point);
    const hit = node('circle', { cx: x(row.year), cy: y(row.value), r: 9, fill: 'transparent', tabindex: 0, 'aria-label': `${row.year}: ${number(row.value)} ${result.metadata.unit}` });
    hit.append(node('title', {}, `${row.year}: ${number(row.value)} ${result.metadata.unit}`));
    const show = () => {
      const tip = $('chart-tooltip');
      tip.textContent = `${row.year} · ${number(row.value)} ${result.metadata.unit}`;
      tip.style.left = `${x(row.year) / width * 100}%`;
      tip.style.top = `${y(row.value) / height * 100}%`;
      tip.hidden = false;
      point.setAttribute('r', 5);
    };
    const hide = () => { $('chart-tooltip').hidden = true; point.setAttribute('r', 3.5); };
    hit.addEventListener('mouseenter', show); hit.addEventListener('mouseleave', hide);
    hit.addEventListener('focus', show); hit.addEventListener('blur', hide);
    parts.push(hit);
  });
  svg.replaceChildren(...parts);
}

function mix(a, b, amount) {
  const channels = color => color.match(/\w\w/g).map(n => parseInt(n, 16));
  const ca = channels(a), cb = channels(b);
  return `#${ca.map((v, i) => Math.round(v + (cb[i] - v) * amount).toString(16).padStart(2, '0')).join('')}`;
}

function heatColor(value, min, max, variable) {
  const amount = (value - min) / (max - min || 1);
  if (variable === 'rainfall') return mix('edf5f6', '147c89', amount);
  return amount < 0.5 ? mix('39768e', 'f0f4ec', amount * 2) : mix('f0f4ec', 'ce6745', amount * 2 - 1);
}

function renderMonthly(result) {
  const svg = $('monthly-chart');
  const years = result.period.end - result.period.start + 1;
  const left = 38, right = 14, top = 12, rowHeight = 15, step = (900 - left - right) / years;
  const valid = result.monthly.filter(row => row.value !== null).map(row => row.value);
  const min = Math.min(...valid), max = Math.max(...valid);
  const color = value => heatColor(value, min, max, result.variable);
  const children = [node('title', { id: 'monthly-title' }, 'Monthly climate patterns'), node('desc', { id: 'monthly-description' }, 'Columns are years and rows are months. Use arrow keys after focusing the first cell to inspect monthly values. Missing months are grey.')];
  const cells = [];
  MONTHS.forEach((month, i) => children.push(node('text', { x: 0, y: top + i * rowHeight + 10, 'font-size': 10 }, month)));
  for (const [i, row] of result.monthly.entries()) {
    const label = `${MONTHS[row.month - 1]} ${row.year}: ${row.value === null ? 'missing' : `${number(row.value)} ${result.metadata.monthly_unit}`}`;
    const cell = node('rect', { x: left + (row.year - result.period.start) * step, y: top + (row.month - 1) * rowHeight, width: Math.max(step - 1.5, 1), height: 12.5, rx: 1.3, fill: row.value === null ? '#c8cfd2' : color(row.value), tabindex: i === 0 ? 0 : -1, 'aria-label': label });
    cell.append(node('title', {}, label));
    const describe = () => { $('monthly-detail').textContent = label; };
    cell.addEventListener('mouseenter', describe);
    cell.addEventListener('focus', describe);
    cell.addEventListener('keydown', event => {
      const offsets = { ArrowRight: 12, ArrowLeft: -12, ArrowDown: 1, ArrowUp: -1 };
      if (!(event.key in offsets) && event.key !== 'Home' && event.key !== 'End') return;
      event.preventDefault();
      const target = event.key === 'Home' ? 0 : event.key === 'End' ? result.monthly.length - 1 : Math.min(Math.max(i + offsets[event.key], 0), result.monthly.length - 1);
      cell.setAttribute('tabindex', -1); cells[target].setAttribute('tabindex', 0); cells[target].focus();
    });
    cells.push(cell); children.push(cell);
  }
  for (let year = result.period.start; year <= result.period.end; year++) {
    if (year !== result.period.start && year !== result.period.end && year % 10 !== 0) continue;
    if (year !== result.period.start && year !== result.period.end && (year - result.period.start < 3 || result.period.end - year < 3)) continue;
    children.push(node('text', { x: left + (year - result.period.start + .5) * step, y: 211, 'text-anchor': 'middle', 'font-size': 10 }, String(year)));
  }
  svg.replaceChildren(...children);
  $('heatmap-key').replaceChildren();
  const lower = document.createElement('span'); lower.textContent = number(min, 0); $('heatmap-key').append(lower);
  for (let i = 0; i < 7; i++) { const swatch = document.createElement('i'); swatch.style.background = color(min + (max - min) * i / 6); $('heatmap-key').append(swatch); }
  const upper = document.createElement('span'); upper.textContent = `${number(max, 0)} ${result.metadata.monthly_unit}`; $('heatmap-key').append(upper);
  $('season-description').textContent = `Each square is one month. Color shows ${result.variable === 'temperature' ? 'mean temperature' : 'approximate precipitation total'}, not an anomaly.`;
  $('monthly-detail').textContent = 'Hover over a month, or use Tab and the arrow keys to inspect a value.';
}

function download(contents, type, filename) {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = filename;
  document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function readNotes() {
  return { question: $('investigation-question').value, interpretation: $('investigation-interpretation').value, remaining_uncertainty: $('investigation-uncertainty').value };
}

function updateStorageControls() {
  const available = ClimateWorkspace.storageAvailable();
  $('save-locally').disabled = !available;
  $('restore-work').disabled = !available;
  $('clear-work').disabled = !available;
  if (!available) $('workspace-status').textContent = 'Browser storage is unavailable. You can still import and download investigation files.';
}

async function persistWork() {
  if (!$('save-locally').checked || !currentResult) return;
  try {
    const saved = await ClimateWorkspace.save(currentResult, readNotes(), currentName);
    if (saved.superseded) return;
    $('workspace-status').textContent = 'Latest investigation saved on this device. It is not uploaded.';
  } catch (error) {
    $('workspace-status').textContent = `Local saving failed: ${error.message}. Download your investigation instead.`;
  }
}

async function openInvestigation(text, origin, sequence = ++importSequence, guided = false) {
  if (!guided) globalThis.ClimateStory?.pause();
  const saved = await ClimateWorkspace.importText(text);
  if (sequence !== importSequence) return;
  if (activeRequest) { activeRequest.abort(); activeRequest = null; }
  $('explore-button').disabled = false;
  currentResult = saved.analysis;
  currentName = saved.locationName;
  currentQuery = null;
  if (!guided) for (const [id, key] of [['investigation-question','question'], ['investigation-interpretation','interpretation'], ['investigation-uncertainty','remaining_uncertainty']]) $(id).value = saved.notes[key];
  $('status').hidden = true; $('error').hidden = true;
  $('results').hidden = false; $('results').setAttribute('aria-busy', 'false');
  render(currentResult, currentName);
  $('import-status').hidden = false;
  $('import-status').textContent = guided
    ? `Guided example: Tehran precipitation, ${currentResult.period.start}–${currentResult.period.end}. Browser checks matched the recorded source hash and recalculated aggregation and point estimates. Uncertainty intervals are precomputed; full Python replay is available. Your notes are preserved.`
    : `${origin}. ${saved.verification.summary} ${saved.verification.limitations} Imported notes are user text, not verified findings. The form remains available to start another analysis.`;
  $('workspace-status').textContent = `Opened saved evidence for ${currentName}. No file was uploaded.`;
  persistWork();
}

async function renderWindows() {
  const result = currentResult;
  if (!result || !SNAPSHOT_MODE || !config?.windows) { $('window-section').hidden = true; return; }
  const key = Object.keys(config.presets).find(key => {
    const p = config.presets[key];
    return Math.abs(p.latitude-result.location.latitude)<.00001 && Math.abs(p.longitude-result.location.longitude)<.00001;
  });
  if (!key) { $('window-section').hidden = true; return; }
  if (windowRequest) windowRequest.abort();
  const request = new AbortController(); windowRequest = request;
  try {
    const records = await Promise.all(config.windows.map(async period => {
      const suffix = period.id === 'full45' ? '' : `-${period.id}`;
      const response = await fetch(`demo/${key}${suffix}-${result.variable}.json`, {signal: request.signal});
      if (!response.ok) throw new Error('Period comparison unavailable.');
      return {period, data: await response.json()};
    }));
    if (currentResult !== result || windowRequest !== request) return;
    if (records.some(row => row.data.provenance.payload_sha256 !== result.provenance.payload_sha256)) { $('window-section').hidden = true; return; }
    $('window-caption').textContent = `${currentName}. Rates in ${result.metadata.unit} per decade. Highlight: displayed period.`;
    $('window-body').replaceChildren(...records.map(({period,data}) => {
      const tr = document.createElement('tr');
      if (data.period.start === result.period.start && data.period.end === result.period.end) tr.setAttribute('aria-current','true');
      for (const value of [`${period.start}–${period.end}`, data.trend.years, signed(data.trend.slope_per_decade,3)]) {
        const td = document.createElement('td'); td.textContent = value; tr.append(td);
      }
      return tr;
    }));
    $('window-section').hidden = false;
  } catch (error) {
    if (currentResult === result && error.name !== 'AbortError') $('window-section').hidden = true;
  }
}

$('window').addEventListener('change', () => {
  if (!config) return;
  const period = config.windows.find(row => row.id === $('window').value);
  $('start').value = period.start; $('end').value = period.end;
});
$('explore-form').addEventListener('input', () => {
  if (!config) ++importSequence;
});
$('explore-form').addEventListener('change', () => {
  if (!config) ++importSequence;
});
$('copy-view-link').addEventListener('click', async () => {
  if (!SNAPSHOT_MODE || !globalThis.ClimateViewLinks) return;
  const result = currentResult;
  const selection = ClimateViewLinks.match(result, config, datasetComparison);
  if (!selection) { updateViewLink(); return; }
  const url = ClimateViewLinks.createURL(globalThis.location.href, selection, config);
  try {
    if (!globalThis.navigator?.clipboard?.writeText) throw new Error('Clipboard unavailable');
    await globalThis.navigator.clipboard.writeText(url);
    if (currentResult !== result) return;
    $('view-link-status').textContent = 'View link copied. It opens the public example and does not include your notes.';
  } catch {
    if (currentResult !== result) return;
    $('view-link-fallback').hidden = false;
    $('view-link-url').value = url;
    $('view-link-url').focus({preventScroll: true});
    $('view-link-url').select();
    $('view-link-status').textContent = 'The browser could not copy automatically. Select and copy the link below.';
  }
});
$('import-file').addEventListener('change', async event => {
  const file = event.target.files[0];
  if (!file) return;
  globalThis.ClimateStory?.pause();
  const sequence = ++importSequence;
  try {
    if (file.size > 2*1024*1024) throw new Error('Choose a JSON file no larger than 2 MiB.');
    await openInvestigation(await file.text(), 'Imported evidence', sequence);
  } catch (error) { if (sequence === importSequence) $('workspace-status').textContent = `Could not open file: ${error.message}`; }
  finally { event.target.value = ''; }
});
$('restore-work').addEventListener('click', async () => {
  globalThis.ClimateStory?.pause();
  const sequence = ++importSequence;
  try {
    const saved = await ClimateWorkspace.restore();
    if (sequence !== importSequence) return;
    if (!saved) { $('workspace-status').textContent = 'No investigation is saved in this browser. Import a downloaded JSON file instead.'; return; }
    await openInvestigation(JSON.stringify({format:'Climate Explorer investigation 1', analysis:{...saved.analysis,location_name:saved.locationName},notes:saved.notes}), 'Restored local evidence', sequence);
  } catch (error) { if (sequence === importSequence) $('workspace-status').textContent = `Could not restore local evidence: ${error.message}`; }
});
$('clear-work').addEventListener('click', () => {
  globalThis.ClimateStory?.pause();
  ++importSequence;
  $('save-locally').checked = false;
  try { ClimateWorkspace.clear(); $('workspace-status').textContent = 'Local saved copy cleared. Current tab and downloaded files remain available.'; }
  catch (error) { $('workspace-status').textContent = `Could not clear browser storage: ${error.message}`; }
});
$('save-locally').addEventListener('change', () => {
  if ($('save-locally').checked) persistWork();
  else {
    try { ClimateWorkspace.clear(); $('workspace-status').textContent = 'Local saving is off. The saved browser copy was cleared.'; }
    catch (error) { $('workspace-status').textContent = `Local saving is off, but the saved copy could not be cleared: ${error.message}`; }
  }
});
for (const id of ['investigation-question','investigation-interpretation','investigation-uncertainty']) $(id).addEventListener('input', persistWork);
window.addEventListener('beforeprint', () => {
  for (const id of ['investigation-question','investigation-interpretation','investigation-uncertainty']) {
    let paragraph = document.getElementById(`${id}-print`);
    if (!paragraph) { paragraph = document.createElement('p'); paragraph.id = `${id}-print`; paragraph.className = 'printed-note'; $(id).after(paragraph); }
    paragraph.textContent = $(id).value || '(No note entered)';
  }
});
$('print-investigation').addEventListener('click', () => { if (currentResult) window.print(); });

$('explore-form').addEventListener('submit', explore);
$('retry').addEventListener('click', () => config ? explore() : initialize());
$('location').addEventListener('change', updateLocation);
for (const id of ['latitude', 'longitude']) $(id).addEventListener('input', updateLocation);
for (const id of ['start', 'end']) $(id).addEventListener('input', () => $('end').setCustomValidity(''));
$('download-report').addEventListener('click', () => {
  if (!currentResult) return;
  download(JSON.stringify({ ...currentResult, location_name: currentName,
    method: 'OLS annual estimate and independent-error mean band. Newey-West conditional intervals, Theil-Sen slope, one-year influence, and fixed period checks. All settings, raw data, hashes, and versions are included. These checks do not guarantee calibrated real-data coverage or adjust for multiple exploration.',
    built_from: 'Climate Explorer prototype started 2026-11-11; competition eligibility not established.'
  }, null, 2), 'application/json', 'climate-explorer-analysis.json');
});
$('download-csv').addEventListener('click', event => {
  event.preventDefault();
  if (!currentResult) return;
  const r = currentResult;
  const quote = value => `"${String(value).replaceAll('"', '""')}"`;
  const rows = [['year', 'annual_value', 'unit', 'latitude', 'longitude', 'parameter', 'aggregation', 'source_url', 'retrieved_utc'], ...r.annual.map(row => [row.year, row.value, r.metadata.unit, r.location.latitude, r.location.longitude, r.metadata.parameter, r.metadata.aggregation, r.provenance.request_url, r.provenance.fetched_at])];
  download(rows.map(row => row.map(quote).join(',')).join('\r\n') + '\r\n', 'text/csv;charset=utf-8', 'climate-explorer-annual.csv');
});
$('download-investigation').addEventListener('click', () => {
  if (!currentResult) return;
  const r = currentResult;
  const comparison = r.period.start === 1981 && r.period.end === 2025 ? matchingComparison() : null;
  const report = {
    format: 'Climate Explorer investigation 1', saved_utc: new Date().toISOString(),
    notes: { question: $('investigation-question').value, interpretation: $('investigation-interpretation').value, remaining_uncertainty: $('investigation-uncertainty').value },
    evidence_summary: `${currentName}, ${r.trend.first_year}–${r.trend.last_year}: ordinary slope ${signed(r.trend.slope_per_decade, 3)} ${r.metadata.unit} per decade. Ordinary 95% interval ${r.trend.ci95_per_decade.map(v => signed(v, 3)).join(' to ')}. This interval assumes independent, normally distributed errors with constant variance. Method and date checks share the same data. No causal or forecast claim.`,
    source_comparison: comparison || null,
    analysis: { ...r, location_name: currentName },
    replay: 'Run evaluation/replay.py on this file. It verifies the nested analysis without using the network; it does not assess or endorse the user notes.',
    ai_assistance: 'Codex wrote and reviewed this application. User notes are entered by the person using the tool. See AI_ASSISTANCE.md in the public repository.',
  };
  download(JSON.stringify(report, null, 2), 'application/json', 'climate-explorer-investigation.json');
});
$('download-chart').addEventListener('click', () => {
  if (!currentResult) return;
  renderAnnual(currentResult, 900);
  const clone = $('annual-chart').cloneNode(true);
  renderAnnual(currentResult);
  clone.setAttribute('xmlns', NS);
  clone.setAttribute('viewBox', '0 -65 900 435');
  clone.setAttribute('width', '1200'); clone.setAttribute('height', '580');
  const style = node('style', {}, 'text{font-family:Arial,sans-serif;fill:#526c76;font-size:11px}.axis-title{fill:#183d47}.observation{stroke:white;stroke-width:1.5}');
  clone.prepend(node('rect', { x: 0, y: -65, width: 900, height: 435, fill: '#ffffff' }), style);
  clone.append(node('text', { x: 60, y: -40, 'font-size': 19 }, `Climate Explorer | ${currentName}`));
  clone.append(node('text', { x: 60, y: -19 }, `${currentResult.metadata.name}, ${currentResult.trend.first_year}–${currentResult.trend.last_year}. Annual values, linear trend, and 95% confidence band for fitted mean.`));
  clone.append(node('text', { x: 60, y: 341 }, `Source: NASA POWER / ${currentResult.provenance.sources.join(', ')}. Retrieved ${currentResult.provenance.fetched_at.slice(0, 10)} UTC.`));
  clone.append(node('text', { x: 60, y: 359 }, 'Exploratory OLS; independent, normally distributed errors assumed. Not a forecast. See analysis JSON for full provenance.'));
  download(new XMLSerializer().serializeToString(clone), 'image/svg+xml', 'climate-explorer-chart.svg');
});

async function initialize() {
  const sequence = importSequence;
  try {
    const response = await fetch(apiPath('config'));
    if (!response.ok) throw new Error('The app configuration could not be loaded. Restart the local server and refresh.');
    config = await response.json();
    const automatic = sequence === importSequence;
    $('start').min = config.first_year; $('start').max = config.last_year - 9;
    $('end').min = config.first_year + 9; $('end').max = config.last_year;
    if (automatic) $('end').value = config.last_year;
    if (SNAPSHOT_MODE) {
      $('demo-notice').hidden = false;
      $('location').querySelector('option[value="custom"]').remove();
      $('window-control').hidden = false;
      $('start').disabled = true; $('end').disabled = true;
      document.querySelector('.field-help').textContent = 'Choose one of four fixed periods ending in 2025. Keep the longest period as your starting point; short records may tell a different story.';
      if (automatic && globalThis.ClimateViewLinks) {
        const view = ClimateViewLinks.parse(globalThis.location?.search || '', config);
        $('location').value = view.selection.place;
        document.querySelector(`input[name="variable"][value="${view.selection.variable}"]`).checked = true;
        $('window').value = view.selection.period;
        const period = config.windows.find(row => row.id === view.selection.period);
        $('start').value = period.start; $('end').value = period.end;
        $('view-link-notice').hidden = view.status === 'default';
        $('view-link-notice').textContent = view.status === 'invalid' ? view.message : `Opened public example: ${config.presets[view.selection.place].name}, ${view.selection.variable === 'rainfall' ? 'precipitation' : 'temperature'}, ${period.start}–${period.end}. Notes are not included.`;
      } else if (automatic) $('start').value = config.first_year;
      else {
        const period = config.windows.find(row => row.id === $('window').value);
        if (period) { $('start').value = period.start; $('end').value = period.end; }
      }
    }
    fetch(apiPath('dataset-check')).then(response => {
      if (!response.ok) throw new Error('Source comparison unavailable.');
      return response.json();
    }).then(result => { datasetComparison = result; renderDatasetComparison(); }).catch(() => { datasetComparison = null; renderDatasetComparison(); });
    updateLocation();
    updateStorageControls();
    if (sequence === importSequence) await explore();
    else if (!currentResult && !activeRequest) {
      $('status').hidden = false;
      $('status').textContent = 'Your choices are ready. Choose Explore this place to load the selected example.';
    }
  } catch (error) {
    if (sequence !== importSequence) return;
    $('status').hidden = true; $('error').hidden = false;
    $('error-text').textContent = error.message;
  }
}

globalThis.ClimateStory?.mount({
  onIntent() {
    const sequence = ++importSequence;
    if (activeRequest) { activeRequest.abort(); activeRequest = null; }
    $('explore-button').disabled = false;
    $('status').hidden = true;
    $('results').setAttribute('aria-busy', 'false');
    if (currentResult) $('results').hidden = false;
    return sequence;
  },
  async openAnalysis(record, context) {
    if (context.intent !== importSequence || !context.isCurrent()) return false;
    await openInvestigation(JSON.stringify(record), 'Guided story evidence', context.intent, true);
    return context.intent === importSequence && context.isCurrent();
  },
  revealChart() {
    $('chart-title').setAttribute('tabindex', '-1');
    $('chart-title').focus({preventScroll: true});
    $('chart-title').scrollIntoView({block: 'start', behavior: 'auto'});
  },
  exploreOwn() {
    $('location').focus({preventScroll: true});
    $('location').scrollIntoView({block: 'center', behavior: 'auto'});
  },
});

initialize();

let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (currentResult && !$('results').hidden) {
      renderAnnual(currentResult);
      renderChecks(currentResult);
    }
  }, 120);
});
