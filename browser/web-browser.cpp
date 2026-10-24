// GPL-2.0-or-later. Browser integration: Old Games Archive / CatBroDev.
// Original game and SDL2 port copyrights remain in the source files/notices.
#include <SDL.h>
#include <emscripten.h>
#include <cstring>
#include "gamectl.h"
#undef SDL_GetTicks
#undef SDL_Delay
static int paused=0,stopping=0,muted=1,ready=0;
static Uint32 pauseStart=0,pauseTotal=0;
extern "C" {
void oga_stop_native();
EMSCRIPTEN_KEEPALIVE void oga_release(){SDL_ResetKeyboard();SDL_FlushEvents(SDL_KEYDOWN,SDL_MOUSEWHEEL);for(int key=BTN_UP;key<=BTN_FIRE;++key)gamecontrol.release(key);}
EMSCRIPTEN_KEEPALIVE void oga_pause(int value){oga_release();if(value&&!paused)pauseStart=SDL_GetTicks();if(!value&&paused)pauseTotal+=SDL_GetTicks()-pauseStart;paused=value!=0;}
EMSCRIPTEN_KEEPALIVE int oga_paused(){return paused;}
EMSCRIPTEN_KEEPALIVE void oga_mute(int value){muted=value!=0;}
EMSCRIPTEN_KEEPALIVE void oga_stop(){stopping=1;oga_pause(0);oga_stop_native();}
unsigned oga_ticks(){return (paused?pauseStart:SDL_GetTicks())-pauseTotal;}
void oga_ready(){ready=1;EM_ASM(if(Module.onGameReady)Module.onGameReady(););}
void oga_sleep(unsigned ms){do{emscripten_sleep(paused?30:(ms?ms:1));}while(paused&&!stopping);}
void oga_audio_gate(void *stream,int length){if(muted||paused||stopping)std::memset(stream,0,length);}
}
#ifdef OGA_DIAGNOSTIC
#include "myship.h"
#include "manage.h"
extern "C" EMSCRIPTEN_KEEPALIVE int oga_state(int i){switch(i){case 0:return myship.get_x();case 1:return myship.get_y();case 2:return myship.health();case 3:return manage.game_stopped();case 4:return manage.scene();case 5:return myship.get_nose_temp();case 6:return manage.ships;case 7:return gamecontrol.get_shot();case 8:return gamecontrol.dir_push();default:return -1;}}
#endif
