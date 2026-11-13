'use strict';

globalThis.ClimateViewLinks = (() => {
  const VARIABLES = ['temperature', 'rainfall'];
  const PERIODS = ['full45', 'recent35', 'recent25', 'recent15'];
  const KEYS = ['place', 'variable', 'period'];
  const DEFAULT = Object.freeze({place: 'tehran', variable: 'temperature', period: 'full45'});

  function valid(selection, config) {
    return selection && config?.presets && Object.hasOwn(config.presets, selection.place)
      && VARIABLES.includes(selection.variable) && PERIODS.includes(selection.period)
      && Array.isArray(config.windows) && config.windows.some(row => row.id === selection.period);
  }

  function parse(search, config) {
    const params = new URLSearchParams(search);
    if ([...params].length === 0) return {status: 'default', selection: {...DEFAULT}};
    const selection = Object.fromEntries(KEYS.map(key => [key, params.get(key)]));
    const exact = [...params.keys()].every(key => KEYS.includes(key)) && KEYS.every(key => params.getAll(key).length === 1);
    if (!exact || !valid(selection, config)) return {
      status: 'invalid', selection: {...DEFAULT},
      message: 'This view link is incomplete or unsupported. Showing the default: Tehran temperature, 1981–2025. Use a copied view link with one place, variable, and period.',
    };
    return {status: 'valid', selection};
  }

  function match(analysis, config, comparison) {
    if (!analysis || !config?.presets || !Array.isArray(config.windows) || !Array.isArray(comparison?.rows)) return null;
    const place = Object.keys(config.presets).find(key => {
      const point = config.presets[key];
      return Math.abs(point.latitude - analysis.location?.latitude) < .00001 && Math.abs(point.longitude - analysis.location?.longitude) < .00001;
    });
    const period = config.windows.find(row => row.start === analysis.period?.start && row.end === analysis.period?.end)?.id;
    const selection = {place, variable: analysis.variable, period};
    if (!valid(selection, config)) return null;
    const source = comparison.rows.find(row => row.power_payload_sha256 === analysis.provenance?.payload_sha256
      && Array.isArray(row.requested_coordinates)
      && Math.abs(row.requested_coordinates[0] - analysis.location.latitude) < .00001
      && Math.abs(row.requested_coordinates[1] - analysis.location.longitude) < .00001);
    return source ? selection : null;
  }

  function createURL(base, selection, config) {
    if (!valid(selection, config)) throw new Error('Only a supported frozen public example can have a view link.');
    const url = new URL(base);
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error('A view link requires an HTTP or HTTPS page.');
    url.username = '';
    url.password = '';
    url.search = '';
    url.hash = 'workspace';
    for (const key of KEYS) url.searchParams.set(key, selection[key]);
    return url.href;
  }

  return Object.freeze({parse, match, createURL});
})();
