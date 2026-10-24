# Browser build

This branch preserves upstream commit `2edc48fc17e21af4ff20912b6205bb0025f8f909`.
The actual game source is `KoboDeluxe-0.5.1/`; the other historic ports remain untouched.
The source list in `sources.json` is derived from David Olofson's author-reference
`src/CMakeLists.txt` at `943aa38f941e4f463863d56c8aac6f23a2ef663b`.

Install Python 3, Node.js and Emscripten 4.0.23. Set `KOBO_EMSDK` to the SDK root.
The build uses the SDK's SDL2, SDL2_image, PNG and zlib ports; it does not compile the
historical SDL copies in the repository. Use UTF-8 mode, including on Windows:

```sh
python -X utf8 browser/build-browser.py release-local
python -X utf8 browser/package-release.py release-local
```

Use a fresh output name each time. Output goes to `browser/build/release-local/`.
All patches apply to a build copy; upstream source and copyright headers stay intact.
Do not pass `--state` for releases: it enables local diagnostic exports.
The package command rejects diagnostic builds and emits notices, the complete
corresponding source ZIP, and file hashes. Serve this directory over HTTP;
`.wasm.bin` should use `application/wasm`. Open `index.html` and press Start.

Optional automated acceptance (Chrome installed):

```sh
npm install --prefix browser
node browser/accept-release.mjs release-local check-01
```

It runs with `--mute-audio`, checks first-stage movement/fire, nonzero audio samples
without speaker output, mute/pause, native Quit and profile/configuration recovery
after closing the browser. It closes its browser and HTTP server in `finally`.
Evidence goes to `browser/evidence/check-01/`. Full completion, later-stage unlocks,
physical phones and native macOS builds have not been certified by these tests.
