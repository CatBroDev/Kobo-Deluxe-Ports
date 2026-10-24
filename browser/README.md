# Kobo Deluxe 0.5.1 — browser restoration

Play: https://oldgamesarchive.org/games/kobodeluxe
中文：https://oldgamesarchive.org/zh-cn/games/kobodeluxe

Kobo Deluxe is David Olofson's enhanced port of XKobo by Akira Higuchi. Original contributors include Masanao Izumo and Erik Auerswald. This build uses the community SDL2 port by ruohoruotsi and contributors; it is not a DOS executable and is not the first browser port.

## Source and attribution

- Author project: https://github.com/olofson/kobodeluxe (reference snapshot `943aa38f941e4f463863d56c8aac6f23a2ef663b`).
- Actual build source: https://github.com/ruohoruotsi/Kobo-Deluxe-Ports/tree/2edc48fc17e21af4ff20912b6205bb0025f8f909/KoboDeluxe-0.5.1
- Official documentation: https://olofson.net/kobodl/
- Game: GPL-2.0-or-later. Individual LGPL library headers and the original `COPYING.LIB`, `README.sfont`, `README.xkobo` and author credits remain in the source download. Original artwork and synthesized sound scripts are retained. SDL2, SDL2_image, libpng, zlib and Emscripten notices accompany this build. This does not change any upstream file's license.
- Browser integration: Old Games Archive / CatBroDev, GPL-2.0-or-later.

## Browser changes

The build removes Mac-only path/timing dependencies, resolves the `pipe2` libc symbol collision, corrects six audio-table definitions for modern Clang, and asks SDL to convert the device format to the original S16 callback format. Asyncify yields the native game loop without rewriting the game. Host pause uses a stopped game clock; key release clears all native button states; mute gates the real audio output. Quit follows the original abort, score, configuration and SDL cleanup path.

IDBFS uses `oldgames-kobodeluxe-v1`. Player files live in `/persistent_data/scores`; configuration lives outside that directory so the legacy score scanner cannot mistake configuration text for a score. Browser configuration saving omits the inapplicable POSIX setgid step. Writes are serialized and flushed before a normal shutdown finishes. The original AGW sound scripts synthesize effects/music locally; no broken cached-wave files are requested. An unused 1024×768 developer image and Makefiles are excluded from the download, preserved in source.

## Controls and saves

Arrows steer in eight directions; Ctrl or Shift fires the nose and tail weapons. Enter confirms menus/player names; Space starts; Esc opens the menu; P pauses; Y/N answer confirmation prompts. Shared touch controls can be configured from the website. For a first game, confirm a player name, choose Start Game and select a skill level; Newbie is the gentlest option.

The game saves profiles, scores, settings and completed-stage progress. It does **not** save the exact position or an unfinished fight. Use the native Quit menu before closing when possible. Browser data clearing/private-session expiry removes saves; storage is local to this site, browser and device, without cloud sync. English in-game menus are preserved. First-stage controls, audio, pause, exit and profile restoration are tested; full completion and physical Android/iOS performance are not certified.

## Build and test

See [BUILD.md](BUILD.md) for the pinned SDK, reproducible build, source packaging,
and muted browser acceptance command. The standalone page provides keyboard controls;
the live website supplies the configurable shared mobile controller through host protocol v1.
