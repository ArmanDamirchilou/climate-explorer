import copy
import json
import shutil
import subprocess
import unittest

from climate import PRESETS, ROOT, analyze_saved, payload_hash


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const entries = new Map([['unrelated-entry', 'preserve']]);
const realCrypto = require('node:crypto').webcrypto;
let digestCalls = 0;
const crypto = {subtle: {digest: (...args) => {
  const result = realCrypto.subtle.digest(...args);
  return input.delayFirst && ++digestCalls === 1
    ? result.then(buffer => new Promise(resolve => setTimeout(() => resolve(buffer), 40))) : result;
}}};
const storage = {
  getItem: key => entries.has(key) ? entries.get(key) : null,
  setItem: (key, value) => { if (input.blockStorage) throw new Error('blocked'); entries.set(key, value); },
  removeItem: key => { if (input.blockStorage) throw new Error('blocked'); entries.delete(key); }
};
const context = {
  crypto: input.noCrypto ? undefined : crypto,
  TextEncoder, URL, localStorage: storage,
  fetch: () => { throw new Error('Workspace must not use the network'); },
  document: new Proxy({}, {get: () => { throw new Error('Workspace must not touch the DOM'); }})
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('static/workspace.js', 'utf8'), context);
(async () => {
  const api = context.ClimateWorkspace;
  let result;
  if (input.operation === 'hash') result = await api.sourceHash(input.payload);
  else if (input.operation === 'availability') result = api.storageAvailable();
  else if (input.operation === 'empty') result = await api.restore();
  else if (input.operation === 'concurrentSaves') {
    const first = api.save(input.analysis, {question: 'old question'}, 'Old location');
    const second = api.save(input.analysis, {question: 'new question'}, 'New location');
    result = {saved: await Promise.all([first, second]), restored: await api.restore()};
  } else if (input.operation === 'clearPending') {
    const saving = api.save(input.analysis, {}, 'Pending save');
    api.clear();
    result = {saved: await saving, restored: await api.restore()};
  }
  else if (input.operation === 'saveRestore') {
    const saved = await api.save(input.analysis, input.notes, input.locationName);
    const restored = await api.restore();
    api.clear();
    result = {saved, restored, afterClear: await api.restore(), unrelated: entries.get('unrelated-entry')};
  } else result = await api.importText(input.text);
  process.stdout.write(JSON.stringify({ok: true, result}));
})().catch(error => process.stdout.write(JSON.stringify({ok: false, error: error.message})));
"""


APP_HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const elements = new Map(), requests = [], storage = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value: '', checked: false, hidden: false, textContent: '', handlers: {},
    addEventListener(type, callback) { this.handlers[type] = callback; },
    setAttribute() {}, setCustomValidity() {}, reportValidity() { return true; },
    querySelector() { return {remove() {}}; }
  });
  return elements.get(id);
}
for (const [id, value] of Object.entries({location:'tehran', start:'1981', end:'2025', latitude:'35.6892', longitude:'51.389', window:'full45'})) element(id).value = value;
const context = {
  input, TextEncoder, URL, URLSearchParams, AbortController, setTimeout, clearTimeout,
  crypto: require('node:crypto').webcrypto,
  localStorage: {getItem: key => storage.get(key) ?? null, setItem: (key,value) => storage.set(key,value), removeItem: key => storage.delete(key)},
  document: {getElementById: element, querySelector: selector => selector.startsWith('meta') ? null : {value:'temperature'}},
  window: {addEventListener() {}, print() {}},
  fetch: path => new Promise(resolve => requests.push({path,resolve}))
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('static/workspace.js','utf8'),context);
vm.runInContext(fs.readFileSync('static/app.js','utf8'),context);
vm.runInContext('render = () => {}; updateLocation = () => {}; updateStorageControls = () => {};', context);
const flush = () => new Promise(resolve => setImmediate(resolve));
const file = JSON.stringify({format:'Climate Explorer investigation 1', analysis:{...input.analysis,location_name:'Imported evidence'},notes:{question:'Imported question'}});
(async () => {
  if (input.operation === 'lateFile') {
    vm.runInContext('config = input.config;',context);
    let finishText;
    const fileText = new Promise(resolve => { finishText = resolve; });
    const reading = element('import-file').handlers.change({target:{files:[{size:100,text:()=>fileText}],value:'chosen.json'}});
    const exploring = context.explore();
    const request = requests.find(request => request.path.startsWith('api/climate?'));
    request.resolve({ok:true,json:async()=>input.analysis});
    await exploring;
    finishText(file);
    await reading;
  } else if (input.operation === 'clearPending') {
    vm.runInContext('currentResult = input.analysis; currentName = "Tehran";',context);
    element('save-locally').checked = true;
    const saving = context.persistWork();
    element('clear-work').handlers.click();
    await saving;
  } else {
    await context.openInvestigation(file,'Imported');
    requests[0].resolve({ok:input.operation !== 'configFailure',json:async()=>input.config});
    await flush(); await flush();
  }
  const state = vm.runInContext('({name:currentName,hasResult:!!currentResult})',context);
  process.stdout.write(JSON.stringify({state,paths:requests.map(request=>request.path),status:element('workspace-status').textContent,errorHidden:element('error').hidden,saved:await context.ClimateWorkspace.restore()}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


@unittest.skipUnless(shutil.which("node"), "Node is needed for browser workspace verification tests")
class WorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = []
        for key, place in PRESETS.items():
            saved = json.loads((ROOT / "evaluation/source-snapshots" / f"{key}-power.json").read_text())
            for variable in ["temperature", "rainfall"]:
                record = analyze_saved({**place, "start": "1981", "end": "2025", "variable": variable}, saved)
                record["location_name"] = place["name"]
                cls.records.append(record)
        cls.record = cls.records[0]

    def run_js(self, **input):
        result = subprocess.run(
            ["node", "-e", HARNESS], input=json.dumps(input), text=True,
            capture_output=True, check=True, cwd=ROOT, timeout=10,
        )
        return json.loads(result.stdout)

    def import_record(self, record):
        return self.run_js(text=json.dumps(record))

    def run_app(self, operation):
        result = subprocess.run(
            ["node", "-e", APP_HARNESS],
            input=json.dumps({"operation": operation, "analysis": self.record, "config": {"presets": PRESETS, "first_year": 1981, "last_year": 2025}}),
            text=True, capture_output=True, check=True, cwd=ROOT, timeout=10,
        )
        return json.loads(result.stdout)

    def assert_rejected(self, record, message):
        result = self.import_record(record)
        self.assertFalse(result["ok"], result)
        self.assertIn(message, result["error"])

    def test_all_ten_frozen_records_import_without_network_or_dom_access(self):
        for record in self.records:
            with self.subTest(place=record["location_name"], variable=record["variable"]):
                result = self.import_record(record)
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["result"]["analysis"], record)
                self.assertEqual(result["result"]["locationName"], record["location_name"])
                self.assertIn("45 complete years", result["result"]["verification"]["summary"])

    def test_hash_matches_python_numeric_normalization_unicode_and_exponents(self):
        payload = {
            "unicode": 'é ❤ \u007f 🛰️ " \\ \n', "ascii": "NASA", "\uffff": 1, "🛰": 2,
            "numbers": [1.0, -0.0, 1e-7, 1.23456789e-8, .00001, .0001, -.0000999, 9007199254740991],
        }
        result = self.run_js(operation="hash", payload=payload)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["result"], payload_hash(payload))

    def test_changed_raw_source_is_rejected(self):
        record = copy.deepcopy(self.record)
        record["raw_source"]["properties"]["parameter"]["T2M"]["198101"] += 1
        self.assert_rejected(record, "hash does not match")

    def test_changed_annual_monthly_and_slope_results_are_rejected(self):
        for field in ["annual", "monthly", "slope"]:
            record = copy.deepcopy(self.record)
            if field == "slope":
                record["trend"]["slope_per_decade"] += .1
            else:
                record[field][0]["value"] += .1
            with self.subTest(field=field):
                self.assert_rejected(record, "Recomputed value differs")

    def test_changed_robust_influence_and_period_slopes_are_rejected(self):
        for field in ["robust", "influence", "period"]:
            record = copy.deepcopy(self.record)
            if field == "robust":
                record["checks"]["theil_sen_slope_per_decade"] += .1
            elif field == "influence":
                record["checks"]["leave_one_out"]["minimum_slope_per_decade"] += .1
            else:
                record["checks"]["periods"][0]["slope_per_decade"] += .1
            with self.subTest(field=field):
                self.assert_rejected(record, "Recomputed value differs")

    def test_source_endpoint_coordinates_and_unit_mismatches_are_rejected(self):
        for field in ["endpoint", "coordinates", "units", "format"]:
            record = copy.deepcopy(self.record)
            if field == "endpoint":
                record["provenance"]["request_url"] = "javascript:alert(1)"
            elif field == "coordinates":
                record["location"]["latitude"] = 0
            elif field == "units":
                record["metadata"]["unit"] = "Kelvin"
            else:
                record["provenance"]["payload_hash_format"] = "unknown"
            with self.subTest(field=field):
                result = self.import_record(record)
                self.assertFalse(result["ok"], result)

    def test_file_size_invalid_json_and_nonfinite_numbers_are_rejected(self):
        for contents in ["x" * (2 * 1024 * 1024 + 1), "{", '{"value": 1e999}', '{"value": NaN}']:
            with self.subTest(prefix=contents[:40]):
                self.assertFalse(self.run_js(text=contents)["ok"])

    def test_unsafe_object_keys_and_deep_nesting_are_rejected(self):
        for contents in ['{"__proto__":{"polluted":true}}', '{"constructor":{}}', "[" * 30 + "0" + "]" * 30]:
            with self.subTest(contents=contents):
                self.assertFalse(self.run_js(text=contents)["ok"])

    def test_html_like_notes_round_trip_as_plain_text_and_clear_only_own_storage(self):
        notes = {"question": '<img src=x onerror="alert(1)">', "interpretation": "=SUM(1,2)", "remaining_uncertainty": "<script>bad()</script>"}
        result = self.run_js(operation="saveRestore", analysis=self.record, notes=notes, locationName="<b>My location</b>")
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["result"]["restored"]["notes"], notes)
        self.assertEqual(result["result"]["restored"]["locationName"], "<b>My location</b>")
        self.assertIsNone(result["result"]["afterClear"])
        self.assertEqual(result["result"]["unrelated"], "preserve")

    def test_storage_denied_empty_workspace_and_crypto_unavailable_are_explicit(self):
        self.assertIsNone(self.run_js(operation="empty")["result"])
        self.assertFalse(self.run_js(operation="availability", blockStorage=True)["result"])
        blocked = self.run_js(operation="saveRestore", analysis=self.record, notes={}, locationName="Tehran", blockStorage=True)
        self.assertFalse(blocked["ok"])
        self.assertIn("Download the investigation JSON", blocked["error"])
        no_crypto = self.run_js(text=json.dumps(self.record), noCrypto=True)
        self.assertFalse(no_crypto["ok"])
        self.assertIn("Web Crypto", no_crypto["error"])

    def test_older_async_save_cannot_replace_newer_notes(self):
        result = self.run_js(operation="concurrentSaves", analysis=self.record, delayFirst=True)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["result"]["saved"][0]["superseded"])
        self.assertFalse(result["result"]["saved"][1]["superseded"])
        self.assertEqual(result["result"]["restored"]["notes"]["question"], "new question")
        self.assertEqual(result["result"]["restored"]["locationName"], "New location")

    def test_clear_cancels_a_pending_async_save(self):
        result = self.run_js(operation="clearPending", analysis=self.record, delayFirst=True)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["result"]["saved"]["superseded"])
        self.assertIsNone(result["result"]["restored"])

    def test_actual_app_late_file_cannot_replace_newer_explore(self):
        result = self.run_app("lateFile")
        self.assertEqual(result["state"]["name"], PRESETS["tehran"]["name"])

    def test_actual_app_pending_config_does_not_overwrite_import(self):
        result = self.run_app("configPending")
        self.assertEqual(result["state"]["name"], "Imported evidence")
        self.assertFalse(any(path.startswith("api/climate?") for path in result["paths"]))

    def test_actual_app_clear_keeps_pending_save_from_restoring_or_changing_status(self):
        result = self.run_app("clearPending")
        self.assertIsNone(result["saved"])
        self.assertIn("Local saved copy cleared", result["status"])

    def test_actual_app_late_config_failure_does_not_replace_import_status(self):
        result = self.run_app("configFailure")
        self.assertEqual(result["state"]["name"], "Imported evidence")
        self.assertTrue(result["errorHidden"])

    def test_missing_fields_oversized_notes_and_invalid_calendar_are_rejected(self):
        record = copy.deepcopy(self.record)
        del record["checks"]
        self.assert_rejected(record, "sensitivity checks")
        wrapped = {"format": "Climate Explorer investigation 1", "analysis": self.record, "notes": {"question": "x" * 8001}}
        self.assert_rejected(wrapped, "note question")
        record = copy.deepcopy(self.record)
        record["monthly"][0]["month"] = 2
        self.assert_rejected(record, "calendar order")

    def test_each_note_limit_matches_the_interface_and_never_truncates(self):
        for key, limit in [("question", 2000), ("interpretation", 4000), ("remaining_uncertainty", 2000)]:
            wrapped = {"format": "Climate Explorer investigation 1", "analysis": self.record, "notes": {key: "x" * limit}}
            with self.subTest(key=key):
                result = self.import_record(wrapped)
                self.assertTrue(result["ok"], result)
                self.assertEqual(len(result["result"]["notes"][key]), limit)
                wrapped["notes"][key] += "x"
                self.assert_rejected(wrapped, f"note {key}")

    def test_required_render_and_provenance_fields_cannot_be_missing(self):
        for path in [("analysis", "code_sha256"), ("analysis", "versions"), ("provenance", "sources"), ("provenance", "spatial_resolution"), ("trend", "line"), ("checks", "leave_one_out")]:
            record = copy.deepcopy(self.record)
            del record[path[0]][path[1]]
            with self.subTest(path=path):
                self.assertFalse(self.import_record(record)["ok"])

    def test_interval_scope_is_explicit_and_does_not_claim_full_replay(self):
        record = copy.deepcopy(self.record)
        record["trend"].update({"ci95_per_decade": [-100, 100], "evidence": "unclear"})
        for row in record["checks"]["intervals"]:
            row.update({"ci95_per_decade": [-100, 100], "evidence": "unclear"})
        record["checks"]["interval_conclusions_agree"] = True
        result = self.import_record(record)
        self.assertTrue(result["ok"], result)
        scope = result["result"]["verification"]["limitations"]
        self.assertIn("do not recompute confidence intervals", scope)
        self.assertIn("does not authenticate NASA data", scope)
        self.assertIn("evaluation/replay.py", scope)


if __name__ == "__main__":
    unittest.main()
