from pathlib import Path
import re,json,shutil,sys,os,subprocess,time
lab=Path(__file__).resolve().parent;src=lab.parent/'KoboDeluxe-0.5.1';out=lab/'build'/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
shutil.copytree(src,out/'src',ignore=shutil.ignore_patterns('*.o','*.a','kobodl','Makefile.in','Makefile','config.log','autom4te.cache'))
sdk=Path(os.environ.get('KOBO_EMSDK',str(lab/'emsdk')));env=dict(os.environ,EM_CONFIG=str(sdk/'.emscripten'),EMSDK_PYTHON=sys.executable,EMCC_CORES='4',TEMP=str(out),TMP=str(out))
# Remove Mac-only diagnostic timing; retain actual sound loading.
p=out/'src/kobo.cpp';t=p.read_text();t=re.sub(r'#include <(?:CoreFoundation|Accelerate|mach)/[^>]+>[^\n]*','',t)
a=t.index('    // TIMING BENCHMARKS');b=t.index('\n\twdash->progress_done();',a)
t=t[:a]+'\n\tif(load_sounds(prefs) < 0) return -3;\n'+t[b:]
t=t.replace('setupWorkingDirectory(false);','/* Web data paths are explicit. */')
t=re.sub(r'^#define (?:KOBO_DATA_DIR|KOBO_SCORE_DIR|KOBO_CONFIG_DIR|KOBO_CONFIG_FILE|SYSCONF_DIR) .*$', '', t, flags=re.M)
p.write_text(t.replace('#if defined(HAVE_GETEGID) && defined(HAVE_SETGID)', '#if defined(HAVE_GETEGID) && defined(HAVE_SETGID) && !defined(__EMSCRIPTEN__)'))
for p in (out/'src').rglob('*'):
 if p.suffix in ['.cpp','.c','.h']:
  t=p.read_bytes();p.write_bytes(re.sub(rb'\bpipe2\b',b'kobo_pipe2',t))
p=out/'src/graphics/window.cpp';t=p.read_text();t=t.replace('char *tok = strchr(txt, token);','const char *tok = strchr(txt, token);');p.write_text(t)
p=out/'src/sound/a_struct.h';t=p.read_text();decls=re.findall(r'^audio_\w+_t (?:wavetab|patchtab|grouptab|channeltab|voicetab|bustab)\[[^;]+;',t,re.M);assert len(decls)==6
for d in decls:t=t.replace(d,'extern '+d)
p.write_text(t)
p=out/'src/sound/audio.c';t=p.read_text();t=t.replace('SDL_AudioSpec as;','SDL_AudioSpec as = {0};').replace('if(SDL_OpenAudio(&as, &audiospec) < 0)','if(SDL_OpenAudio(&as, NULL) < 0)').replace('if(audiospec.format != AUDIO_S16SYS)','audiospec = as; // SDL converts the device format to the requested S16 callback format.\n\tif(audiospec.format != AUDIO_S16SYS)');p.write_text(t)
# Yield the existing main loop under Asyncify; keep native gameplay intact.
p=out/'src/graphics/gfxengine.cpp';t=p.read_text();assert 'while(is_running)\n\t{' in t;t=t.replace('while(is_running)\n\t{','while(is_running)\n\t{\n\t\toga_sleep(1);');p.write_text(t)
compat=(lab/'web-compat.h').read_text();(out/'compat.h').write_text(compat)
shutil.copy2(lab/'web-browser.cpp',out/'src/web-browser.cpp')
p=out/'src/kobo.cpp';s=p.read_text();s=s.replace('\n\tkm.run();','\n\toga_ready();\n\tkm.run();')
s=s.replace('static KOBO_main km;', 'static KOBO_main km;\nextern "C" EMSCRIPTEN_KEEPALIVE void oga_checkpoint(){if(prefs && prefs->changed){km.save_config(prefs);prefs->changed=0;}}\nextern "C" void oga_stop_native(){km.exit_game_fast=1;exit_game=1;if(gengine)gengine->stop();}\n');p.write_text(s)
p=out/'src/sound/audio.c';s=p.read_text();anchor='static void _audio_callback(void *ud, Uint8 *stream, int len)';assert anchor in s
s=s.replace(anchor,'static void _audio_render(void *ud, Uint8 *stream, int len);\nstatic void _audio_callback(void *ud, Uint8 *stream, int len){\n if(oga_paused()){memset(stream,0,len);return;}\n _audio_render(ud,stream,len);oga_audio_gate(stream,len);\n}\nstatic void _audio_render(void *ud, Uint8 *stream, int len)');p.write_text(s)
files=json.loads((lab/'sources.json').read_text())
files.append('web-browser.cpp')
inc=['-I'+str(out),'-I'+str(out/'src'),*['-I'+str(out/'src'/n) for n in ['graphics','sound','eel']],'-I'+str(src/'data/sfx')]
base=(['-DOGA_DIAGNOSTIC'] if '--state' in sys.argv else [])+['-O1','-DHAVE_CONFIG_H','-DKOBO_DATA_DIR="/data"','-DKOBO_SCORE_DIR="/persistent_data/scores"','-DKOBO_CONFIG_DIR="/persistent_data"','-DKOBO_CONFIG_FILE="kobodeluxe.cfg"','-DSYSCONF_DIR="/persistent_data"','-sUSE_SDL=2','-sUSE_SDL_IMAGE=2','-sSDL2_IMAGE_FORMATS=["png"]','-include',str(out/'compat.h'),*inc,'-Wno-incompatible-pointer-types','-Wno-deprecated-non-prototype']
objects=[];start=time.monotonic();log=(out/'build.log').open('w')
for name in files:
 f=out/'src'/name;o=out/(name.replace('/','_')+'.o');compiler='em++.py' if f.suffix=='.cpp' else 'emcc.py'
 r=subprocess.run([sys.executable,str(sdk/'upstream/emscripten'/compiler),*base,'-c',str(f),'-o',str(o)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=35)
 if r.returncode:log.close();print((out/'build.log').read_text()[-5000:]);sys.exit(r.returncode)
 objects.append(o)
# Omit unused development files from the download, preserve all originals in source.
data=out/'data';shutil.copytree(src/'data',data,ignore=shutil.ignore_patterns('Makefile*','screen2_1024_768.png'))
for f in (lab/'web').iterdir():shutil.copy2(f,out/f.name)
flags=['-O1','-sUSE_SDL=2','-sUSE_SDL_IMAGE=2','-sSDL2_IMAGE_FORMATS=["png"]','-sASYNCIFY','-sASYNCIFY_STACK_SIZE=131072','-sSTACK_SIZE=1048576','-sALLOW_MEMORY_GROWTH=1','-sFORCE_FILESYSTEM=1','-sEXPORTED_RUNTIME_METHODS=["FS","IDBFS","callMain","addRunDependency","removeRunDependency"]','-sEXIT_RUNTIME=1','-lidbfs.js','--preload-file',str(data)+'@/data','--use-preload-plugins','-o',str(out/'kobo.js')]
r=subprocess.run([sys.executable,str(sdk/'upstream/emscripten/em++.py'),*[str(o) for o in objects],*flags],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120);log.close();result={'exitCode':r.returncode,'seconds':round(time.monotonic()-start,1),'units':len(files)};(out/'build-result.json').write_text(json.dumps(result));print(json.dumps(result))
if r.returncode:print((out/'build.log').read_text()[-5000:]);sys.exit(r.returncode)

for ext in ['wasm','data']:shutil.copy2(out/('kobo.'+ext),out/('kobo.'+ext+'.bin'))
