#!/usr/bin/env python3
"""Draw original SVG artwork and render with rsvg-convert."""
from pathlib import Path
import subprocess
import math
import random

ROOT = Path(__file__).resolve().parents[1]
T = ROOT
BADGE = '''<g fill="none" stroke="#87919a" stroke-width="2">
<path d="M160 8 292 84 292 236 160 312 28 236 28 84Z"/>
<path d="M160 28 274 94 274 226 160 292 46 226 46 94Z"/>
<circle cx="160" cy="145" r="65"/><ellipse cx="160" cy="145" rx="100" ry="24" transform="rotate(-32 160 145)"/>
<path stroke="#4fd1ff" d="M160 70V220M85 145H235"/>
<path d="M145 130 160 116 175 130 175 160 160 174 145 160Z"/>
</g><text x="160" y="250" text-anchor="middle" font-family="monospace" font-size="19" fill="#ffffff">OMARCHI-GROKBOT</text>'''
def svg(body, width=3840, height=2160):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{body}</svg>\n'
(T/'mark.svg').write_text(svg(BADGE,320,320))
rng = random.Random(71024)
stars = ''.join(f'<circle cx="{rng.randrange(3840)}" cy="{rng.randrange(2160)}" r="{rng.choice([0.8,1,1.4,2])}" fill="#ffffff" opacity="{rng.uniform(.15,.65):.2f}"/>' for _ in range(620))
base = '<rect width="3840" height="2160" fill="#000000"/>'
footer = f'<g transform="translate(3390 1690) scale(.9)">{BADGE}</g><g fill="#87919a" font-family="monospace" font-size="22"><text x="160" y="1960">OMARCHI-GROKBOT / MISSION SYSTEMS</text><text x="160" y="2000">COMMUNITY FLIGHT DECK · 3840 / 2160</text></g>'
void = stars + '<circle cx="1920" cy="1050" r="560" fill="none" stroke="#87919a" stroke-opacity=".15"/><path d="M1840 1050H2000M1920 970V1130" stroke="#4fd1ff" stroke-width="2"/><text x="160" y="200" fill="#e6e6e6" font-family="monospace" font-size="32">01 / VOID   •   DEEP FIELD</text>'
orbit = stars + '<defs><radialGradient id="limb"><stop stop-color="#000000"/><stop offset=".95" stop-color="#0a0a0b"/><stop offset="1" stop-color="#87919a"/></radialGradient></defs><circle cx="2650" cy="1900" r="1280" fill="url(#limb)"/>'
orbit += ''.join(f'<ellipse cx="2500" cy="1550" rx="{r}" ry="{r*.32}" transform="rotate(-24 2500 1550)" fill="none" stroke="{c}" stroke-width="2" opacity=".6"/>' for r,c in [(1100,'#87919a'),(1400,'#e6e6e6'),(1680,'#4fd1ff')])
orbit += '<text x="160" y="200" fill="#e6e6e6" font-family="monospace" font-size="32">02 / ORBIT   •   LIMB OBSERVATION</text>'
signal = '<g stroke="#87919a" opacity=".2">' + ''.join(f'<path d="M160 {y}H3180"/>' for y in range(500,1601,100)) + '</g>'
for idx in range(3):
    y=650+idx*360
    points=' '.join(f'{x},{y + (math.sin(x/95)*math.sin(x/430)*70 if idx!=1 else math.sin(x/38)*55)*math.exp(-((x-1920)/950)**2):.1f}' for x in range(160,3181,8))
    signal+=f'<polyline points="{points}" fill="none" stroke="{["#e6e6e6","#4fd1ff","#87919a"][idx]}" stroke-width="2"/><text x="160" y="{y-100}" fill="#87919a" font-family="monospace" font-size="24">CHANNEL 0{idx+1} / PASSIVE TELEMETRY</text>'
signal += '<text x="160" y="200" fill="#e6e6e6" font-family="monospace" font-size="32">03 / SIGNAL   •   RECEIVER ARRAY</text>'
grid='<g fill="none" stroke="#87919a" opacity=".15">'+''.join(f'<path d="M{x} 0V2160"/>' for x in range(0,3841,80))+''.join(f'<path d="M0 {y}H3840"/>' for y in range(0,2161,80))+'</g>'
grid+='<g fill="none" stroke="#e6e6e6" stroke-width="2"><rect x="1400" y="480" width="1040" height="1120"/><circle cx="1920" cy="1040" r="360"/><circle cx="1920" cy="1040" r="260"/><path d="M1920 320V1760M1200 1040H2640M1400 480 2440 1600M2440 480 1400 1600" stroke-opacity=".35"/><rect x="1780" y="900" width="280" height="280" stroke="#4fd1ff"/></g><g fill="#87919a" font-family="monospace" font-size="24"><text x="2490" y="1040">PAD 04 / ALIGNMENT</text><text x="160" y="200" fill="#e6e6e6" font-size="32">04 / GRID   •   LAUNCH GEOMETRY</text></g>'
for name, body in [('1-void',void),('2-orbit',orbit),('3-signal',signal),('4-grid',grid)]:
    (T/'backgrounds'/f'{name}.svg').write_text(svg(base+body+footer))

def render(source, target):
    subprocess.run(['rsvg-convert', '-o', str(target), str(source)], check=True)

subprocess.run(['rsvg-convert', '-w', '1024', '-h', '1024',
                '-o', str(T / 'mark.png'), str(T / 'mark.svg')], check=True)
subprocess.run(['rsvg-convert', '-w', '1920', '-h', '1080',
                '-o', str(T / 'preview.png'), str(T / 'preview.svg')], check=True)
for source in sorted((T/'backgrounds').glob('*.svg')):
    render(source,source.with_suffix('.png'))
    print(f'Rendered {source.name}')
