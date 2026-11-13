'use strict';

globalThis.ClimateStory = (() => {
  const $ = id => document.getElementById(id);
  const UNITS = 'mm/year per decade';
  let options, evidence, step = 0, generation = 0, pending, mounted = false;

  function rate(value) {
    return `${value > 0 ? '+' : value < 0 ? '−' : ''}${Math.abs(value).toFixed(3)}`;
  }

  function requireValue(condition, message) {
    if (!condition) throw new Error(message);
  }

  async function load(signal) {
    if (evidence) return evidence;
    const response = await fetch('story-tehran.json', {signal});
    if (!response.ok) throw new Error('The saved story could not be loaded. Try again, or use the explorer below.');
    const raw = await response.text();
    requireValue(new TextEncoder().encode(raw).length <= ClimateWorkspace.MAX_BYTES, 'The story file is too large.');
    const story = JSON.parse(raw);
    requireValue(story.format === 'Climate Explorer guided story 1' && story.id === 'tehran-rainfall', 'The story format is not supported.');
    const verified = await Promise.all(['full45', 'recent15'].map(id => ClimateWorkspace.importText(JSON.stringify(story.analyses?.[id]))));
    const [full, recent] = verified.map(result => result.analysis);
    requireValue(full.variable === 'rainfall' && recent.variable === 'rainfall' && full.period.start === 1981 && recent.period.start === 2011 && full.period.end === 2025 && recent.period.end === 2025, 'The story periods or variable do not match.');
    requireValue(full.annual.length === 45 && recent.annual.length === 15 && full.location.latitude === 35.6892 && full.location.longitude === 51.389 && recent.location.latitude === full.location.latitude && recent.location.longitude === full.location.longitude, 'The story location or year coverage does not match.');
    requireValue(full.provenance.payload_sha256 === recent.provenance.payload_sha256 && story.source?.payload_sha256 === full.provenance.payload_sha256, 'The story analyses do not use the same frozen source.');
    requireValue(full.trend.slope_per_decade > 0 && recent.trend.slope_per_decade < 0, 'The saved example no longer has the documented opposite directions.');
    requireValue(typeof story.selection_note === 'string' && story.selection_note.length <= 4000, 'The story selection note is missing.');
    evidence = story;
    return story;
  }

  function busy(value) {
    $('story-start').disabled = value;
    for (const id of ['story-previous', 'story-next', 'story-open-chart', 'story-open-full', 'story-open-recent', 'story-step-0', 'story-step-1', 'story-step-2']) $(id).disabled = value;
    $('story-panel').setAttribute('aria-busy', String(value));
    if (!value) $('story-previous').disabled = step === 0;
  }

  function drawRates() {
    const full = evidence.analyses.full45.trend.slope_per_decade;
    const recent = evidence.analyses.recent15.trend.slope_per_decade;
    const extent = Math.ceil(Math.max(Math.abs(full), Math.abs(recent)) / 10) * 10;
    for (const [name, value] of [['full', full], ['recent', recent]]) {
      const width = Math.abs(value) / extent * 50;
      $('story-value-' + name).textContent = rate(value);
      $('story-bar-' + name).style.width = `${width}%`;
      $('story-bar-' + name).style.left = `${value >= 0 ? 50 : 50 - width}%`;
      $('story-rate-' + name).classList.toggle('story-rate-current', step === (name === 'full' ? 0 : 1));
    }
    $('story-rate-recent').hidden = step === 0;
  }

  function render() {
    const full = evidence.analyses.full45, recent = evidence.analyses.recent15;
    const record = step === 0 ? full : recent;
    const headings = ['Start with the longer record.', 'Keep the source. Change the dates.', 'Different periods need different claims.'];
    $('story-panel').hidden = false;
    $('story-progress').textContent = `Step ${step + 1} of 3 · Tehran precipitation`;
    $('story-heading').textContent = headings[step];
    $('story-explanation').textContent = step === 0
      ? `Across 1981–2025, the fitted annual rainfall rate is ${rate(full.trend.slope_per_decade)} ${UNITS}. That is an upward fitted rate over these 45 complete years.`
      : step === 1
        ? `Using 2011–2025 gives ${rate(recent.trend.slope_per_decade)} ${UNITS}. The direction is now downward. The location, monthly source values, aggregation, and fitting method are the same. The selected period changed.`
        : `The 45-year estimate is ${rate(full.trend.slope_per_decade)} ${UNITS}; the 15-year estimate is ${rate(recent.trend.slope_per_decade)}. They estimate change over different spans of history. The periods overlap and are not independent confirmations.`;
    const interval = record.trend.ci95_per_decade;
    $('story-interval').textContent = `Ordinary OLS 95% slope interval for ${record.period.start}–${record.period.end}: ${rate(interval[0])} to ${rate(interval[1])} ${UNITS}. It ${interval[0] <= 0 && interval[1] >= 0 ? 'includes' : 'excludes'} zero under the independent-error model. Browser source and point-calculation checks do not recompute this interval.`;
    $('story-caution').textContent = step === 0
      ? 'A fitted line is not a forecast. Its uncertainty depends on the error assumptions. Open the chart to inspect the observations and method checks.'
      : step === 1
        ? 'The 15-year ordinary interval includes zero. This short record does not establish a permanent downward trend or a climate reversal.'
        : 'Changing the dates changes what is being estimated. Opposite fitted signs alone do not establish a climate reversal, acceleration, a cause, or what happens next.';
    for (let i = 0; i < 3; i++) $('story-step-' + i).setAttribute('aria-current', i === step ? 'step' : 'false');
    $('story-claim').hidden = step !== 2;
    $('story-open-chart').hidden = step === 2;
    $('story-open-chart').textContent = step === 0 ? 'View the 45-year chart' : 'View the 15-year chart';
    $('story-comparison-actions').hidden = step !== 2;
    $('story-next').textContent = step === 2 ? 'Explore on my own' : 'Next step';
    $('story-source-description').textContent = `${full.provenance.provider} / ${full.provenance.sources.join(', ')}. Same frozen response, retrieved ${full.provenance.fetched_at.slice(0, 10)} UTC. Native grid: 0.5° latitude × 0.625° longitude. This is not a local weather-station reading.`;
    $('story-source-hash').textContent = full.provenance.payload_sha256;
    $('story-source-link').href = full.provenance.request_url;
    $('story-selection').textContent = evidence.selection_note;
    drawRates();
  }

  async function choose(nextStep, {revealChart = false, windowId = null} = {}) {
    const sequence = ++generation;
    if (pending) pending.abort();
    pending = new AbortController();
    const request = pending;
    const intent = options.onIntent();
    busy(true);
    $('story-load-status').hidden = false;
    $('story-load-status').textContent = evidence ? 'Opening the saved evidence…' : 'Loading and checking the two frozen NASA analyses…';
    try {
      await load(request.signal);
      if (sequence !== generation) return;
      step = nextStep;
      render();
      const selected = windowId || (step === 0 ? 'full45' : 'recent15');
      const opened = await options.openAnalysis(evidence.analyses[selected], {intent, isCurrent: () => sequence === generation});
      if (sequence !== generation || !opened) return;
      $('story-status').textContent = `The chart below now shows Tehran precipitation, ${evidence.analyses[selected].period.start}–2025, from the frozen story source. Explorer controls start a new analysis.`;
      $('story-load-status').hidden = true;
      if (revealChart) options.revealChart();
      else $('story-heading').focus({preventScroll: true});
    } catch (error) {
      if (sequence !== generation || error.name === 'AbortError') return;
      $('story-load-status').textContent = `Story could not open: ${error.message}`;
    } finally {
      if (sequence === generation) { pending = null; busy(false); }
    }
  }

  function pause() {
    ++generation;
    if (pending) pending.abort();
    pending = null;
    if (!mounted) return;
    busy(false);
    $('story-load-status').hidden = true;
    if (!$('story-panel').hidden) $('story-status').textContent = 'Story paused while you use the explorer. Choose a story step to return to the frozen example.';
  }

  function close(focusExplorer = false) {
    pause();
    $('story-panel').hidden = true;
    if (focusExplorer) options.exploreOwn();
    else $('story-start').focus({preventScroll: true});
  }

  function mount(callbacks) {
    if (mounted) return;
    options = callbacks;
    mounted = true;
    $('story-start').addEventListener('click', () => choose(0));
    for (let i = 0; i < 3; i++) $('story-step-' + i).addEventListener('click', () => choose(i));
    $('story-next').addEventListener('click', () => step === 2 ? close(true) : choose(step + 1));
    $('story-previous').addEventListener('click', () => choose(Math.max(0, step - 1)));
    $('story-open-chart').addEventListener('click', () => choose(step, {revealChart: true}));
    $('story-open-full').addEventListener('click', () => choose(2, {revealChart: true, windowId: 'full45'}));
    $('story-open-recent').addEventListener('click', () => choose(2, {revealChart: true, windowId: 'recent15'}));
    $('story-close').addEventListener('click', () => close());
    $('story-claim').addEventListener('change', event => {
      const feedback = {
        periods: 'Supported: the fitted rate depends on the stated period. Include both dates and the uncertainty. This does not explain a cause or predict future rainfall.',
        reversal: 'This comparison does not establish a permanent climate reversal. The fits cover different periods, and the short-period ordinary interval includes zero.',
        forecast: 'These fitted lines describe past observations. This analysis does not forecast the next decade.',
      };
      $('story-claim-feedback').textContent = feedback[event.target.value] || '';
    });
  }

  return Object.freeze({mount, pause});
})();
