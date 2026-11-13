import copy
import json
import shutil
import subprocess
import unittest

from climate import PRESETS, ROOT, analyze_saved
from window_analysis import FIXED_WINDOWS


HARNESS = r"""
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const context={URL,URLSearchParams};vm.createContext(context);
vm.runInContext(fs.readFileSync('static/view-links.js','utf8'),context);
const api=context.ClimateViewLinks;
let result;
if(input.operation==='match')result=api.match(input.analysis,input.config,input.comparison);
else if(input.operation==='url')result=api.createURL(input.base,input.selection,input.config);
else result=api.parse(input.search,input.config);
process.stdout.write(JSON.stringify(result));
"""


APP_HARNESS = r"""
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const elements=new Map(),paths=[],copied=[],radios={temperature:{value:'temperature',checked:true},rainfall:{value:'rainfall',checked:false}};
let finishConfig,finishCopy,selected=false,focused=null;
function element(id){
 if(!elements.has(id))elements.set(id,{
  value:'',checked:false,hidden:['view-link-notice','view-link-controls','view-link-fallback'].includes(id),disabled:false,textContent:'',style:{},handlers:{},
  addEventListener(type,callback){this.handlers[type]=callback;},setAttribute(){},setCustomValidity(){},reportValidity(){return true;},
  querySelector(){return{remove(){}};},focus(){focused=id;},select(){selected=true;},classList:{toggle(){}}
 });return elements.get(id);
}
for(const[id,value]of Object.entries({location:'tehran',start:'1981',end:'2025',latitude:'35.6892',longitude:'51.389',window:'full45'}))element(id).value=value;
const configResponse={ok:true,json:async()=>input.config};
const context={input,URL,URLSearchParams,TextEncoder,AbortController,setTimeout,clearTimeout,
 crypto:require('node:crypto').webcrypto,
 location:{href:'https://example.test/climate-explorer/'+input.search+'#old',search:input.search},
 navigator:{clipboard:{writeText:url=>{copied.push(url);return input.clipboard==='denied'?Promise.reject(new Error('denied')):input.clipboard==='pending'?new Promise(resolve=>{finishCopy=resolve;}):Promise.resolve();}}},
 localStorage:{getItem(){return null;},setItem(){},removeItem(){}},
 document:{getElementById:element,querySelector:selector=>{
  if(selector.startsWith('meta'))return input.local?null:{content:'snapshot'};
  if(selector.includes(':checked'))return Object.values(radios).find(radio=>radio.checked);
  const match=selector.match(/value="(temperature|rainfall)"/);if(match)return radios[match[1]];
  return{};
 }},window:{addEventListener(){}},
 fetch:path=>{
  paths.push(path);
  if(path==='demo/config.json'||path==='api/config')return new Promise(resolve=>{finishConfig=()=>resolve(configResponse);});
  if(path==='demo/dataset-check.json'||path==='api/dataset-check')return Promise.resolve({ok:true,json:async()=>input.comparison});
  if(path.startsWith('demo/tehran')||path.startsWith('api/climate?'))return Promise.resolve({ok:true,json:async()=>path.includes('rainfall')?input.recent:input.full});
  throw new Error('Unexpected request: '+path);
 }
};
// Radio inputs share one checked state in the browser.
for(const key of ['temperature','rainfall'])Object.defineProperty(radios[key],'checked',{get(){return this.active??(key==='temperature');},set(value){if(value)for(const other of Object.keys(radios))radios[other].active=other===key;else this.active=false;},configurable:true});
vm.createContext(context);
for(const name of ['workspace.js','view-links.js','app.js'])vm.runInContext(fs.readFileSync('static/'+name,'utf8'),context);
vm.runInContext('render=()=>updateViewLink(); renderDatasetComparison=()=>updateViewLink(); updateLocation=()=>{};',context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 if(input.operation==='manualBeforeConfig'){
  element('location').value='berlin';element('window').value='recent15';
  element('explore-form').handlers.change();
 }
 finishConfig();await flush();await flush();
 if(input.operation==='unmatchedImport')await context.openInvestigation(JSON.stringify(input.unmatched),'Imported evidence');
 if(input.operation==='copy')await element('copy-view-link').handlers.click();
 if(input.operation==='staleCopy'){
  const copying=element('copy-view-link').handlers.click();
  vm.runInContext('currentResult=input.unmatched; updateViewLink();',context);
  finishCopy();await copying;
 }
 process.stdout.write(JSON.stringify({paths,copied,selected,focused,location:element('location').value,period:element('window').value,start:element('start').value,end:element('end').value,
  notice:element('view-link-notice').textContent,noticeHidden:element('view-link-notice').hidden,controlsHidden:element('view-link-controls').hidden,disabled:element('copy-view-link').disabled,
  fallbackHidden:element('view-link-fallback').hidden,url:element('view-link-url').value,status:element('view-link-status').textContent,loadingStatus:element('status').textContent,
  help:element('view-link-help').textContent,state:vm.runInContext('currentResult?{variable:currentResult.variable,start:currentResult.period.start}:null',context)}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


@unittest.skipUnless(shutil.which("node"), "Node is needed for view-link and application interaction tests")
class ViewLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {"presets": PRESETS, "windows": list(FIXED_WINDOWS), "first_year": 1981, "last_year": 2025}
        cls.comparison = json.loads((ROOT / "evaluation/dataset-check.json").read_text())
        saved = json.loads((ROOT / "evaluation/source-snapshots/tehran-power.json").read_text())
        cls.full = analyze_saved({"start": "1981", "end": "2025", "variable": "temperature"}, saved)
        cls.recent = analyze_saved({"start": "2011", "end": "2025", "variable": "rainfall"}, saved)
        cls.unmatched = copy.deepcopy(cls.recent)
        cls.unmatched["location"]["latitude"] = 35.6893
        cls.unmatched["provenance"]["request_url"] = cls.unmatched["provenance"]["request_url"].replace("latitude=35.6892", "latitude=35.6893")

    def run_js(self, script=HARNESS, **options):
        result = subprocess.run(
            ["node", "-e", script], input=json.dumps({"config": self.config, "comparison": self.comparison, **options}),
            cwd=ROOT, text=True, capture_output=True, check=True, timeout=10,
        )
        return json.loads(result.stdout)

    def run_app(self, operation="load", search="?place=tehran&variable=rainfall&period=recent15", **options):
        return self.run_js(APP_HARNESS, operation=operation, search=search, full=self.full, recent=self.recent, unmatched=self.unmatched, **options)

    def test_valid_fixed_view_parses_exact_selection(self):
        result = self.run_js(search="?place=tehran&variable=rainfall&period=recent15")
        self.assertEqual(result, {"status": "valid", "selection": {"place": "tehran", "variable": "rainfall", "period": "recent15"}})

    def test_unknown_incomplete_duplicate_or_malicious_parameters_have_explicit_default(self):
        for search in ["?place=tehran", "?place=constructor&variable=rainfall&period=recent15", "?place=tehran&variable=rainfall&period=javascript:alert(1)", "?place=tehran&variable=rainfall&period=recent15&place=berlin", "?utm=anything", "?place=tehran&variable=rainfall&period=recent15&url=https://example.test"]:
            with self.subTest(search=search):
                result = self.run_js(search=search)
                self.assertEqual(result["status"], "invalid")
                self.assertEqual(result["selection"], {"place": "tehran", "variable": "temperature", "period": "full45"})
                self.assertIn("Showing the default", result["message"])

    def test_generated_link_strips_other_query_and_fragment_and_contains_no_notes(self):
        url = self.run_js(operation="url", base="https://private:password@example.test/climate-explorer/?note=private&token=old#sources", selection={"place": "tehran", "variable": "rainfall", "period": "recent15"})
        self.assertEqual(url, "https://example.test/climate-explorer/?place=tehran&variable=rainfall&period=recent15#workspace")

    def test_match_requires_the_frozen_source_and_exact_preset_period(self):
        matched = self.run_js(operation="match", analysis=self.recent)
        self.assertEqual(matched, {"place": "tehran", "variable": "rainfall", "period": "recent15"})
        self.assertIsNone(self.run_js(operation="match", analysis=self.unmatched))
        changed = copy.deepcopy(self.recent)
        changed["provenance"]["payload_sha256"] = "f" * 64
        self.assertIsNone(self.run_js(operation="match", analysis=changed))

    def test_actual_app_supported_link_loads_fifteen_year_rainfall_only_from_snapshot(self):
        result = self.run_app()
        self.assertIn("demo/tehran-recent15-rainfall.json", result["paths"])
        self.assertEqual(result["state"], {"variable": "rainfall", "start": 2011})
        self.assertFalse(any(path.startswith("api/") or path.startswith("https:") for path in result["paths"]))
        self.assertIn("2011–2025", result["notice"])
        self.assertFalse(result["disabled"])

    def test_actual_app_invalid_link_announces_and_loads_explicit_default(self):
        result = self.run_app(search="?place=../../api/climate&variable=rainfall&period=recent15")
        self.assertIn("demo/tehran-temperature.json", result["paths"])
        self.assertEqual(result["state"], {"variable": "temperature", "start": 1981})
        self.assertIn("Showing the default", result["notice"])

    def test_actual_app_manual_choices_beat_late_configuration_and_url(self):
        result = self.run_app("manualBeforeConfig")
        self.assertEqual(result["location"], "berlin")
        self.assertEqual(result["period"], "recent15")
        self.assertEqual(str(result["start"]), "2011")
        self.assertFalse(any("tehran-recent15" in path for path in result["paths"]))
        self.assertIsNone(result["state"])
        self.assertIn("Your choices are ready", result["loadingStatus"])

    def test_actual_app_clipboard_denial_shows_selectable_fallback_without_permission_flow(self):
        result = self.run_app("copy", clipboard="denied")
        self.assertFalse(result["fallbackHidden"])
        self.assertTrue(result["selected"])
        self.assertEqual(result["focused"], "view-link-url")
        self.assertEqual(result["url"], "https://example.test/climate-explorer/?place=tehran&variable=rainfall&period=recent15#workspace")
        self.assertIn("does not freeze", result["help"])

    def test_actual_app_clipboard_success_keeps_notes_out_of_url(self):
        result = self.run_app("copy", search="?place=tehran&variable=rainfall&period=recent15")
        self.assertEqual(len(result["copied"]), 1)
        self.assertIn("View link copied", result["status"])
        self.assertTrue(result["fallbackHidden"])

    def test_actual_app_unmatched_import_disables_link(self):
        result = self.run_app("unmatchedImport")
        self.assertTrue(result["disabled"])
        self.assertIn("Download your investigation", result["help"])

    def test_actual_app_late_clipboard_result_cannot_change_new_view_status(self):
        result = self.run_app("staleCopy", clipboard="pending")
        self.assertEqual(result["status"], "")
        self.assertTrue(result["disabled"])

    def test_full_local_server_ignores_view_query_and_hides_link_controls(self):
        result = self.run_app(local=True)
        self.assertTrue(result["controlsHidden"])
        self.assertTrue(result["noticeHidden"])
        self.assertTrue(any(path.startswith("api/climate?") for path in result["paths"]))
        self.assertEqual(result["state"], {"variable": "temperature", "start": 1981})


if __name__ == "__main__":
    unittest.main()
