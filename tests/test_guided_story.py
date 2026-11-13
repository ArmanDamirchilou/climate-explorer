import copy
import json
import shutil
import subprocess
import unittest

from climate import ROOT
from evaluation.replay import verify


HARNESS = r"""
const fs = require('fs'), vm = require('vm');
const input = JSON.parse(fs.readFileSync(0,'utf8'));
const elements = new Map(), opened = [], paths = [];
let focus = null, chartReveals = 0, ownExplores = 0, intent = 0, finishFetch;
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    hidden: id === 'story-panel', disabled:false, textContent:'', style:{}, attributes:{}, handlers:{},
    classList:{toggle() {}},
    setAttribute(key,value) { this.attributes[key] = value; },
    addEventListener(type,callback) { this.handlers[type] = callback; },
    focus() { focus = id; },
    set innerHTML(value) { throw new Error('Story text must not be inserted as HTML'); }
  });
  return elements.get(id);
}
const response = {ok:!input.failFetch,text:async()=>JSON.stringify(input.story)};
const context = {
  TextEncoder, URL, AbortController, crypto:require('node:crypto').webcrypto,
  document:{getElementById:element},
  fetch: (path,options) => {
    paths.push(path);
    return input.delayFetch ? new Promise(resolve=>{finishFetch=()=>resolve(response);}) : Promise.resolve(response);
  }
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('static/workspace.js','utf8'),context);
vm.runInContext(fs.readFileSync('static/guided-story.js','utf8'),context);
const api = context.ClimateStory;
api.mount({
  onIntent() { return ++intent; },
  async openAnalysis(record,state) { opened.push({period:record.period,variable:record.variable,current:state.isCurrent(),intent:state.intent}); return true; },
  revealChart() { chartReveals++; },
  exploreOwn() { ownExplores++; }
});
async function click(id) { await element(id).handlers.click(); }
(async()=>{
  if (input.operation === 'pausePending') {
    const starting = element('story-start').handlers.click();
    api.pause(); finishFetch(); await starting;
  } else {
    await click('story-start');
    if (input.operation === 'threeSteps') {
      await click('story-next'); await click('story-next');
      element('story-claim').handlers.change({target:{value:'reversal'}});
    } else if (input.operation === 'chartNavigation') {
      await click('story-next'); await click('story-open-chart');
      await click('story-next'); await click('story-open-full'); await click('story-open-recent');
    } else if (input.operation === 'complete') {
      await click('story-next'); await click('story-next');
      element('story-claim').handlers.change({target:{value:'periods'}});
      await click('story-next');
    } else if (input.operation === 'close') await click('story-close');
  }
  const state = {};
  for (const [id,value] of elements) state[id] = {hidden:value.hidden,disabled:value.disabled,text:value.textContent,attributes:value.attributes,style:value.style};
  process.stdout.write(JSON.stringify({state,opened,paths,focus,chartReveals,ownExplores}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


APP_HARNESS = r"""
const fs = require('fs'), vm = require('vm');
const input = JSON.parse(fs.readFileSync(0,'utf8'));
const elements = new Map(), requests = [], storage = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value:'',checked:false,hidden:false,textContent:'',style:{},handlers:{},
    classList:{toggle() {}},setAttribute() {},focus() {},scrollIntoView() {},
    addEventListener(type,callback) { this.handlers[type] = callback; },
    setCustomValidity() {},reportValidity() { return true; },
    querySelector() { return {remove() {}}; }
  });
  return elements.get(id);
}
for (const [id,value] of Object.entries({location:'tehran',start:'1981',end:'2025',latitude:'35.6892',longitude:'51.389',window:'full45','investigation-question':'My original question','investigation-interpretation':'My own interpretation','investigation-uncertainty':'I need more evidence'})) element(id).value=value;
const context = {
  input,TextEncoder,URL,URLSearchParams,AbortController,setTimeout,clearTimeout,
  crypto:require('node:crypto').webcrypto,
  localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
  document:{getElementById:element,querySelector:selector=>selector.startsWith('meta')?null:{value:'temperature'}},
  window:{addEventListener() {}},
  fetch:path=>path==='story-tehran.json'
    ? Promise.resolve({ok:true,text:async()=>JSON.stringify(input.story)})
    : new Promise(resolve=>requests.push({path,resolve}))
};
vm.createContext(context);
for (const name of ['workspace.js','guided-story.js','app.js']) vm.runInContext(fs.readFileSync('static/'+name,'utf8'),context);
vm.runInContext('render=()=>{};',context);
(async()=>{
  await element('story-start').handlers.click();
  await element('story-next').handlers.click();
  const storyNotes = ['investigation-question','investigation-interpretation','investigation-uncertainty'].map(id=>element(id).value);
  const storyBanner = element('import-status').textContent;
  if (input.manualImport) {
    await context.openInvestigation(JSON.stringify({format:'Climate Explorer investigation 1',analysis:input.story.analyses.full45,notes:{question:'Imported question',interpretation:'Imported interpretation',remaining_uncertainty:'Imported uncertainty'}}),'Imported evidence');
  }
  const notes = ['investigation-question','investigation-interpretation','investigation-uncertainty'].map(id=>element(id).value);
  process.stdout.write(JSON.stringify({storyNotes,storyBanner,notes,banner:element('import-status').textContent,state:vm.runInContext('({start:currentResult.period.start,variable:currentResult.variable})',context)}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


@unittest.skipUnless(shutil.which("node"), "Node is needed for guided-story interaction tests")
class GuidedStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.story = json.loads((ROOT / "static/story-tehran.json").read_text())

    def run_story(self, operation="start", story=None, **options):
        result = subprocess.run(
            ["node", "-e", HARNESS], input=json.dumps({"story": story or self.story, "operation": operation, **options}),
            cwd=ROOT, text=True, capture_output=True, check=True, timeout=10,
        )
        return json.loads(result.stdout)

    def run_app(self, manual_import=False):
        result = subprocess.run(
            ["node", "-e", APP_HARNESS], input=json.dumps({"story": self.story, "manualImport": manual_import}),
            cwd=ROOT, text=True, capture_output=True, check=True, timeout=10,
        )
        return json.loads(result.stdout)

    def test_both_story_records_have_full_offline_python_replay(self):
        self.assertEqual(verify(self.story["analyses"]["full45"]), 45)
        self.assertEqual(verify(self.story["analyses"]["recent15"]), 15)

    def test_start_opens_verified_full_record_and_uses_exact_derived_rate(self):
        result = self.run_story()
        self.assertEqual(result["paths"], ["story-tehran.json"])
        self.assertEqual(result["opened"][0]["period"], {"start": 1981, "end": 2025})
        self.assertEqual(result["opened"][0]["variable"], "rainfall")
        expected = f"+{self.story['analyses']['full45']['trend']['slope_per_decade']:.3f}"
        self.assertIn(expected, result["state"]["story-explanation"]["text"])
        self.assertEqual(result["state"]["story-step-0"]["attributes"]["aria-current"], "step")
        self.assertTrue(result["state"]["story-rate-recent"]["hidden"])
        self.assertEqual(result["focus"], "story-heading")

    def test_three_steps_keep_same_source_and_explain_changed_period_and_uncertainty(self):
        result = self.run_story("threeSteps")
        self.assertEqual([row["period"]["start"] for row in result["opened"]], [1981, 2011, 2011])
        self.assertEqual(result["paths"], ["story-tehran.json"])
        self.assertIn("different spans of history", result["state"]["story-explanation"]["text"])
        self.assertIn("includes zero", result["state"]["story-interval"]["text"])
        self.assertIn("do not establish a climate reversal", result["state"]["story-caution"]["text"])
        self.assertIn("does not establish a permanent climate reversal", result["state"]["story-claim-feedback"]["text"])
        self.assertFalse(result["state"]["story-claim"]["hidden"])
        self.assertFalse(result["state"]["story-rate-recent"]["hidden"])

    def test_chart_navigation_opens_the_requested_exact_record(self):
        result = self.run_story("chartNavigation")
        self.assertEqual(result["chartReveals"], 3)
        self.assertEqual([row["period"]["start"] for row in result["opened"]][-2:], [1981, 2011])
        self.assertTrue(all(row["current"] for row in result["opened"]))

    def test_pause_cancels_a_pending_story_before_any_chart_opens(self):
        result = self.run_story("pausePending", delayFetch=True)
        self.assertEqual(result["opened"], [])
        self.assertFalse(result["state"]["story-start"]["disabled"])
        self.assertTrue(result["state"]["story-load-status"]["hidden"])

    def test_source_or_analysis_tampering_prevents_story_display(self):
        story = copy.deepcopy(self.story)
        story["analyses"]["recent15"]["annual"][0]["value"] += 1
        result = self.run_story(story=story)
        self.assertEqual(result["opened"], [])
        self.assertIn("Recomputed value differs", result["state"]["story-load-status"]["text"])
        self.assertTrue(result["state"]["story-panel"]["hidden"])

    def test_failed_fetch_is_actionable_and_retry_remains_enabled(self):
        result = self.run_story(failFetch=True)
        self.assertEqual(result["opened"], [])
        self.assertIn("Try again", result["state"]["story-load-status"]["text"])
        self.assertFalse(result["state"]["story-start"]["disabled"])

    def test_selection_text_stays_plain_and_exposes_no_html_sink(self):
        story = copy.deepcopy(self.story)
        story["selection_note"] = '<img src=x onerror="alert(1)">'
        result = self.run_story(story=story)
        self.assertEqual(result["state"]["story-selection"]["text"], story["selection_note"])

    def test_completion_returns_to_explorer_without_creating_a_claim_for_the_user(self):
        result = self.run_story("complete")
        self.assertEqual(result["ownExplores"], 1)
        self.assertTrue(result["state"]["story-panel"]["hidden"])
        self.assertIn("Supported", result["state"]["story-claim-feedback"]["text"])

    def test_close_restores_keyboard_focus_to_start(self):
        result = self.run_story("close")
        self.assertEqual(result["focus"], "story-start")
        self.assertTrue(result["state"]["story-panel"]["hidden"])

    def test_actual_app_story_navigation_preserves_all_existing_notes(self):
        result = self.run_app()
        self.assertEqual(result["storyNotes"], ["My original question", "My own interpretation", "I need more evidence"])
        self.assertEqual(result["state"], {"start": 2011, "variable": "rainfall"})
        self.assertIn("Your notes are preserved", result["storyBanner"])
        self.assertIn("Uncertainty intervals are precomputed", result["storyBanner"])
        self.assertNotIn("Imported notes", result["storyBanner"])

    def test_actual_app_manual_import_still_replaces_notes_after_a_story(self):
        result = self.run_app(manual_import=True)
        self.assertEqual(result["notes"], ["Imported question", "Imported interpretation", "Imported uncertainty"])
        self.assertIn("Imported notes are user text", result["banner"])

    def test_markup_and_styles_keep_native_keyboard_and_reduced_motion_behavior(self):
        html = (ROOT / "static/index.html").read_text()
        script = (ROOT / "static/guided-story.js").read_text()
        styles = (ROOT / "static/style.css").read_text()
        for i in range(3):
            self.assertIn(f'id="story-step-{i}" type="button"', html)
        self.assertIn('name="story-claim"', html)
        self.assertNotIn("setInterval", script)
        self.assertNotIn("behavior: 'smooth'", script)
        self.assertIn(".story-content{grid-template-columns:1fr", styles)


if __name__ == "__main__":
    unittest.main()
