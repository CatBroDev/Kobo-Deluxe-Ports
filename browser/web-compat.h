#include <SDL.h>
#include <emscripten.h>
#ifdef __cplusplus
extern "C" {
#endif
void oga_sleep(unsigned ms);
unsigned oga_ticks(void);
void oga_ready(void);
int oga_paused(void);
void oga_audio_gate(void *stream, int length);
#ifdef __cplusplus
}
#endif
#define SDL_Delay(ms) oga_sleep(ms)
#define SDL_GetTicks() oga_ticks()
