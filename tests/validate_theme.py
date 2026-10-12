#!/usr/bin/env python3
"""Validate theme assets and exercise side effects in an isolated repository HOME."""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import tomllib
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT
CLI = ROOT / 'bin/omarchi-grokbot'
EXPECTED = '''colors.toml palette.json colors.md alacritty.toml ghostty.conf kitty.conf
foot.ini hyprland.conf hyprlock.conf waybar.css walker.css mako.ini swayosd.css btop.theme
neovim.lua icons.theme chromium.theme mark.svg mark.png preview.svg preview.png grokbot/hyprland/scratchpad.conf
grokbot/waybar/config-snippet.jsonc grokbot/waybar/style-snippet.css
grokbot/waybar/grokbot-status.sh grokbot/waybar/grokbot-open.sh
grokbot/waybar/grokbot-screenshot.sh grokbot/walker/grokbot.desktop
grokbot/mako/rules.ini'''.split()
for name in EXPECTED:
    path = THEME / name
    assert path.is_file() and path.stat().st_size, f'Missing/empty: {name}'
for path in THEME.rglob('*'):
    if path.suffix == '.toml':
        tomllib.loads(path.read_text())
    elif path.suffix in ('.json', '.jsonc'):
        # Shipped JSONC deliberately uses the strict JSON subset.
        json.loads(path.read_text())
    elif path.suffix in ('.css', '.conf', '.ini', '.theme', '.lua'):
        assert path.read_text().strip(), path
palette = json.loads((THEME / 'palette.json').read_text())
assert palette == tomllib.loads((THEME / 'colors.toml').read_text())
assert palette['accent'] == '#4fd1ff'
assert palette['background'] == '#0a0a0b'
for key, value in palette.items():
    if key != 'mode':
        assert len(value) == 7 and value.startswith('#')
        red, green, blue = (int(value[i:i+2], 16) for i in (1, 3, 5))
        assert value == '#4fd1ff' or max(red, green, blue) - min(red, green, blue) <= 20, value


def check_png(path, dimensions=(3840, 2160)):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    pos, chunks, compressed = 8, [], bytearray()
    while pos < len(data):
        size = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        payload = data[pos+8:pos+8+size]
        crc = struct.unpack('>I', data[pos+8+size:pos+12+size])[0]
        assert zlib.crc32(kind + payload) == crc, path
        chunks.append(kind)
        if kind == b'IHDR':
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            assert (width, height) == dimensions, path
            assert depth == 8 and color in (2, 6) and interlace == 0
        if kind == b'IDAT':
            compressed.extend(payload)
        pos += 12 + size
    assert chunks[0] == b'IHDR' and chunks[-1] == b'IEND' and pos == len(data)
    channels = 3 if color == 2 else 4
    assert len(zlib.decompress(compressed)) == height * (1 + width * channels)


check_png(THEME / 'mark.png', (1024, 1024))
check_png(THEME / 'preview.png', (1920, 1080))
ET.parse(THEME / 'preview.svg')

badge = ET.parse(THEME / 'mark.svg').getroot()
assert badge.tag == '{http://www.w3.org/2000/svg}svg'
walls = sorted((THEME / 'backgrounds').glob('*.jpg'))
assert len(walls) >= 4, 'need at least 4 wallpapers'
for w in walls:
    data = w.read_bytes()
    assert data[:3] == b'\xff\xd8\xff', f'not a JPEG: {w}'
print(f'PASS: expected files, palette, TOML/JSON, badge, and {len(walls)} wallpapers')


def snapshot(home):
    return {str(p.relative_to(home)): (p.read_bytes() if p.is_file() else None)
            for p in home.rglob('*')}


with tempfile.TemporaryDirectory(prefix='.grokbot-test-', dir=ROOT / 'tests') as temp:
    fixture = Path(temp)
    home = fixture / 'home'
    home.mkdir()
    (home / 'keep.txt').write_text('untouched')
    env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'))

    def run(args, environment=None, check=True):
        result = subprocess.run(args, env=environment or env, text=True, capture_output=True, timeout=15)
        if check:
            assert result.returncode == 0, result.stderr + result.stdout
        return result

    before = snapshot(home)
    for action in ('install', 'uninstall'):
        result = run(['bash', str(CLI), action])
        assert 'Dry-run' in result.stdout
        assert snapshot(home) == before, f'{action} dry-run mutated HOME'
    assert 'omarchy-theme-set grokbot' in run(['bash', str(CLI), 'install']).stdout
    target = home / '.config/omarchy/themes/grokbot'
    run(['bash', str(CLI), 'install', '--yes'])
    expected = {k: v for k, v in snapshot(THEME).items()
                if not k.split('/')[0].startswith('.')}
    # The active test fixture belongs to the checkout, not the delivered theme.
    expected = {k: v for k, v in expected.items()
                if not k.startswith('tests/.grokbot-test-')}
    assert snapshot(target) == expected
    assert not (target / '.git').exists()
    installed = snapshot(home)
    for action in ('install', 'uninstall'):
        run(['bash', str(CLI), action])
        assert snapshot(home) == installed
    assert run(['bash', str(CLI), 'install', '--yes'], check=False).returncode != 0
    assert snapshot(home) == installed
    run(['bash', str(CLI), 'uninstall', '--yes'])
    assert not target.exists() and (home / 'keep.txt').read_text() == 'untouched'
    for args in [['install', '--bogus'], ['bogus']]:
        assert run(['bash', str(CLI), *args], check=False).returncode != 0
    # A redirected target must never be removed.
    other = fixture / 'other'; other.mkdir(); (other / 'keep').write_text('keep')
    target.symlink_to(other, target_is_directory=True)
    assert run(['bash', str(CLI), 'uninstall', '--yes'], check=False).returncode != 0
    assert (other / 'keep').read_text() == 'keep'
    target.unlink()
    print('PASS: dry-runs preserve HOME, install copies exactly, overwrite/symlink refusal, uninstall containment')

    # Controlled PATH ensures tests cannot launch a real app/browser or capture a desktop.
    commands = fixture / 'bin'; commands.mkdir()
    bash = shutil.which('bash')
    fake_env = dict(env, PATH=str(commands), LOG=str(fixture / 'calls'))
    log = fixture / 'calls'

    def stub(name, body):
        path = commands / name
        path.write_text('#!' + bash + '\nset -euo pipefail\n' + body + '\n')
        path.chmod(0o755)

    scripts = THEME / 'grokbot/waybar'
    def helper(name):
        return run([bash, str(scripts / ('grokbot-' + name + '.sh'))], fake_env)
    assert json.loads(helper('status').stdout)['class'] == 'standby'
    helper('open'); helper('screenshot')  # All tools absent.
    stub('xdg-open', 'printf "%s\\n" "$*" >> "$LOG"')
    helper('open'); assert log.read_text().strip() == 'https://grok.com/'
    log.unlink()
    stub('grokbot', 'printf "app\\n" >> "$LOG"')
    assert json.loads(helper('status').stdout)['class'] == 'ready'
    helper('open'); assert log.read_text().strip() == 'app'
    log.unlink()
    stub('slurp', 'exit 1')
    stub('grim', 'printf "grim:%s\\n" "$*" >> "$LOG"; printf "fake-png"')
    stub('wl-copy', 'printf "copy:%s\\n" "$*" >> "$LOG"; read -r data || true; printf "%s\\n" "$data" >> "$LOG"')
    helper('screenshot'); assert not log.exists(), 'Cancelled screenshot must not capture'
    stub('slurp', 'printf "10,20 30x40\\n"')
    helper('screenshot')
    content = log.read_text()
    assert 'grim:-g 10,20 30x40 -' in content and 'copy:--type image/png' in content and 'fake-png' in content
    print('PASS: stateless JSON, browser/app fallback, missing tools, screenshot cancel and clipboard pipeline')

    # CLI needs its basic filesystem utilities on the controlled PATH.
    for name in ('dirname', 'bash', 'python3'):
        (commands / name).symlink_to(shutil.which(name))
    stub('hyprctl', "printf '%s\\n' '[{\"class\":\"org.example.Bot\",\"title\":\"Grok Bot\"}]'")
    report = run([bash, str(CLI), 'doctor'], fake_env)
    assert 'Detected candidate app class: org.example.Bot' in report.stdout
    stub('hyprctl', 'exit 1')
    assert 'No live Hyprland' in run([bash, str(CLI), 'doctor'], fake_env).stdout
    print('PASS: doctor detects runtime app class and handles missing session')
print('All theme checks passed.')
