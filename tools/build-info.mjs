// Stamps a build with what the update notifier compares against: the commit, run number and time.
// Usage (CI): node tools/build-info.mjs <out file> [channel]
import { readFileSync, writeFileSync } from 'node:fs';

const pkgVersion = () => { try { return JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8')).version; } catch (e) { return ''; } };

export function buildInfo(channel = '') {
  return {
    sha: process.env.GITHUB_SHA || 'dev',
    version: pkgVersion(),
    run: Number(process.env.GITHUB_RUN_NUMBER) || 0,
    repo: process.env.GITHUB_REPOSITORY || 'redhozr21/prics-neubrutalism-android',
    builtAt: new Date().toISOString(),
    channel,
  };
}

export const buildInfoScript = (channel) => `window.MURIEL_BUILD = ${JSON.stringify(buildInfo(channel))};\n`;

if (process.argv[1] && process.argv[1].endsWith('build-info.mjs')) {
  const [out = 'build-info.js', channel = ''] = process.argv.slice(2);
  writeFileSync(out, buildInfoScript(channel));
  console.log(`${out}: ${buildInfoScript(channel).trim()}`);
}
