/*
 * File: web/js/build.js
 *
 * Which build this is. "dev" while you work locally; tools/build_site.py
 * replaces it in the published copy with "<version>-<git commit>".
 * main.js only turns on offline mode (the service worker) for real builds,
 * so development never gets stuck on cached files.
 */

export const BUILD = "dev";
