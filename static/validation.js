'use strict';

const snapshotMode = document.querySelector('meta[name="climate-mode"]')?.content === 'snapshot';
const endpoint = name => snapshotMode ? `demo/${name}.json` : `api/${name}`;
for (const link of document.querySelectorAll('[data-report]')) link.href = endpoint(link.dataset.report);

async function showEvaluation() {
  const $ = id => document.getElementById(id);
  const percent = value => `${(100 * value).toFixed(1)}%`;
  const rate = (value, interval) => `${percent(value)} (${percent(interval[0])}–${percent(interval[1])})`;
  try {
    const response = await fetch(endpoint('validation'));
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Evaluation could not be loaded.');
    $('protocol-summary').textContent = `Protocol fixed on 11 November 2026. Seed ${result.seed}, ${result.bit_generator}. ${result.replicates_per_scenario.toLocaleString('en')} replicates in each of ${result.scenarios.length} scenarios. Python ${result.versions.python}, NumPy ${result.versions.numpy}, SciPy ${result.versions.scipy}, statsmodels ${result.versions.statsmodels}.`;
    const selector = $('scenario');
    selector.replaceChildren(...result.scenarios.map((scenario, index) => {
      const option = document.createElement('option'); option.value = String(index); option.textContent = `${scenario.scenario} (${scenario.n} years)`; return option;
    }));
    const all = document.createElement('option'); all.value = 'all'; all.textContent = 'All scenarios'; selector.append(all);
    selector.disabled = false;
    function renderScenario() {
      const fragment = document.createDocumentFragment();
      const selected = selector.value === 'all' ? result.scenarios : [result.scenarios[Number(selector.value)]];
      for (const scenario of selected) {
      for (const [method, values] of Object.entries(scenario.methods)) {
        const tr = document.createElement('tr');
        for (const text of [`${scenario.scenario} (n=${scenario.n})`, method, rate(values.coverage, values.coverage_mc95), rate(values.excludes_zero, values.excludes_zero_mc95), values.rmse_per_decade.toFixed(3), String(values.failures)]) {
          const td = document.createElement('td'); td.textContent = text; tr.append(td);
        }
        fragment.append(tr);
      }
      }
      $('evaluation-body').replaceChildren(fragment);
      $('evaluation-caption').textContent = `Paired comparisons: ${selector.selectedOptions[0].textContent}. Each method sees the same simulated record. Slopes use arbitrary units per decade.`;
    }
    selector.addEventListener('change', renderScenario);
    renderScenario();
  } catch (error) {
    $('validation-error').hidden = false;
    $('validation-error').textContent = error.message;
    $('protocol-summary').textContent = 'The saved evaluation is unavailable. Run evaluation/calibration.py in the project environment, then reload.';
  }
}

showEvaluation();

async function showDatasetCheck() {
  const status = document.getElementById('dataset-status');
  try {
    const response = await fetch(endpoint('dataset-check'));
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Dataset comparison could not be loaded.');
    const fragment = document.createDocumentFragment();
    for (const row of result.rows) {
      const tr = document.createElement('tr');
      const difference = row.slope_difference_power_minus_gistemp;
      for (const text of [row.name, row.gistemp_cell_center.join(', '), `${row.years[0]}–${row.years.at(-1)} (${row.years.length})`, row.power_slope_c_per_decade.toFixed(3), row.gistemp_slope_c_per_decade.toFixed(3), `${difference > 0 ? '+' : ''}${difference.toFixed(3)}`]) {
        const td = document.createElement('td'); td.textContent = text; tr.append(td);
      }
      fragment.append(tr);
    }
    document.getElementById('dataset-body').replaceChildren(fragment);
    status.textContent = `Comparison saved ${result.generated_utc.slice(0, 10)} UTC. The frozen source files, hashes, and extraction script are retained in the project evaluation folder.`;
  } catch (error) {
    status.textContent = error.message;
  }
}

showDatasetCheck();

async function showSpatialAudit() {
  const status = document.getElementById('audit-status');
  try {
    const response = await fetch(endpoint('science-audit'));
    if (!response.ok) throw new Error('The frozen spatial audit is unavailable. Read SCIENCE_AUDIT.md in the repository.');
    const audit = await response.json();
    const labels = { original_toronto: 'Original Toronto request', nominal_nearby_grid: 'Nominal nearby grid coordinate', gistemp_cell_center: 'GISTEMP cell center', north_neighbor: 'Fixed northern request', west_neighbor: 'Fixed western request' };
    document.getElementById('audit-body').replaceChildren(...audit.power.map(row => {
      const tr = document.createElement('tr');
      const params = new URL(row.request_url).searchParams;
      for (const text of [labels[row.label] || row.label, `${params.get('latitude')}, ${params.get('longitude')}`, row.weighted_slope_c_per_decade.toFixed(3), row.max_abs_weighted_minus_nasa_annual_c.toFixed(4)]) {
        const td = document.createElement('td'); td.textContent = text; tr.append(td);
      }
      return tr;
    }));
    status.textContent = `Exploratory audit saved ${audit.generated_utc.slice(0, 10)} UTC. All 45 original annual values agree with NASA's rounded annual summaries within 0.005°C. Nearby POWER rates differ, while the nine checked GISTEMP cells range from 0.294 to 0.349°C per decade. Spatial support is still not matched; no cause or correct source has been established.`;
  } catch (error) {
    status.textContent = error.message;
  }
}

showSpatialAudit();
