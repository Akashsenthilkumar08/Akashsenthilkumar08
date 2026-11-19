#!/usr/bin/env python3
"""Generate self-contained animated SVG cards for Akash's GitHub profile."""
import json, os, urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"cards"
LOGIN=os.getenv("GITHUB_REPOSITORY_OWNER","Akashsenthilkumar08")
TOKEN=os.getenv("GITHUB_TOKEN","")
STATIC=os.getenv("STATIC","0")=="1"
BLUE="#2563EB"; RED="#D65345"; GOLD="#D9A441"; PAPER="#F6F2E9"; INK="#182235"

def shell(w,h,body):
    css="" if STATIC else """<style>
    .reveal{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) forwards}
    .shine{animation:shine 5s ease-in-out 2s infinite}
    .pulse{animation:pulse 3s ease-in-out infinite}
    @keyframes rise{to{opacity:1;transform:translateY(0)}}
    @keyframes shine{0%,72%,100%{transform:translateX(-180px)}88%{transform:translateX(760px)}}
    @keyframes pulse{0%,100%{opacity:.4}50%{opacity:1}}
    @media(prefers-reduced-motion:reduce){.reveal,.shine,.pulse{animation:none!important;opacity:1!important;transform:none!important}}
    </style>"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="paper"><stop stop-color="#fffdf8"/><stop offset="1" stop-color="{PAPER}"/></linearGradient><clipPath id="clip"><rect width="{w}" height="{h}" rx="22"/></clipPath></defs>{css}<g clip-path="url(#clip)">{body}</g></svg>'

def get_calendar():
    if not TOKEN: return None
    end=date.today(); start=end-timedelta(days=364)
    q='query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
    data=json.dumps({"query":q,"variables":{"login":LOGIN,"from":start.isoformat()+"T00:00:00Z","to":end.isoformat()+"T23:59:59Z"}}).encode()
    req=urllib.request.Request("https://api.github.com/graphql",data=data,headers={"Authorization":"Bearer "+TOKEN,"Content-Type":"application/json","User-Agent":"profile-svg-cards"})
    with urllib.request.urlopen(req,timeout=30) as r: result=json.load(r)
    return result.get("data",{}).get("user",{}).get("contributionsCollection",{}).get("contributionCalendar")

def render_hero():
    b=f'''<rect width="1100" height="300" fill="url(#paper)"/><circle cx="1000" cy="10" r="190" fill="{BLUE}" opacity=".08"/>
    <text x="64" y="60" fill="{BLUE}" font-family="Arial" font-size="13" letter-spacing="4" font-weight="bold">AKASH S / DEVELOPER PROFILE</text>
    <text class="reveal" x="62" y="157" fill="{INK}" font-family="Georgia" font-size="76">Building things</text>
    <text class="reveal" x="62" y="235" fill="{BLUE}" font-family="Georgia" font-size="76" font-style="italic" style="animation-delay:.2s">that make a difference.</text>
    <text x="68" y="276" fill="#596579" font-family="Arial" font-size="16">Computer Science student · Full-stack developer · AI enthusiast</text>
    <rect class="shine" x="420" y="90" width="120" height="190" fill="white" opacity=".25" transform="skewX(-22)"/><circle class="pulse" cx="1030" cy="252" r="7" fill="{RED}"/>'''
    return shell(1100,300,b)

def render_activity(cal):
    days=[d for w in (cal or {}).get("weeks",[]) for d in w.get("contributionDays",[])]
    total=(cal or {}).get("totalContributions",0)
    monthly={}
    for d in days: monthly[d["date"][:7]]=monthly.get(d["date"][:7],0)+d.get("contributionCount",0)
    keys=sorted(monthly)[-12:]; vals=[monthly[k] for k in keys]; maxv=max(vals or [1]) or 1
    streak=0
    for d in reversed(days):
        if d.get("contributionCount",0): streak+=1
        elif streak: break
    busiest=max(days,key=lambda d:d.get("contributionCount",0),default={})
    heat=[]
    for wi,w in enumerate((cal or {}).get("weeks",[])[-52:]):
        for di,d in enumerate(w.get("contributionDays",[])):
            n=d.get("contributionCount",0); c="#E6E2D9" if n==0 else "#BFDBFE" if n<3 else "#60A5FA" if n<6 else BLUE
            heat.append(f'<rect x="{65+wi*18}" y="{205+di*15}" width="12" height="11" rx="2" fill="{c}"/>')
    bars=[]
    for i,(k,v) in enumerate(zip(keys,vals)):
        x=65+i*83; h=95*v/maxv
        bars.append(f'<rect x="{x}" y="{408-h:.1f}" width="44" height="{h:.1f}" rx="5" fill="{BLUE}" opacity=".82"/><text x="{x+22}" y="430" text-anchor="middle" font-size="10" fill="#64748B">{escape(k[5:])}</text>')
    b=f'''<rect width="1100" height="470" fill="url(#paper)"/><text x="58" y="54" fill="{INK}" font-family="Georgia" font-size="32">A year in motion.</text>
    <text x="60" y="82" fill="#64748B" font-family="Arial" font-size="12" letter-spacing="2">GITHUB CONTRIBUTION ACTIVITY · LAST 12 MONTHS</text>
    <text x="60" y="145" fill="{BLUE}" font-family="Georgia" font-size="48">{total:,}</text><text x="62" y="168" fill="#64748B" font-family="Arial" font-size="12">TOTAL CONTRIBUTIONS</text>
    <text x="340" y="145" fill="{INK}" font-family="Georgia" font-size="36">{streak}</text><text x="340" y="168" fill="#64748B" font-family="Arial" font-size="12">CURRENT STREAK*</text>
    <text x="620" y="145" fill="{INK}" font-family="Georgia" font-size="20">{escape(busiest.get("date","—"))}</text><text x="620" y="168" fill="#64748B" font-family="Arial" font-size="12">BUSIEST DAY</text>
    <text x="60" y="194" fill="#64748B" font-family="Arial" font-size="10">LESS</text>{''.join(heat)}<text x="1000" y="194" fill="#64748B" font-family="Arial" font-size="10">MORE</text>
    <path d="M60 370H1050" stroke="#D9D5CC"/>{''.join(bars)}
    <text x="60" y="455" fill="#94A3B8" font-family="Arial" font-size="10">*Consecutive-day estimate from the fetched contribution calendar. No token = zero-data fallback.</text>'''
    return shell(1100,470,b)

def tile(title,kicker,copy,color,mark):
    b=f'''<rect width="340" height="220" fill="url(#paper)"/><rect width="340" height="8" fill="{color}"/>
    <text x="26" y="42" fill="{color}" font-family="Arial" font-size="11" font-weight="bold" letter-spacing="3">{kicker}</text>
    <text class="reveal" x="24" y="105" fill="{INK}" font-family="Georgia" font-size="42">{title}</text>
    <text x="27" y="143" fill="#64748B" font-family="Arial" font-size="13">{copy}</text>
    <text x="27" y="193" fill="{color}" font-family="Georgia" font-size="26">{mark}</text>
    <path d="M270 180l30-30m-15 0h15v15" stroke="{color}" stroke-width="2" fill="none"/>'''
    return shell(340,220,b)

def main():
    OUT.mkdir(exist_ok=True)
    try: cal=get_calendar()
    except Exception as e: print("Contribution API unavailable:",e); cal=None
    cards={"hero.svg":render_hero(),"activity.svg":render_activity(cal),
           "build.svg":tile("Build","01 / ENGINEER","Turn ideas into products",BLUE,"↗"),
           "create.svg":tile("Create","02 / EXPERIMENT","Design, prototype, explore",RED,"✳"),
           "learn.svg":tile("Learn","03 / GROW","Stay curious. Keep shipping.",GOLD,"＋")}
    for name,content in cards.items(): (OUT/name).write_text(content,encoding="utf-8")
    print("Rendered",len(cards),"SVG cards in",OUT)

if __name__=="__main__": main()
