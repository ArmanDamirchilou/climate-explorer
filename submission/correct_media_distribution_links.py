"""Replace retired distribution text in retained films; copy all audio packets."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont
from build_story_video import Painter, FONT_PATHS, BOLD_PATHS, PALE, INK, MUTED, ease

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'tmp/distribution-link-correction'
URL = 'github.com/ArmanDamirchilou/climate-explorer'
FONT = next(x for x in FONT_PATHS if Path(x).exists())
BOLD = next(x for x in BOLD_PATHS if Path(x).exists())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]).stdout)


def stream_hash(path, pcm=False):
    args = ['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-vn']
    args += ['-c:a', 'pcm_f32le'] if pcm else ['-c:a', 'copy']
    args += ['-f', 'hash', '-hash', 'sha256', '-']
    result = run(args)
    if result.stderr:
        raise RuntimeError(result.stderr.decode())
    return result.stdout.decode().strip().split('=')[-1]


def panel(name, size, text, font_size, bold, fill):
    im = Image.new('RGBA', size, PALE)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(BOLD if bold else FONT, font_size)
    y = 0
    for line in text.split('\n'):
        if d.textlength(line, font=font) > size[0] - 8:
            raise ValueError('Link text does not fit correction panel')
        d.text((4, y), line, font=font, fill=fill)
        y += round(font_size * 1.22)
    path = WORK / (name + '.png')
    im.save(path)
    return path


class LinkPainter(Painter):
    def text(self, value, *args, **kwargs):
        if value == 'armandamirchilou.github.io/climate-explorer/':
            value = URL
        return super().text(value, *args, **kwargs)


def judge_patch_video():
    # Only a 696x48 crop is recomposed. At crossfades the original chart renderer
    # retains the same scientific labels; no graph or caption is masked wholesale.
    dest = WORK / 'judge-link-patch.mov'
    full = json.loads((ROOT / 'submission/story-inputs/tehran-rainfall.json').read_text())
    recent = json.loads((ROOT / 'submission/story-inputs/tehran-recent15-rainfall.json').read_text())
    command = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pixel_format', 'rgba', '-video_size', '696x48', '-framerate', '30', '-i', '-', '-an', '-c:v', 'qtrle', str(dest)]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    painter = LinkPainter(False, FONT, BOLD)
    for index in range(894):
        t = index / 30
        image = painter.presenter_overlay(t, False)
        alpha = min(ease((t - 4.9) / .22), ease((22.3 - t) / .24))
        if alpha > 0:
            chart = painter.chart(t, full, recent, False)
            if alpha < 1:
                chart.putalpha(chart.getchannel('A').point(lambda v: round(v * alpha)))
            image = Image.alpha_composite(image, chart)
        proc.stdin.write(image.crop((80, 744, 776, 792)).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError('Small judge correction-patch encode failed')
    return dest


def encode(mode):
    stem = 'climate-explorer-story-' + mode
    original = WORK / (stem + '.mp4')
    if not original.exists():
        raise ValueError('Preserve the original film in ignored tmp before correction')
    old = json.loads((WORK / (stem + '.json')).read_text())
    if digest(original) != old['sha256']:
        raise ValueError('Preserved original hash differs from its review record')
    target = WORK / (stem + '-corrected.mp4')
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(original)]
    if mode == 'judge':
        asset = judge_patch_video()
        command += ['-i', str(asset)]
        filters = "[0:v][1:v]overlay=x=80:y=744:enable='lt(t,5.12)+gte(t,22.0666666667)'[v]"
        rectangles = [{'xywh': [80,744,696,48], 'seconds': [[0,5.12],[22.0666666667,29.8]], 'method':'Original source-built URL crop, preserving the chart crossfade and existing labels'}]
    elif mode == 'reel':
        asset = panel('reel-link', (930,114), 'github.com/ArmanDamirchilou\n/climate-explorer', 42, True, INK)
        command += ['-loop', '1', '-i', str(asset)]
        filters = "[0:v][1:v]overlay=x=59:y=1297:enable='gte(t,40)'[v]"
        rectangles = [{'xywh':[59,1297,930,114], 'seconds':[[40,45]], 'method':'Opaque source-built URL text panel'}]
    else:
        small = panel('technical-source-link', (850,48), URL, 24, False, MUTED)
        large = panel('technical-end-link', (1130,66), URL, 45, True, INK)
        command += ['-loop','1','-i',str(small),'-loop','1','-i',str(large)]
        # Full-screen correction plates supersede the source label. Final endcard
        # begins at source t>22, i.e. the first frame strictly after global130.
        active = "gte(t,108)*lte(t,130)*not(between(t,115.07,117.93))*not(between(t,127.12,130))"
        # The exact130.000 frame shows the base source label (audio plate guard
        # intentionally stops at local22); include that one frame explicitly.
        active = '(' + active + ')+eq(n,3900)'
        filters = f"[0:v][1:v]overlay=x=59:y=774:enable='{active}'[a];[a][2:v]overlay=x=59:y=460:enable='gt(t,130)'[v]"
        rectangles = [
            {'xywh':[59,774,850,48], 'seconds':[[108,115.07],[117.93,127.12],[130,130.0333333333]], 'method':'Opaque URL text panel; omitted wherever a full-screen correction plate supersedes the source label'},
            {'xywh':[59,460,1130,66], 'seconds':[[130.0333333333,135]], 'method':'Opaque endcard URL text panel'}]
    command += ['-filter_complex',filters,'-map','[v]','-map','0:a:0','-map_metadata','0','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-t',str(old['duration_seconds']),'-movflags','+faststart',str(target)]
    run(command)
    details = probe(target)
    video = next(s for s in details['streams'] if s['codec_type']=='video')
    audio = next(s for s in details['streams'] if s['codec_type']=='audio')
    original_probe = probe(original)
    ov = next(s for s in original_probe['streams'] if s['codec_type']=='video')
    for key in ['width','height','r_frame_rate','nb_frames']:
        if video[key] != ov[key]:
            raise ValueError('Video geometry/timing changed: '+key)
    stream_before,stream_after = stream_hash(original),stream_hash(target)
    pcm_before,pcm_after = stream_hash(original,True),stream_hash(target,True)
    if stream_before!=stream_after or pcm_before!=pcm_after:
        raise ValueError('Copied audio differs')
    decode = run(['ffmpeg','-v','warning','-i',str(target),'-f','null','-'])
    if decode.stderr:
        raise ValueError('Full decode warnings: '+decode.stderr.decode())
    old.update({'sha256':digest(target),'bytes':target.stat().st_size,'duration_seconds':float(details['format']['duration']),'frame_count':int(video['nb_frames']),'video_codec':video['codec_name'],'audio_codec':audio['codec_name']})
    old['distribution_link_correction']={
        'reason':'Retired GitHub Pages destination replaced by stable source-repository address after hosting migration',
        'replacement_text':URL,'source_original_sha256':digest(original),'source_original_record_sha256':digest(WORK/(stem+'.json')),
        'script':'submission/correct_media_distribution_links.py','script_sha256':digest(__file__),
        'rectangles':rectangles,'audio_processing':'-c:a copy; no audio filtering or encoding',
        'compressed_audio_sha256_before':stream_before,'compressed_audio_sha256_after':stream_after,
        'decoded_float_pcm_sha256_before':pcm_before,'decoded_float_pcm_sha256_after':pcm_after,
        'original_builder_sha256':old.get('builder_sha256'),
        'provenance_scope':'builder_sha256 identifies the original composition; this correction script is the final distribution-text pass',
        'full_decode_passed':True,'encoded_visual_review':False,'checked_utc':datetime.now(timezone.utc).isoformat()}
    (WORK/(stem+'-corrected.json')).write_text(json.dumps(old,indent=2)+'\n')
    print(json.dumps({'mode':mode,'path':str(target.relative_to(ROOT)),'sha256':old['sha256'],'bytes':old['bytes'],'audio_copy_and_pcm_identical':True}),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['judge','reel','technical','all'],default='all')
    args=p.parse_args()
    WORK.mkdir(parents=True,exist_ok=True)
    for mode in (['judge','reel','technical'] if args.mode=='all' else [args.mode]):
        encode(mode)


if __name__=='__main__':
    main()
