'use strict';

globalThis.ClimateWindowAtlas = (() => {
  const FORMAT = 'Climate Explorer window atlas 1';
  const MAX_BYTES = 8 * 1024 * 1024;
  const PAGE_SIZE = 30;
  const SCOPE = [
    'Every contiguous calendar window meeting the recorded minimum span is enumerated, not just windows supporting a preferred result.',
    'Changing dates changes the period being estimated. Overlapping windows are not independent replications.',
    'Slope ranges and counts describe this finite collection of windows. They are not confidence intervals, probabilities of direction, or measures of truth.',
    'Each ordinary and Newey-West interval remains conditional on its own error assumptions. None is adjusted for searching across windows.',
    'This atlas supplies no joint significance test, multiple-testing correction, causal attribution, forecast, or guarantee against selective interpretation.',
  ];
  const NS = 'http://www.w3.org/2000/svg';
  const $ = id => document.getElementById(id);
  const key = row => `${row.start}-${row.end}`;
  let options, current, place, placeName, caseId, pack, selected, displayed = [], page = 0;
  let generation = 0, request, mounted = false, cells = new Map();

  function requireValue(condition, message) {
    if (!condition) throw new Error(message);
  }

  function close(left, right) {
    return Number.isFinite(left) && Math.abs(left - right) <= 1e-8 * Math.max(1, Math.abs(right));
  }

  function slope(rows) {
    const mx = rows.reduce((sum, row) => sum + row.year, 0) / rows.length;
    const my = rows.reduce((sum, row) => sum + row.value, 0) / rows.length;
    let xy = 0, xx = 0;
    for (const row of rows) { xy += (row.year - mx) * (row.value - my); xx += (row.year - mx) ** 2; }
    return xy / xx * 10;
  }

  async function validate(data) {
    requireValue(data?.format === FORMAT && data.base_analysis && Array.isArray(data.windows) && JSON.stringify(data.scope) === JSON.stringify(SCOPE), 'Unsupported window atlas format or missing interpretation limits.');
    const base = (await ClimateWorkspace.importText(JSON.stringify(data.base_analysis))).analysis;
    requireValue(data.basis?.source_payload_sha256 === base.provenance.payload_sha256 && data.basis?.analysis_code_sha256 === base.analysis.code_sha256 && data.basis?.variable === base.variable && data.basis?.unit === base.metadata.unit && data.basis?.location?.latitude === base.location.latitude && data.basis?.location?.longitude === base.location.longitude && data.basis?.period?.start === base.period.start && data.basis?.period?.end === base.period.end, 'Atlas basis differs from its source analysis.');
    const minimum = data.specification?.minimum_calendar_years;
    requireValue(minimum === 10 && data.specification.minimum_complete_years === 10, 'This atlas requires both ten calendar years and ten complete years.');
    const expected = [];
    for (let start = base.period.start; start <= base.period.end - minimum + 1; start++) {
      for (let end = start + minimum - 1; end <= base.period.end; end++) expected.push([start, end]);
    }
    requireValue(data.windows.length === expected.length && expected.length <= 2000, 'The atlas is not the complete bounded window set.');
    data.windows.forEach((row, index) => {
      const [start, end] = expected[index];
      const annual = base.annual.filter(item => item.year >= start && item.year <= end);
      requireValue(row.start === start && row.end === end && row.calendar_years === end - start + 1 && row.complete_years === annual.length && row.available === (annual.length >= 10), 'Atlas calendar enumeration or coverage differs from the source.');
      if (row.available) {
        const interval = row.ordinary_ci95_per_decade;
        const recorded = row.trend?.ci95_per_decade;
        requireValue(close(row.slope_per_decade, slope(annual)) && close(row.trend?.slope_per_decade, row.slope_per_decade), 'An atlas point estimate does not match the frozen annual values.');
        requireValue(Array.isArray(interval) && interval.length === 2 && interval.every(Number.isFinite) && interval[0] <= interval[1] && Array.isArray(recorded) && recorded.length === 2 && recorded.every((value, i) => close(value, interval[i])), 'An atlas interval is malformed or inconsistent.');
      } else requireValue(typeof row.reason === 'string' && row.reason.length <= 1000, 'An unavailable window needs an explanation.');
    });
    requireValue(data.summary?.candidate_windows === expected.length && data.summary.available_windows === data.windows.filter(row => row.available).length, 'Atlas counts do not match the enumerated windows.');
    return data;
  }

  function materialize(data, row) {
    requireValue(row.available, 'This window has fewer than ten complete years and has no fitted result.');
    const record = {...data.base_analysis, period: {start: row.start, end: row.end}, trend: row.trend, checks: row.checks};
    delete record.window_context;
    for (const field of ['annual', 'monthly']) record[field] = data.base_analysis[field].filter(item => item.year >= row.start && item.year <= row.end);
    record.excluded_years = data.base_analysis.excluded_years.filter(year => year >= row.start && year <= row.end);
    record.window_atlas_context = {format: FORMAT, minimum_calendar_years: 10, candidate_windows: data.windows.length, scope: data.scope};
    return record;
  }

  function signed(value) {
    return `${value > 0 ? '+' : value < 0 ? '−' : ''}${Math.abs(value).toFixed(3)}`;
  }

  function unit() { return `${pack.base_analysis.metadata.unit} per decade`; }

  function svg(tag, attributes, content = '') {
    const element = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
    if (content) element.textContent = content;
    return element;
  }

  function choose(row, focus = false) {
    selected = row;
    $('atlas-selected').textContent = row.available
      ? `${row.start}–${row.end}: ${row.complete_years} complete years. Fitted rate ${signed(row.slope_per_decade)} ${unit()}. Ordinary 95% interval ${signed(row.ordinary_ci95_per_decade[0])} to ${signed(row.ordinary_ci95_per_decade[1])}. This interval is precomputed and conditional on independent, normally distributed, constant-variance errors.`
      : `${row.start}–${row.end}: ${row.complete_years} complete years. ${row.reason}`;
    $('atlas-open').disabled = !row.available;
    $('atlas-selection-hidden').hidden = displayed.some(item => key(item) === key(row));
    for (const [id, cell] of cells) {
      cell.setAttribute('aria-pressed', String(id === key(row)));
      cell.setAttribute('tabindex', id === key(row) ? '0' : '-1');
      cell.classList.toggle('atlas-selected-cell', id === key(row));
    }
    if (!cells.has(key(row)) && cells.size) cells.values().next().value.setAttribute('tabindex', '0');
    if (focus) $('atlas-selected').focus({preventScroll: true});
  }

  function color(row, maximum) {
    if (!row.available) return '#c8cfd2';
    const base = row.slope_per_decade < 0 ? [150, 78, 111] : [20, 124, 137];
    const strength = .15 + .85 * Math.min(1, Math.abs(row.slope_per_decade) / (maximum || 1));
    return `rgb(${base.map(value => Math.round(255 + (value - 255) * strength)).join(',')})`;
  }

  function draw() {
    const base = pack.base_analysis, minimum = pack.specification.minimum_calendar_years;
    const count = base.period.end - base.period.start - minimum + 2;
    const stepSize = 14, left = 60, top = 38, size = count * stepSize;
    const width = left + size + 18, height = top + size + 45;
    const maximum = Math.max(...pack.windows.filter(row => row.available).map(row => Math.abs(row.slope_per_decade)));
    const nodes = [svg('title', {}, 'Window sensitivity: start year by end year'), svg('desc', {}, 'Each square is a requested period. Teal is a positive fitted rate, plum a negative rate. Arrow keys move among displayed windows. The table provides the same values. Color scale uses the full atlas, even when display filters change.')];
    cells = new Map();
    for (let year = base.period.start; year <= base.period.end - minimum + 1; year++) {
      if (year === base.period.start || year % 5 === 0) nodes.push(svg('text', {x: left - 8, y: top + (year - base.period.start + .75) * stepSize, 'text-anchor': 'end'}, String(year)));
    }
    for (let year = base.period.start + minimum - 1; year <= base.period.end; year++) {
      if (year === base.period.end || year % 5 === 0) nodes.push(svg('text', {x: left + (year - base.period.start - minimum + 1.5) * stepSize, y: top + size + 18, 'text-anchor': 'middle'}, String(year)));
    }
    nodes.push(svg('text', {x: left, y: 17}, 'Start year ↓'));
    nodes.push(svg('text', {x: left + size, y: height - 4, 'text-anchor': 'end'}, 'End year →'));
    for (const row of displayed) {
      const label = row.available ? `${row.start}–${row.end}, ${row.complete_years} complete years, ${signed(row.slope_per_decade)} ${unit()}` : `${row.start}–${row.end}, unavailable: ${row.reason}`;
      const cell = svg('rect', {x: left + (row.end - base.period.start - minimum + 1) * stepSize, y: top + (row.start - base.period.start) * stepSize, width: 12.5, height: 12.5, rx: 1, fill: color(row, maximum), role: 'button', tabindex: '-1', 'aria-label': label, 'aria-pressed': 'false'});
      cell.append(svg('title', {}, label));
      cell.addEventListener('click', () => choose(row));
      cell.addEventListener('focus', () => choose(row));
      cell.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(row); return; }
        let next;
        if (event.key === 'Home') next = displayed[0];
        else if (event.key === 'End') next = displayed.at(-1);
        else if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
          const direction = event.key === 'ArrowRight' ? 1 : -1;
          next = displayed.filter(item => item.start === row.start && (item.end - row.end) * direction > 0).sort((a, b) => Math.abs(a.end - row.end) - Math.abs(b.end - row.end))[0];
        } else if (['ArrowUp', 'ArrowDown'].includes(event.key)) {
          const direction = event.key === 'ArrowDown' ? 1 : -1;
          next = displayed.filter(item => item.end === row.end && (item.start - row.start) * direction > 0).sort((a, b) => Math.abs(a.start - row.start) - Math.abs(b.start - row.start))[0];
        } else return;
        event.preventDefault();
        if (next) cells.get(key(next)).focus();
      });
      cells.set(key(row), cell); nodes.push(cell);
    }
    $('atlas-chart').setAttribute('viewBox', `0 0 ${width} ${height}`);
    $('atlas-chart').replaceChildren(...nodes);
  }

  function table() {
    const rows = displayed.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
    $('atlas-table-body').replaceChildren(...rows.map(row => {
      const tr = document.createElement('tr'), td = document.createElement('td'), button = document.createElement('button');
      button.type = 'button'; button.className = 'atlas-period-button'; button.textContent = `${row.start}–${row.end}`;
      button.addEventListener('click', () => choose(row, true)); td.append(button); tr.append(td);
      for (const value of [row.complete_years, row.available ? signed(row.slope_per_decade) : 'Unavailable', row.available ? `${signed(row.ordinary_ci95_per_decade[0])} to ${signed(row.ordinary_ci95_per_decade[1])}` : row.reason]) {
        const cell = document.createElement('td'); cell.textContent = value; tr.append(cell);
      }
      return tr;
    }));
    const totalPages = Math.max(1, Math.ceil(displayed.length / PAGE_SIZE));
    $('atlas-page-status').textContent = `Page ${page + 1} of ${totalPages}. Ordered by start year, then end year.`;
    $('atlas-page-previous').disabled = page === 0;
    $('atlas-page-next').disabled = page + 1 >= totalPages;
    $('atlas-table-caption').textContent = `Displayed windows. Rates and ordinary intervals in ${unit()}. These are overlapping periods, not independent evidence.`;
  }

  function filter() {
    const minimum = Number($('atlas-minimum').value), direction = $('atlas-direction').value;
    displayed = pack.windows.filter(row => row.calendar_years >= minimum && (direction === 'all' || row.available && (direction === 'positive' ? row.slope_per_decade > 0 : direction === 'negative' ? row.slope_per_decade < 0 : row.slope_per_decade === 0)));
    page = 0;
    $('atlas-counts').textContent = `Showing ${displayed.length} of ${pack.windows.length} enumerated windows. ${pack.summary.available_windows} have at least ten complete years. Filters change the display only; they do not recompute any estimate or create independent tests.`;
    draw(); table();
    if (selected) choose(selected);
  }

  function sourceNote() {
    if (!pack) return;
    const base = pack.base_analysis;
    const differs = current?.provenance?.payload_sha256 !== base.provenance.payload_sha256;
    $('atlas-source-note').textContent = `${base.location_name || place}, ${base.metadata.name.toLowerCase()}. Retained NASA response retrieved ${base.provenance.fetched_at.slice(0, 10)} UTC. ${differs ? 'This retained response differs from the current chart source. Opening a window switches the chart to this frozen evidence.' : 'This atlas and the current chart use the same raw-source hash.'}`;
    $('atlas-source-link').href = base.provenance.request_url;
    $('atlas-source-hash').textContent = base.provenance.payload_sha256;
  }

  function pause() {
    ++generation;
    if (request) request.abort();
    request = null;
    if (mounted) { $('atlas-load').disabled = !caseId; if (selected) $('atlas-open').disabled = !selected.available; }
  }

  function setAnalysis(analysis, config) {
    if (!mounted) return;
    current = analysis;
    const next = Object.keys(config?.presets || {}).find(id => ['tehran', 'ankara', 'berlin', 'toronto', 'milan'].includes(id) && Math.abs(config.presets[id].latitude - analysis?.location?.latitude) < .00001 && Math.abs(config.presets[id].longitude - analysis?.location?.longitude) < .00001);
    placeName = next ? config.presets[next].name : null;
    const nextCase = next && ['temperature', 'rainfall'].includes(analysis.variable) ? `${next}-${analysis.variable}` : null;
    if (caseId !== nextCase) {
      pause(); caseId = nextCase; place = next; pack = null; selected = null; displayed = [];
      $('atlas-content').hidden = true; $('atlas-status').textContent = '';
      $('atlas-load').disabled = !caseId;
      $('atlas-load').textContent = caseId ? `Load the ${config.presets[next].name.split(',')[0]} ${analysis.metadata.name.toLowerCase()} atlas` : 'Choose a preset location to load its atlas';
    }
    sourceNote();
  }

  async function load() {
    if (!caseId) return;
    const sequence = ++generation, expectedCase = caseId;
    if (request) request.abort();
    request = new AbortController(); const active = request;
    $('atlas-load').disabled = true; $('atlas-status').textContent = 'Loading and checking the complete window set from retained NASA data…';
    try {
      const response = await fetch(`atlas/${expectedCase}.json`, {signal: active.signal});
      requireValue(response.ok, 'The retained atlas is unavailable. The main investigation remains usable.');
      const content = await response.text();
      requireValue(new TextEncoder().encode(content).length <= MAX_BYTES, 'The atlas file exceeds the 8 MiB limit.');
      const data = await validate(JSON.parse(content));
      if (sequence !== generation || expectedCase !== caseId) return;
      const [latitude, longitude] = [current.location.latitude, current.location.longitude];
      requireValue(data.base_analysis.variable === current.variable && Math.abs(data.base_analysis.location.latitude - latitude) < .00001 && Math.abs(data.base_analysis.location.longitude - longitude) < .00001, 'The atlas case differs from the selected location or variable.');
      pack = data;
      selected = pack.windows.find(row => row.start === current.period.start && row.end === current.period.end) || pack.windows.find(row => row.start === pack.base_analysis.period.start && row.end === pack.base_analysis.period.end);
      $('atlas-content').hidden = false;
      $('atlas-minimum').value = '10'; $('atlas-direction').value = 'all';
      filter(); sourceNote();
      $('atlas-download').href = `atlas/${expectedCase}.json`;
      $('atlas-status').textContent = 'Complete window set loaded. Select a square or a table row, then open its evidence. Browser checks recalculate point slopes; displayed uncertainty intervals are precomputed.';
    } catch (error) {
      if (sequence === generation && error.name !== 'AbortError') $('atlas-status').textContent = `Atlas could not load: ${error.message}`;
    } finally { if (sequence === generation) { request = null; $('atlas-load').disabled = false; } }
  }

  async function open() {
    if (!pack || !selected?.available) return;
    const sequence = ++generation, row = selected;
    const intent = options.onIntent();
    $('atlas-open').disabled = true;
    $('atlas-status').textContent = `Checking the selected ${row.start}–${row.end} evidence…`;
    try {
      const record = materialize(pack, row);
      record.location_name = placeName || record.location_name || place;
      const verified = await ClimateWorkspace.importText(JSON.stringify(record));
      if (sequence !== generation) return;
      const opened = await options.openAnalysis(verified.analysis, {intent, isCurrent: () => sequence === generation});
      if (sequence !== generation || !opened) return;
      $('atlas-status').textContent = `Opened ${row.start}–${row.end} from this frozen atlas. Your notes are preserved. Opening a selected window does not correct for examining many overlapping windows.`;
      options.revealChart();
    } catch (error) { if (sequence === generation) $('atlas-status').textContent = `Selected evidence could not open: ${error.message}`; }
    finally { if (sequence === generation) $('atlas-open').disabled = !selected?.available; }
  }

  function mount(callbacks) {
    if (mounted) return;
    mounted = true; options = callbacks;
    $('atlas-load').addEventListener('click', load);
    $('atlas-open').addEventListener('click', open);
    for (const id of ['atlas-minimum', 'atlas-direction']) $(id).addEventListener('change', () => { if (pack) filter(); });
    $('atlas-page-previous').addEventListener('click', () => { if (page > 0) { page--; table(); } });
    $('atlas-page-next').addEventListener('click', () => { if ((page + 1) * PAGE_SIZE < displayed.length) { page++; table(); } });
  }

  return Object.freeze({mount, setAnalysis, pause, validate, materialize});
})();
