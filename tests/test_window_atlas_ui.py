import copy
import json
import shutil
import subprocess
import unittest

from climate import PRESETS, ROOT, analyze_saved
from evaluation.replay import verify
from window_atlas import build_window_atlas


HARNESS = r"""
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const elements=new Map(),opened=[],paths=[];
let focus=null,finishFetch,intent=0,chartReveals=0;
function node(tag='element'){
 return {tag,children:[],attributes:{},handlers:{},style:{},hidden:false,disabled:false,textContent:'',value:'',
  classList:{toggle(){}},setAttribute(key,value){this.attributes[key]=value;},
  append(...items){this.children.push(...items);},replaceChildren(...items){this.children=items;},
  addEventListener(type,callback){this.handlers[type]=callback;},
  focus(){focus=this.attributes['aria-label']||this.id;if(this.handlers.focus)this.handlers.focus();},
  set innerHTML(value){throw new Error('Atlas must not insert HTML from data');}
 };
}
function element(id){if(!elements.has(id)){const el=node();el.id=id;elements.set(id,el);}return elements.get(id);}
element('atlas-content').hidden=true;element('atlas-minimum').value='10';element('atlas-direction').value='all';
const context={TextEncoder,URL,AbortController,crypto:require('node:crypto').webcrypto,
 document:{getElementById:element,createElement:node,createElementNS:(ns,tag)=>node(tag)},
 fetch:path=>{paths.push(path);const response={ok:true,text:async()=>JSON.stringify(input.atlas)};return input.delayFetch?new Promise(resolve=>{finishFetch=()=>resolve(response);}):Promise.resolve(response);}
};
vm.createContext(context);
for(const name of ['workspace.js','window-atlas.js'])vm.runInContext(fs.readFileSync('static/'+name,'utf8'),context);
const api=context.ClimateWindowAtlas;
api.mount({onIntent(){return++intent;},async openAnalysis(analysis,state){opened.push({analysis,current:state.isCurrent()});return true;},revealChart(){chartReveals++;}});
api.setAnalysis(input.current||input.atlas.base_analysis,input.config);
(async()=>{
 if(input.operation==='validate'){
  try{await api.validate(input.atlas);process.stdout.write(JSON.stringify({valid:true}));}
  catch(error){process.stdout.write(JSON.stringify({valid:false,error:error.message}));}return;
 }
 if(input.operation==='switchPending'){
  const loading=element('atlas-load').handlers.click();
  const other={...input.atlas.base_analysis,location:input.config.presets.berlin};
  api.setAnalysis(other,input.config);finishFetch();await loading;
 }else{
  await element('atlas-load').handlers.click();
  const cell=(start,end)=>element('atlas-chart').children.find(child=>child.attributes['aria-label']?.startsWith(`${start}–${end},`));
  if(input.operation==='filter'){
   element('atlas-direction').value='negative';element('atlas-direction').handlers.change();
   await element('atlas-open').handlers.click();
  }else if(input.operation==='keyboard'){
   const target=cell(1981,2025);target.handlers.keydown({key:'ArrowLeft',preventDefault(){}});
   await element('atlas-open').handlers.click();
  }else if(input.operation==='selected'){
   cell(input.start,input.end).handlers.click();await element('atlas-open').handlers.click();
  }else if(input.operation==='pauseOpen'){
   const opening=element('atlas-open').handlers.click();api.pause();await opening;
  }else if(input.operation==='pagination'){
   element('atlas-page-next').handlers.click();
  }
 }
 const state={};for(const[id,value]of elements)state[id]={text:value.textContent,hidden:value.hidden,disabled:value.disabled,href:value.href};
 process.stdout.write(JSON.stringify({state,opened,paths,focus,chartReveals,cellCount:element('atlas-chart').children.filter(child=>child.tag==='rect').length,tablePeriods:element('atlas-table-body').children.map(tr=>tr.children[0].children[0].textContent)}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


APP_HARNESS = r"""
const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const elements=new Map(),requests=[],storage=new Map();
function node(tag='element'){
 return{tag,children:[],attributes:{},handlers:{},style:{},hidden:false,disabled:false,value:'',checked:false,textContent:'',
  classList:{toggle(){}},setAttribute(key,value){this.attributes[key]=value;},setCustomValidity(){},reportValidity(){return true;},
  append(...items){this.children.push(...items);},replaceChildren(...items){this.children=items;},
  addEventListener(type,callback){this.handlers[type]=callback;},focus(){},scrollIntoView(){},querySelector(){return{remove(){}};}
 };
}
function element(id){if(!elements.has(id)){const el=node();el.id=id;elements.set(id,el);}return elements.get(id);}
for(const[id,value]of Object.entries({location:'tehran',start:'1981',end:'2025',latitude:'35.6892',longitude:'51.389',window:'full45','investigation-question':'My question','investigation-interpretation':'My interpretation','investigation-uncertainty':'My uncertainty','atlas-minimum':'10','atlas-direction':'all'}))element(id).value=value;
const context={input,TextEncoder,URL,URLSearchParams,AbortController,setTimeout,clearTimeout,
 crypto:require('node:crypto').webcrypto,
 document:{getElementById:element,createElement:node,createElementNS:(ns,tag)=>node(tag),querySelector:selector=>selector.startsWith('meta')?null:{value:'rainfall'}},
 window:{addEventListener(){}},localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
 fetch:path=>path==='atlas/tehran-rainfall.json'?Promise.resolve({ok:true,text:async()=>JSON.stringify(input.atlas)}):new Promise((resolve,reject)=>requests.push({path,resolve,reject}))
};
vm.createContext(context);
for(const name of ['workspace.js','window-atlas.js','app.js'])vm.runInContext(fs.readFileSync('static/'+name,'utf8'),context);
vm.runInContext('config=input.config;currentResult=input.atlas.base_analysis;currentName="Tehran, Iran";render=record=>ClimateWindowAtlas.setAnalysis(record,config);ClimateWindowAtlas.setAnalysis(currentResult,config);',context);
(async()=>{
 if(input.operation==='staleFailure'){
  const first=context.explore(),second=context.explore();
  const climate=requests.filter(request=>request.path.startsWith('api/climate?'));
  climate[1].resolve({ok:true,json:async()=>input.atlas.base_analysis});await second;
  climate[0].reject(new Error('Old request failed'));await first;
 }else{
  await element('atlas-load').handlers.click();
  const target=element('atlas-chart').children.find(cell=>cell.attributes['aria-label']?.startsWith('1990–2007,'));
  target.handlers.click();await element('atlas-open').handlers.click();
 }
 const notes=['investigation-question','investigation-interpretation','investigation-uncertainty'].map(id=>element(id).value);
 process.stdout.write(JSON.stringify({notes,analysis:vm.runInContext('currentResult',context),name:vm.runInContext('currentName',context),banner:element('import-status').textContent,errorHidden:element('error').hidden,error:element('error-text').textContent}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


@unittest.skipUnless(shutil.which("node"), "Node is needed for atlas browser interaction tests")
class WindowAtlasUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        saved = json.loads((ROOT / "evaluation/source-snapshots/tehran-power.json").read_text())
        base = analyze_saved({"start": 1981, "end": 2025, "variable": "rainfall"}, saved)
        base["location_name"] = "Tehran, Iran"
        cls.atlas = build_window_atlas(base)
        cls.config = {"presets": PRESETS}

    def run_ui(self, operation="load", atlas=None, **options):
        result = subprocess.run(
            ["node", "-e", HARNESS], input=json.dumps({"atlas": atlas or self.atlas, "config": self.config, "operation": operation, **options}),
            text=True, capture_output=True, check=True, cwd=ROOT, timeout=20,
        )
        return json.loads(result.stdout)

    def run_app(self, operation="selected"):
        atlas = copy.deepcopy(self.atlas)
        atlas["base_analysis"].pop("location_name", None)
        result = subprocess.run(
            ["node", "-e", APP_HARNESS], input=json.dumps({"atlas": atlas, "config": self.config, "operation": operation}),
            text=True, capture_output=True, check=True, cwd=ROOT, timeout=20,
        )
        return json.loads(result.stdout)

    def test_all_666_windows_render_and_table_is_chronological(self):
        result = self.run_ui()
        self.assertEqual(result["cellCount"], 666)
        self.assertEqual(result["paths"], ["atlas/tehran-rainfall.json"])
        self.assertEqual(result["tablePeriods"][:2], ["1981–1990", "1981–1991"])
        self.assertEqual(len(result["tablePeriods"]), 30)
        self.assertIn("Showing 666 of 666", result["state"]["atlas-counts"]["text"])
        self.assertEqual(result["opened"], [])

    def test_display_filter_keeps_full_basis_and_selected_window(self):
        result = self.run_ui("filter")
        expected = sum(row["slope_per_decade"] < 0 for row in self.atlas["windows"])
        self.assertEqual(result["cellCount"], expected)
        self.assertIn(f"Showing {expected} of 666", result["state"]["atlas-counts"]["text"])
        self.assertFalse(result["state"]["atlas-selection-hidden"]["hidden"])
        self.assertEqual(result["opened"][0]["analysis"]["period"], {"start": 1981, "end": 2025})
        self.assertEqual(verify(result["opened"][0]["analysis"]), 45)

    def test_keyboard_navigation_selects_adjacent_end_year_and_opens_exact_evidence(self):
        result = self.run_ui("keyboard")
        self.assertIn("1981–2024", result["focus"])
        self.assertEqual(result["opened"][0]["analysis"]["period"], {"start": 1981, "end": 2024})
        self.assertEqual(verify(result["opened"][0]["analysis"]), 44)
        self.assertEqual(result["chartReveals"], 1)

    def test_selected_interior_period_materializes_full_replayable_analysis(self):
        result = self.run_ui("selected", start=1990, end=2007)
        record = result["opened"][0]["analysis"]
        self.assertEqual(record["period"], {"start": 1990, "end": 2007})
        self.assertEqual(verify(record), 18)
        self.assertEqual(record["window_atlas_context"]["candidate_windows"], 666)
        self.assertEqual(record["window_atlas_context"]["scope"], self.atlas["scope"])

    def test_pause_prevents_pending_selected_evidence_from_opening(self):
        result = self.run_ui("pauseOpen")
        self.assertEqual(result["opened"], [])
        self.assertFalse(result["state"]["atlas-open"]["disabled"])

    def test_case_change_discards_late_atlas_load(self):
        result = self.run_ui("switchPending", delayFetch=True)
        self.assertTrue(result["state"]["atlas-content"]["hidden"])
        self.assertIn("Berlin", result["state"]["atlas-load"]["text"])
        self.assertEqual(result["cellCount"], 0)

    def test_pagination_retains_chronological_order(self):
        result = self.run_ui("pagination")
        self.assertEqual(result["tablePeriods"][0], "1981–2020")
        self.assertIn("Page 2 of 23", result["state"]["atlas-page-status"]["text"])

    def test_different_current_source_is_explained_before_switching_evidence(self):
        current = copy.deepcopy(self.atlas["base_analysis"])
        current["provenance"]["payload_sha256"] = "f" * 64
        result = self.run_ui(current=current)
        self.assertIn("differs from the current chart source", result["state"]["atlas-source-note"]["text"])
        self.assertEqual(result["opened"], [])

    def test_missing_windows_tampered_points_and_missing_scope_are_rejected(self):
        for changed in ["missing", "point", "scope", "basis"]:
            atlas = copy.deepcopy(self.atlas)
            if changed == "missing": atlas["windows"].pop()
            elif changed == "point": atlas["windows"][0]["slope_per_decade"] += 1
            elif changed == "scope": atlas["scope"].pop()
            else: atlas["basis"]["unit"] = "wrong unit"
            with self.subTest(changed=changed):
                result = self.run_ui("validate", atlas=atlas)
                self.assertFalse(result["valid"])

    def test_actual_app_selected_window_preserves_notes_and_preset_identity(self):
        result = self.run_app()
        self.assertEqual(result["notes"], ["My question", "My interpretation", "My uncertainty"])
        self.assertEqual(result["name"], "Tehran, Iran")
        self.assertIn("Window atlas evidence", result["banner"])
        self.assertIn("Your notes are preserved", result["banner"])
        self.assertEqual(verify(result["analysis"]), 18)

    def test_actual_app_stale_non_abort_error_cannot_replace_newer_result(self):
        result = self.run_app("staleFailure")
        self.assertTrue(result["errorHidden"])
        self.assertNotIn("Old request failed", result["error"])
        self.assertEqual(verify(result["analysis"]), 45)

    def test_incomplete_years_make_short_window_unavailable_without_compressing_time(self):
        saved = json.loads((ROOT / "evaluation/source-snapshots/tehran-power.json").read_text())
        saved["payload"]["properties"]["parameter"]["PRECTOTCORR"]["198506"] = -999
        base = analyze_saved({"start": 1981, "end": 1992, "variable": "rainfall"}, saved)
        atlas = build_window_atlas(base)
        result = self.run_ui("selected", atlas=atlas, start=1981, end=1990)
        self.assertEqual(result["cellCount"], 6)
        self.assertIn("9 complete years", result["state"]["atlas-selected"]["text"])
        self.assertTrue(result["state"]["atlas-open"]["disabled"])
        self.assertEqual(result["opened"], [])


if __name__ == "__main__":
    unittest.main()
