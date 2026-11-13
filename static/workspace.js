'use strict';

globalThis.ClimateWorkspace = (() => {
  const MAX_BYTES = 2 * 1024 * 1024;
  const STORAGE_KEY = 'climate-explorer.workspace.v1';
  const NOTE_KEYS = ['question', 'interpretation', 'remaining_uncertainty'];
  const NOTE_LIMITS = {question: 2000, interpretation: 4000, remaining_uncertainty: 2000};
  let saveGeneration = 0;
  const HASH_FORMAT = 'SHA256 of Python sorted-key compact JSON after converting integral floats to integers, including negative zero';
  const LIMITATIONS = 'Browser checks verify the raw-source hash, calendar aggregation, and slope sensitivity calculations. They do not recompute confidence intervals, p-values, residual correlation, or uncertainty bands. Use evaluation/replay.py for the full numerical replay. A matching hash does not authenticate NASA data, verify the notes, or establish scientific validity.';

  function requireValue(condition, message) {
    if (!condition) throw new Error(message);
  }

  function object(value, field) {
    requireValue(value !== null && typeof value === 'object' && !Array.isArray(value), `Missing or invalid ${field}.`);
    return value;
  }

  function text(value, field, maximum = 1000) {
    requireValue(typeof value === 'string' && value.length <= maximum, `Invalid or oversized ${field}.`);
    return value;
  }

  function finite(value, field) {
    requireValue(typeof value === 'number' && Number.isFinite(value), `Invalid finite number at ${field}.`);
    return value;
  }

  function integer(value, field) {
    requireValue(Number.isSafeInteger(value), `Invalid integer at ${field}.`);
    return value;
  }

  function close(actual, expected, field) {
    finite(actual, field);
    requireValue(Math.abs(actual - expected) <= 1e-8 * Math.max(1, Math.abs(expected)), `Recomputed value differs at ${field}.`);
  }

  function inspect(value, depth = 0, state = {nodes: 0}) {
    requireValue(depth <= 24 && ++state.nodes <= 100000, 'The file is too deeply nested or complex.');
    if (typeof value === 'number') {
      requireValue(Number.isFinite(value) && Math.abs(value) <= Number.MAX_SAFE_INTEGER, 'The file contains an unsupported or non-finite number.');
    } else if (typeof value === 'string') {
      requireValue(value.length <= 65536, 'The file contains an oversized text field.');
    } else if (value !== null && typeof value === 'object') {
      for (const key of Object.keys(value)) {
        requireValue(!['__proto__', 'constructor', 'prototype'].includes(key), 'The file contains an unsafe object key.');
        requireValue(key.length <= 256, 'The file contains an oversized object key.');
        inspect(value[key], depth + 1, state);
      }
    }
  }

  function codePointOrder(left, right) {
    const a = Array.from(left), b = Array.from(right);
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      const difference = a[i].codePointAt(0) - b[i].codePointAt(0);
      if (difference) return difference;
    }
    return a.length - b.length;
  }

  function sourceJSON(value) {
    if (value === null || typeof value === 'boolean') return String(value);
    if (typeof value === 'string') return JSON.stringify(value).replace(/[\u007f-\uffff]/g, char => `\\u${char.charCodeAt(0).toString(16).padStart(4, '0')}`);
    if (typeof value === 'number') {
      finite(value, 'source payload');
      requireValue(Math.abs(value) <= Number.MAX_SAFE_INTEGER, 'Source number exceeds the browser verification limit.');
      if (Number.isInteger(value)) return String(value === 0 ? 0 : value);
      if (Math.abs(value) < .0001) {
        const [mantissa, exponent] = value.toExponential().split('e');
        return `${mantissa}e${Number(exponent) < 0 ? '-' : '+'}${String(Math.abs(Number(exponent))).padStart(2, '0')}`;
      }
      return JSON.stringify(value);
    }
    if (Array.isArray(value)) return `[${value.map(sourceJSON).join(',')}]`;
    object(value, 'source payload');
    return `{${Object.keys(value).sort(codePointOrder).map(key => `${sourceJSON(key)}:${sourceJSON(value[key])}`).join(',')}}`;
  }

  async function sourceHash(payload) {
    requireValue(globalThis.crypto?.subtle, 'Browser verification needs a secure page with Web Crypto. Open the HTTPS demonstration or the local app.');
    const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(sourceJSON(payload)));
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
  }

  function daysInMonth(year, month) {
    if (month === 2) return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 29 : 28;
    return [4, 6, 9, 11].includes(month) ? 30 : 31;
  }

  function aggregate(record) {
    const parameter = record.variable === 'temperature' ? 'T2M' : 'PRECTOTCORR';
    const expectedUnit = record.variable === 'temperature' ? ['C', '°C'] : ['mm/day'];
    const payload = object(record.raw_source, 'raw source');
    const descriptor = object(object(payload.parameters, 'NASA parameters')[parameter], 'NASA parameter units');
    requireValue(expectedUnit.includes(descriptor.units), 'NASA parameter units do not match this variable.');
    const raw = object(object(object(payload.properties, 'NASA properties').parameter, 'NASA measurements')[parameter], 'NASA monthly measurements');
    const fill = payload.header?.fill_value ?? -999;
    const annual = [], monthly = [], excluded = [];
    for (let year = record.period.start; year <= record.period.end; year++) {
      let total = 0, totalDays = 0, complete = true;
      for (let month = 1; month <= 12; month++) {
        const value = raw[`${year}${String(month).padStart(2, '0')}`];
        const valid = typeof value === 'number' && Number.isFinite(value) && value !== fill && (record.variable !== 'rainfall' || value >= 0);
        const days = daysInMonth(year, month);
        monthly.push({year, month, value: valid ? (record.variable === 'rainfall' ? value * days : value) : null});
        if (valid) { total += value * days; totalDays += days; }
        else complete = false;
      }
      if (complete) annual.push({year, value: record.variable === 'temperature' ? total / totalDays : total});
      else excluded.push(year);
    }
    return {annual, monthly, excluded};
  }

  function fit(rows) {
    const meanYear = rows.reduce((sum, row) => sum + row.year, 0) / rows.length;
    const mean = rows.reduce((sum, row) => sum + row.value, 0) / rows.length;
    let numerator = 0, denominator = 0;
    for (const row of rows) {
      numerator += (row.year - meanYear) * (row.value - mean);
      denominator += (row.year - meanYear) ** 2;
    }
    return {slope: numerator / denominator, meanYear, mean};
  }

  function direction(value) {
    return value > 1e-12 ? 'positive' : value < -1e-12 ? 'negative' : 'zero';
  }

  function pair(value, field) {
    requireValue(Array.isArray(value) && value.length === 2, `Invalid ${field}.`);
    value.forEach(number => finite(number, field));
    requireValue(value[0] <= value[1], `Reversed bounds at ${field}.`);
  }

  function validateTrend(record, annual) {
    const trend = object(record.trend, 'trend');
    const computed = fit(annual), first = annual[0].year, last = annual.at(-1).year;
    requireValue(trend.years === annual.length && trend.first_year === first && trend.last_year === last, 'Trend coverage does not match the complete years.');
    close(trend.slope_per_decade, computed.slope * 10, 'ordinary slope');
    close(trend.mean, computed.mean, 'annual mean');
    close(trend.fitted_change, computed.slope * (last - first), 'fitted change');
    pair(trend.ci95_per_decade, 'ordinary interval');
    requireValue(['positive', 'negative', 'unclear'].includes(trend.evidence), 'Invalid ordinary evidence label.');
    const [low, high] = trend.ci95_per_decade;
    requireValue(trend.evidence === (low > 0 ? 'positive' : high < 0 ? 'negative' : 'unclear'), 'Ordinary evidence label disagrees with its interval.');
    requireValue(finite(trend.p_value, 'p-value') >= 0 && trend.p_value <= 1, 'Invalid p-value.');
    requireValue(finite(trend.r_squared, 'R squared') >= 0 && trend.r_squared <= 1 + 1e-12, 'Invalid R squared.');
    requireValue(trend.lag1_residual_correlation === null || Math.abs(finite(trend.lag1_residual_correlation, 'residual correlation')) <= 1, 'Invalid residual correlation.');
    requireValue(Array.isArray(trend.line) && trend.line.length === annual.length, 'Invalid fitted line.');
    trend.line.forEach((row, i) => {
      object(row, 'fitted line row');
      requireValue(row.year === annual[i].year, 'Fitted line years do not match.');
      close(row.value, computed.mean + computed.slope * (row.year - computed.meanYear), 'fitted line');
      pair([row.low, row.high], 'mean band');
      requireValue(row.low <= row.value + 1e-8 && row.high >= row.value - 1e-8, 'Mean band does not contain its fitted line.');
    });
    return computed;
  }

  function validateChecks(record, annual, computed) {
    const checks = object(record.checks, 'sensitivity checks');
    const consecutive = annual.every((row, i) => i === 0 || row.year === annual[i - 1].year + 1);
    requireValue(checks.hac_available === consecutive, 'Missing-year dependence status does not match.');
    requireValue(Array.isArray(checks.intervals) && checks.intervals.length === (consecutive ? 4 : 1), 'Invalid sensitivity interval count.');
    checks.intervals.forEach(row => {
      object(row, 'sensitivity interval');
      text(row.method, 'interval method', 120);
      requireValue(row.lag === null || Number.isSafeInteger(row.lag) && row.lag >= 0 && row.lag <= 150, 'Invalid interval lag.');
      close(row.slope_per_decade, computed.slope * 10, 'sensitivity interval slope');
      pair(row.ci95_per_decade, 'sensitivity interval');
      const [low, high] = row.ci95_per_decade;
      requireValue(row.evidence === (low > 1e-12 ? 'positive' : high < -1e-12 ? 'negative' : 'unclear'), 'Sensitivity evidence label disagrees with its interval.');
    });
    requireValue(typeof checks.interval_conclusions_agree === 'boolean', 'Invalid interval agreement label.');
    requireValue(checks.interval_conclusions_agree === (checks.intervals.length > 1 && new Set(checks.intervals.map(row => row.evidence)).size === 1), 'Interval agreement label does not match.');
    const slopes = [];
    annual.forEach((row, i) => annual.slice(i + 1).forEach(next => slopes.push((next.value - row.value) / (next.year - row.year))));
    slopes.sort((a, b) => a - b);
    const middle = Math.floor(slopes.length / 2);
    const median = slopes.length % 2 ? slopes[middle] : (slopes[middle - 1] + slopes[middle]) / 2;
    close(checks.theil_sen_slope_per_decade, median * 10, 'Theil-Sen slope');
    const removed = annual.map((row, i) => fit(annual.filter((_, index) => index !== i)).slope * 10);
    const influence = object(checks.leave_one_out, 'one-year influence');
    close(influence.minimum_slope_per_decade, Math.min(...removed), 'minimum one-year influence');
    close(influence.maximum_slope_per_decade, Math.max(...removed), 'maximum one-year influence');
    for (const key of ['year_removed_for_minimum', 'year_removed_for_maximum']) requireValue(annual.some(row => row.year === influence[key]), 'Influence year is outside the complete record.');
    requireValue(influence.direction_changes === removed.some(slope => direction(slope) !== direction(computed.slope * 10)), 'One-year direction-change label does not match.');
    requireValue(Array.isArray(checks.periods) && checks.periods.length === 4, 'Invalid fixed period checks.');
    const {start, end} = record.period;
    const windows = [[start, end], [start + 5, end], [start, end - 5], [start + 5, end - 5]];
    checks.periods.forEach((row, i) => {
      object(row, 'fixed period');
      text(row.label, 'period label', 120);
      const [first, last] = windows[i];
      const selected = annual.filter(item => item.year >= first && item.year <= last);
      const available = last >= first && selected.length >= 10;
      requireValue(row.requested_start === first && row.requested_end === last && row.years === selected.length && row.available === available, 'Fixed period coverage does not match.');
      if (available) {
        const slope = fit(selected).slope * 10;
        requireValue(row.first_year === selected[0].year && row.last_year === selected.at(-1).year && row.direction === direction(slope), 'Fixed period direction or years do not match.');
        close(row.slope_per_decade, slope, 'fixed period slope');
      } else text(row.reason, 'unavailable period reason', 500);
    });
    requireValue(checks.period_direction_changes === checks.periods.some(row => row.available && row.direction !== direction(computed.slope * 10)), 'Fixed period direction-change label does not match.');
    requireValue(Array.isArray(checks.messages) && checks.messages.length <= 30, 'Invalid check messages.');
    checks.messages.forEach(message => text(message, 'check message', 1000));
    text(checks.scope, 'check scope', 2000);
    text(checks.calibration_caution, 'calibration caution', 2000);
  }

  function validateSource(record) {
    const provenance = object(record.provenance, 'provenance');
    requireValue(provenance.provider === 'NASA POWER', 'This import supports NASA POWER analysis exports only.');
    requireValue(provenance.payload_hash_format === HASH_FORMAT, 'Unsupported source hash format. Use an export from version 0.2.1 or later.');
    requireValue(/^[a-f0-9]{64}$/.test(text(provenance.payload_sha256, 'source hash', 64)), 'Invalid source hash.');
    const url = new URL(text(provenance.request_url, 'NASA request URL', 2000));
    requireValue(url.protocol === 'https:' && url.hostname === 'power.larc.nasa.gov' && !url.username && !url.password && !url.port && url.pathname === '/api/temporal/monthly/point' && !url.hash, 'The recorded source is not the supported HTTPS NASA POWER endpoint.');
    for (const [key, expected] of [['latitude', record.location.latitude], ['longitude', record.location.longitude]]) {
      requireValue(url.searchParams.getAll(key).length === 1 && url.searchParams.get(key).trim() !== '' && Number.isFinite(Number(url.searchParams.get(key))) && Math.abs(Number(url.searchParams.get(key)) - expected) <= .00005, 'Source request coordinates do not match the analysis.');
    }
    requireValue(['start', 'end'].every(key => url.searchParams.getAll(key).length === 1 && /^\d{4}$/.test(url.searchParams.get(key))) && Number(url.searchParams.get('start')) <= record.period.start && Number(url.searchParams.get('end')) >= record.period.end, 'Source request period does not cover the analysis.');
    requireValue([['parameters', 'T2M,PRECTOTCORR'], ['format', 'JSON'], ['community', 'AG']].every(([key, value]) => url.searchParams.getAll(key).length === 1 && url.searchParams.get(key) === value), 'Unsupported NASA request parameters.');
    requireValue(Array.isArray(provenance.sources) && provenance.sources.length <= 20, 'Invalid source names.');
    provenance.sources.forEach(source => text(source, 'source name', 100));
    requireValue(Number.isFinite(Date.parse(text(provenance.fetched_at, 'retrieval date', 100))), 'Invalid retrieval date.');
    text(provenance.delivery, 'delivery description', 500);
    requireValue(provenance.api_version === null || typeof provenance.api_version === 'string' || typeof provenance.api_version === 'number', 'Invalid source API version.');
    const spatial = object(provenance.spatial_resolution, 'spatial resolution');
    text(spatial.description, 'spatial description', 1000);
  }

  function notesFrom(value = {}) {
    object(value, 'notes');
    return Object.fromEntries(NOTE_KEYS.map(key => [key, text(value[key] ?? '', `note ${key}`, NOTE_LIMITS[key])]));
  }

  async function importText(contents) {
    requireValue(typeof contents === 'string' && new TextEncoder().encode(contents).length <= MAX_BYTES, 'Choose a JSON file no larger than 2 MiB.');
    let parsed;
    try { parsed = JSON.parse(contents); }
    catch { throw new Error('The file is not valid JSON.'); }
    inspect(parsed);
    object(parsed, 'analysis file');
    const wrapped = parsed.format === 'Climate Explorer investigation 1';
    const record = object(wrapped ? parsed.analysis : parsed, 'analysis');
    const period = object(record.period, 'analysis period');
    integer(period.start, 'start year'); integer(period.end, 'end year');
    requireValue(period.start >= 1981 && period.end <= new Date().getUTCFullYear() - 1 && period.end - period.start >= 9 && period.end - period.start < 150, 'Choose a record covering 10 to 150 complete years from 1981 onward.');
    requireValue(['temperature', 'rainfall'].includes(record.variable), 'Unsupported climate variable.');
    const location = object(record.location, 'location');
    requireValue(Math.abs(finite(location.latitude, 'latitude')) <= 90 && Math.abs(finite(location.longitude, 'longitude')) <= 180, 'Coordinates are outside the supported range.');
    const metadata = object(record.metadata, 'metadata');
    const expected = record.variable === 'temperature'
      ? {parameter: 'T2M', unit: '°C', monthly_unit: '°C', name: 'Temperature', aggregation: 'Day-weighted annual mean'}
      : {parameter: 'PRECTOTCORR', unit: 'mm/year', monthly_unit: 'mm/month', name: 'Precipitation', aggregation: 'Sum of monthly precipitation totals'};
    for (const key of Object.keys(expected)) requireValue(metadata[key] === expected[key], `Unsupported metadata ${key}.`);
    const analysis = object(record.analysis, 'analysis settings');
    text(object(analysis.settings, 'method settings').version, 'method version', 40);
    requireValue(/^[a-f0-9]{64}$/.test(text(analysis.code_sha256, 'code fingerprint', 64)), 'Invalid code fingerprint.');
    requireValue(/^\d{4}-\d{2}-\d{2}$/.test(text(analysis.build_started, 'build start date', 10)), 'Invalid build start date.');
    const versions = object(analysis.versions, 'dependency versions');
    for (const key of ['python', 'numpy', 'scipy', 'statsmodels']) text(versions[key], `${key} version`, 80);
    validateSource(record);
    const digest = await sourceHash(record.raw_source);
    requireValue(digest === record.provenance.payload_sha256, 'The raw-source hash does not match. The file may have changed.');
    const aggregated = aggregate(record);
    requireValue(aggregated.annual.length >= 10, 'Fewer than ten complete years remain in the raw source.');
    requireValue(Array.isArray(record.annual) && record.annual.length === aggregated.annual.length && Array.isArray(record.monthly) && record.monthly.length === aggregated.monthly.length, 'Annual or monthly coverage does not match the raw source.');
    for (const key of ['annual', 'monthly']) record[key].forEach((row, i) => {
      object(row, `${key} row`);
      const expectedRow = aggregated[key][i];
      requireValue(row.year === expectedRow.year && (key !== 'monthly' || row.month === expectedRow.month), `${key} calendar order does not match.`);
      if (expectedRow.value === null) requireValue(row.value === null, 'A missing source month was replaced.');
      else close(row.value, expectedRow.value, `${key} value`);
    });
    requireValue(JSON.stringify(record.excluded_years) === JSON.stringify(aggregated.excluded), 'Excluded years do not match the raw source.');
    const computed = validateTrend(record, aggregated.annual);
    validateChecks(record, aggregated.annual, computed);
    const locationName = text(record.location_name ?? 'Imported location', 'location name', 200);
    return {
      analysis: record,
      notes: notesFrom(wrapped ? parsed.notes : {}),
      locationName,
      verification: {
        summary: `Browser checks passed for ${aggregated.annual.length} complete years.`,
        checks: ['Recorded raw-source hash', 'Day-weighted annual and monthly values', 'Complete-year exclusions', 'OLS slope and fitted mean', 'Theil-Sen, one-year influence, and fixed period slopes'],
        limitations: LIMITATIONS,
      },
    };
  }

  function storageAvailable() {
    try {
      const key = `${STORAGE_KEY}.probe`;
      globalThis.localStorage.setItem(key, '1');
      globalThis.localStorage.removeItem(key);
      return true;
    } catch { return false; }
  }

  async function save(analysis, notes = {}, locationName = 'Saved location') {
    const generation = ++saveGeneration;
    const savedAt = new Date().toISOString();
    const envelope = {format: 'Climate Explorer investigation 1', saved_utc: savedAt, notes: notesFrom(notes), analysis: {...analysis, location_name: text(locationName, 'location name', 200)}};
    const contents = JSON.stringify(envelope);
    await importText(contents);
    if (generation !== saveGeneration) return {savedAt: null, superseded: true};
    try { globalThis.localStorage.setItem(STORAGE_KEY, contents); }
    catch { throw new Error('This browser could not save the workspace. Download the investigation JSON instead.'); }
    return {savedAt, superseded: false};
  }

  async function restore() {
    let contents;
    try { contents = globalThis.localStorage.getItem(STORAGE_KEY); }
    catch { throw new Error('This browser does not allow local workspace storage.'); }
    return contents === null ? null : importText(contents);
  }

  function clear() {
    ++saveGeneration;
    try { globalThis.localStorage.removeItem(STORAGE_KEY); }
    catch { throw new Error('This browser could not clear the saved workspace.'); }
  }

  return Object.freeze({importText, save, restore, clear, storageAvailable, sourceHash, MAX_BYTES});
})();
