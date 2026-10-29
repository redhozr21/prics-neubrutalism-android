"""Applies Muriel's Riff->Muriel rename to a checkout. Used to port upstream Riff changes:
rename an old and a new upstream snapshot the same way, diff them, apply that diff to Muriel."""
import os, re, sys

FILES = ['app.js', 'index.html', 'welcome.html', 'styles.css', 'main.js', 'preload.js', 'platform.js', 'launcher.js',
         'cli.js', 'tools.js', 'audio-engine.js', 'server.js', 'themes.js', 'discord-rpc.js', 'updater.js',
         'audio-output.js', 'library-tools.js', 'logger.js', 'lyrics-rtl.js', 'm3shapes.js', 'plugins.js', 'search-text.js',
         'track-sort.js']

def rename(s):
    s = s.replace("writeString(0, 'RIFF')", "writeString(0, '\x00WAV\x00')").replace('rIfFileNotExist', '\x00RIFNE\x00')
    s = s.replace('RiffAudioEngine', 'MurielAudioEngine')
    s = re.sub(r'\bRIFF_', 'MURIEL_', s)
    s = re.sub(r'\briff_', 'muriel_', s)
    s = re.sub(r'\briff-', 'muriel-', s)
    s = re.sub(r'\briff:', 'muriel:', s)
    s = s.replace('.rifftutorial', '.murieltutorial').replace("'C:\\Riff\\\\", "'C:\\Muriel\\\\")
    s = s.replace('riff.desktop', 'muriel.desktop').replace('riff.png', 'muriel.png').replace('riffCustom', 'murielCustom')
    s = s.replace("defineTheme('riff'", "defineTheme('muriel'").replace("setTheme('riff')", "setTheme('muriel')")
    s = s.replace('Usage: riff lyrics', 'Usage: muriel lyrics')
    s = re.sub(r'\bRiff\b', 'Muriel', s)
    return s.replace('\x00WAV\x00', 'RIFF').replace('\x00RIFNE\x00', 'rIfFileNotExist')

root = sys.argv[1] if len(sys.argv) > 1 else '.'
for f in FILES:
    p = os.path.join(root, f)
    if os.path.exists(p):
        s = open(p, encoding='utf-8').read()
        n = rename(s)
        if n != s:
            open(p, 'w', encoding='utf-8', newline='').write(n)
