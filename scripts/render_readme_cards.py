#!/usr/bin/env python3
"""Generate the animated SVG cards used by Akash's GitHub profile README."""
import json, os, urllib.request, datetime, html
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"cards"
LOGIN=os.getenv("GITHUB_REPOSITORY_OWNER","Akashsenthilkumar08")
TOKEN=os.getenv("GITHUB_TOKEN","")
STATIC=os.getenv("STATIC","")=="1"
PAPER="#f3f3f1"; PAPER2="#e2e2de"; INK="#111111"; SOFT="#3a3a3c"; MUTED="#6e6e73"; RULE="#dcdcd7"
BLUE="#2f55ff"; RED="#ef3b2d"; YELLOW="#ffc81a"; W=880
CSS="""
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{to{opacity:1}} @keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes sheen{0%{transform:translateX(-240px) skewX(-20deg)}30%,100%{transform:translateX(520px) skewX(-20deg)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.pulse{animation:pulse 1.6s ease-in-out infinite}
.sh{animation:sheen 5s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){.r,.f,.g,.pulse,.sh{animation:none!important;opacity:1!important;transform:none!important}.sh{display:none}}
"""
def svg(name,w,h,body):
    css=CSS
    if STATIC: css += ".r,.f,.g,.pulse{animation:none!important;opacity:1!important;transform:none!important}.sh{display:none}"
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>{css}</style>{body}</svg>',encoding="utf-8")

def contributions():
    if not TOKEN: raise RuntimeError("GITHUB_TOKEN is not set")
    end=datetime.date.today(); start=end-datetime.timedelta(days=364)
    query='query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
    payload=json.dumps({"query":query,"variables":{"login":LOGIN,"from":start.isoformat()+"T00:00:00Z","to":end.isoformat()+"T23:59:59Z"}}).encode()
    req=urllib.request.Request("https://api.github.com/graphql",data=payload,headers={"Authorization":"Bearer "+TOKEN,"Content-Type":"application/json","User-Agent":"akash-profile-art"})
    with urllib.request.urlopen(req,timeout=30) as r: data=json.load(r)
    if data.get("errors"): raise RuntimeError(str(data["errors"]))
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def hero():
    # A terminal-style typographic portrait, custom-drawn for this profile.
    rows=["        .:::::.        ","      .:::::::::.      ","     :::  :::  :::     ","     :::  :::  :::     ","      ':::::::::'      ","        .:::::.        ","      .:::::::::.      ","    .::  :::::  ::.    ","   :::   :::::   :::   ","   :::   :::::   :::   ","    '::..:::::..::'    ","       /:::::::\       ","      /:::::::::\      ","     /:::::::::::\     ","    /_____________\    "]
    portrait="".join(f'<text x="0" y="{24+i*17}" fill="{BLUE}" font-family="monospace" font-size="12" xml:space="preserve">{html.escape(row)}</text>' for i,row in enumerate(rows))
    body=f'''<rect width="{W}" height="420" rx="14" fill="{PAPER}"/>
    <rect class="pulse" x="48" y="49" width="8" height="8" rx="2" fill="{BLUE}"/>
    <text class="f" x="66" y="57" font-family="monospace" font-size="12" letter-spacing="1" fill="{MUTED}">COMPUTER SCIENCE STUDENT · DEVELOPER</text>
    <text class="r" x="44" y="188" font-family="Georgia,serif" font-size="116" letter-spacing="-3" fill="{INK}">Akash</text>
    <text class="r" x="44" y="288" font-family="Georgia,serif" font-style="italic" font-size="112" letter-spacing="-3" fill="url(#shine)">S</text>
    <defs><linearGradient id="shine"><stop stop-color="{INK}"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="{INK}"/></linearGradient></defs>
    <text class="r" x="48" y="340" font-family="Arial,sans-serif" font-size="18" fill="{SOFT}">I build full-stack products, explore AI,</text>
    <text class="r" x="48" y="367" font-family="Arial,sans-serif" font-size="18" fill="{SOFT}">and turn curious ideas into useful tools.</text>
    <text class="f" x="48" y="399" font-family="monospace" font-size="13" fill="{INK}">github.com/{LOGIN}</text>
    <g transform="translate(560 92)">{portrait}</g>'''
    svg("hero.svg",W,420,body)

def heatmap(cal):
    days=[d for week in cal["weeks"] for d in week["contributionDays"]]
    cell=12; step=15; x0=42; y0=112; cells=[]; months=[]; seen=set()
    for i,d in enumerate(days):
        col,row=divmod(i,7); n=d["contributionCount"]
        color=PAPER2 if n==0 else "#c8d3ff" if n<=5 else "#94a8ff" if n<=15 else "#6280ff" if n<=30 else BLUE
        delay=0.5+col*.012+row*.01
        cells.append(f'<rect class="r" style="animation-delay:{delay:.2f}s" x="{x0+col*step}" y="{y0+row*step}" width="{cell}" height="{cell}" rx="3" fill="{color}"><title>{d["date"]}: {n} contributions</title></rect>')
        dt=datetime.date.fromisoformat(d["date"])
        if dt.day<=7 and (dt.year,dt.month) not in seen and row==0:
            seen.add((dt.year,dt.month)); months.append((col,dt.strftime("%b")))
    cols=(len(days)+6)//7; right=x0+cols*step
    labels="".join(f'<text x="{x0+c*step}" y="239" font-family="monospace" font-size="11" fill="{MUTED}">{m}</text>' for c,m in months if c<cols-12)
    legend="".join(f'<rect x="{right-105+i*15}" y="228" width="11" height="11" rx="2" fill="{c}"/>' for i,c in enumerate([PAPER2,"#c8d3ff","#94a8ff","#6280ff",BLUE]))
    body=f'''<rect width="{W}" height="260" rx="14" fill="{PAPER}"/><text class="r" x="42" y="58" font-family="Georgia,serif" font-size="34" fill="{INK}">Every day, <tspan font-style="italic" fill="{BLUE}">in blue.</tspan></text>
    <text class="f" x="838" y="57" text-anchor="end" font-family="monospace" font-size="12" letter-spacing="1" fill="{MUTED}">REFRESHED DAILY</text>{''.join(cells)}{labels}{legend}
    <text x="{right-115}" y="239" text-anchor="end" font-family="monospace" font-size="11" fill="{MUTED}">less</text><text x="{right-20}" y="239" font-family="monospace" font-size="11" fill="{MUTED}">more</text>'''
    svg("heatmap.svg",W,260,body)

def activity(cal):
    days=[d for week in cal["weeks"] for d in week["contributionDays"]]
    monthly={}
    for d in days:
        key=d["date"][:7]; monthly[key]=monthly.get(key,0)+d["contributionCount"]
    keys=sorted(monthly)[-12:]; vals=[monthly[k] for k in keys]; peak=max(vals or [1]) or 1
    best=max(monthly.items(),key=lambda x:x[1]) if monthly else ("—",0)
    streak=0
    for d in reversed(days):
        if d["contributionCount"]: streak+=1
        elif streak: break
    total=cal["totalContributions"]; active=sum(1 for d in days if d["contributionCount"])
    x0=42; base=282; bw=38; gap=8; bars=[]
    for i,(k,v) in enumerate(zip(keys,vals)):
        h=max(3,round(v/peak*126)); x=x0+i*(bw+gap)
        bars.append(f'<rect class="g" style="animation-delay:{1.2+i*.07:.2f}s" x="{x}" y="{base-h}" width="{bw}" height="{h}" rx="4" fill="{BLUE if v==best[1] else "#bfc0bc"}"/><text x="{x+bw/2}" y="306" text-anchor="middle" font-family="monospace" font-size="10" fill="{MUTED}">{k[5:]}</text>')
    body=f'''<rect width="{W}" height="340" rx="14" fill="{PAPER}"/><text class="f" x="42" y="48" font-family="monospace" font-size="12" letter-spacing="1" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
    <text class="r" x="40" y="108" font-family="Georgia,serif" font-size="48" fill="{INK}">{total:,} <tspan font-style="italic">contributions</tspan></text>{''.join(bars)}
    <path d="M625 72V300" stroke="{RULE}"/><text class="r" x="660" y="115" font-family="Georgia,serif" font-size="40" fill="{INK}">{streak} <tspan font-style="italic" font-size="24">days</tspan></text>
    <text x="660" y="140" font-family="Arial" font-size="13" fill="{MUTED}">current streak*</text><path d="M660 164H840" stroke="{RULE}"/>
    <text class="r" x="660" y="210" font-family="Georgia,serif" font-size="36" fill="{INK}">{active}</text><text x="660" y="234" font-family="Arial" font-size="13" fill="{MUTED}">active days</text>
    <text class="r" x="660" y="280" font-family="Georgia,serif" font-size="30" fill="{BLUE}">{best[1]:,}</text><text x="660" y="304" font-family="Arial" font-size="13" fill="{MUTED}">best month total</text>
    <text x="42" y="330" font-family="Arial" font-size="10" fill="{MUTED}">*Consecutive days calculated from the contribution calendar.</text>'''
    svg("activity.svg",W,340,body)

def tile(name,label,color,fg,number,word,blurb,delay):
    body=f'''<rect width="293.33" height="210" rx="14" fill="{color}"/>
    <text class="f" style="animation-delay:{delay}s" x="22" y="34" font-family="monospace" font-size="11" letter-spacing="1.5" fill="{fg}">{label}</text>
    <text class="r" style="animation-delay:{delay+.2}s" x="22" y="105" font-family="Georgia,serif" font-size="48" fill="{fg}">{number} <tspan font-style="italic" font-size="27">{word}</tspan></text>
    <text class="r" style="animation-delay:{delay+.45}s" x="22" y="151" font-family="Arial" font-size="13" fill="{fg}">{html.escape(blurb)}</text>
    <text x="260" y="36" font-family="monospace" font-size="16" fill="{fg}">↗</text>'''
    svg(name+".svg",293,210,body)

def repo_card(name,title,desc,lang,color):
    body=f'''<rect width="293" height="174" rx="14" fill="{PAPER}"/><rect x="22" y="28" width="8" height="8" rx="2" fill="{color}"/>
    <text class="r" x="42" y="38" font-family="Arial" font-size="17" font-weight="600" fill="{INK}">{html.escape(title)}</text>
    <text x="22" y="76" font-family="Arial" font-size="13" fill="{SOFT}">{html.escape(desc[:42])}</text>
    <text x="22" y="97" font-family="Arial" font-size="13" fill="{SOFT}">{html.escape(desc[42:84])}</text>
    <text x="22" y="150" font-family="monospace" font-size="11" fill="{MUTED}">{html.escape(lang)}</text>'''
    svg("repo-"+name+".svg",293,174,body)

def main():
    try: cal=contributions()
    except Exception as e:
        print("Contribution fetch failed; retaining placeholder stats:",e)
        cal={"totalContributions":0,"weeks":[]}
    hero()
    if cal["weeks"]:
        heatmap(cal); activity(cal)
    else:
        svg("heatmap.svg",W,260,f'<rect width="{W}" height="260" rx="14" fill="{PAPER}"/><text x="42" y="58" font-family="Georgia" font-size="34" fill="{INK}">Every day, in blue.</text><text x="42" y="130" font-family="Arial" font-size="16" fill="{MUTED}">Contribution graph will populate after the first successful workflow run.</text>')
        svg("activity.svg",W,340,f'<rect width="{W}" height="340" rx="14" fill="{PAPER}"/><text x="42" y="58" font-family="Georgia" font-size="34" fill="{INK}">A year in motion.</text><text x="42" y="120" font-family="Arial" font-size="16" fill="{MUTED}">Live contribution stats will populate after the first workflow run.</text>')
    tile("build","BUILD",BLUE,"#ffffff","01","/ ENGINEER","Build useful products, tools and experiences.",.8)
    tile("brand","CREATE",RED,"#ffffff","02","/ EXPERIMENT","Shape ideas through design and creative code.",1.0)
    tile("learn","LEARN",YELLOW,INK,"03","/ GROW","Stay curious. Keep learning by shipping.",1.2)
    repo_card("rescuevoice","RescueVoice","Real-time interruption-aware voice agent with multi-model speech recognition","TypeScript",BLUE)
    repo_card("prompt-wars","SYNAPSE 2026","3D event platform with skill matchmaking, judging and live venue tools","React / Three.js",RED)
    repo_card("aidetect","AI Detect","AI and ML-powered image authenticity and manipulation detection","AI / ML",YELLOW)
    title_body=f'<text class="r" x="2" y="46" font-family="Georgia,serif" font-size="34" fill="{INK}">What I\'m <tspan font-style="italic">building</tspan></text>'
    svg("title-coding-light.svg",W,64,title_body)
    print("Rendered profile SVG cards.")
if __name__=="__main__": main()
