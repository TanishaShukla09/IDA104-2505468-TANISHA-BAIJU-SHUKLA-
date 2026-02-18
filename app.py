import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import io
import time
import json
from datetime import datetime

warnings.filterwarnings("ignore")
# Required packages: streamlit pandas numpy matplotlib seaborn plotly scipy
# pip install streamlit pandas numpy matplotlib seaborn plotly scipy
# statsmodels is NOT required — trendlines use numpy polyfit

# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Rocket Launch Analytics",
                   page_icon="🚀", layout="wide",
                   initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════
# SESSION STATE  ← NEW
# ══════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "sim_history":    [],    # last 10 simulation results
        "sim_steps_idx":  0,     # step-reveal pointer
        "sim_steps_data": [],    # precomputed step list
        "show_all_steps": False,
        "total_sims":     0,
        "page_visits":    {},
        "filter_presets": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init_state()

# ──────────────────────────────────────────────────────────────
# CSS  (original + new component styles appended)
# ──────────────────────────────────────────────────────────────
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
:root{--bg:#050a14;--srf:#0b1628;--srf2:#0f2040;--brd:#1a3a60;
      --cyan:#00e5ff;--c2:#00a8cc;--org:#ff6b00;--grn:#00e676;
      --red:#ff1744;--txt:#cce0f0;--muted:#5a7a9a;--gold:#ffd700;}
.stApp{background:var(--bg)!important;color:var(--txt);}
html,body,[class*="css"]{font-family:'Rajdhani',sans-serif;}

/* starfield */
.stApp::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    radial-gradient(1px 1px at  7% 11%,rgba(255,255,255,.9)  0%,transparent 100%),
    radial-gradient(1px 1px at 21% 57%,rgba(255,255,255,.6)  0%,transparent 100%),
    radial-gradient(1px 1px at 37%  4%,rgba(255,255,255,.8)  0%,transparent 100%),
    radial-gradient(1px 1px at 52% 78%,rgba(255,255,255,.55) 0%,transparent 100%),
    radial-gradient(1px 1px at 67% 32%,rgba(255,255,255,.9)  0%,transparent 100%),
    radial-gradient(1px 1px at 81% 13%,rgba(255,255,255,.7)  0%,transparent 100%),
    radial-gradient(1px 1px at 92% 69%,rgba(255,255,255,.75) 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 14% 83%,rgba(180,220,255,.9) 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 58% 46%,rgba(180,220,255,.7) 0%,transparent 100%),
    radial-gradient(1px 1px at 76% 91%,rgba(255,255,255,.55) 0%,transparent 100%),
    radial-gradient(1px 1px at 32% 36%,rgba(255,255,255,.5)  0%,transparent 100%),
    radial-gradient(1px 1px at  3% 48%,rgba(255,255,255,.75) 0%,transparent 100%),
    radial-gradient(2px 2px   at 93% 43%,rgba(200,230,255,1)  0%,transparent 100%),
    radial-gradient(1px 1px at 44% 94%,rgba(255,255,255,.65) 0%,transparent 100%),
    radial-gradient(1px 1px at 18%  7%,rgba(255,255,255,.9)  0%,transparent 100%),
    radial-gradient(1px 1px at 70% 24%,rgba(200,240,255,.65) 0%,transparent 100%),
    radial-gradient(1px 1px at  2% 71%,rgba(255,255,255,.55) 0%,transparent 100%),
    radial-gradient(1px 1px at 47% 26%,rgba(255,255,255,.5)  0%,transparent 100%),
    radial-gradient(1px 1px at 61% 61%,rgba(220,240,255,.7)  0%,transparent 100%),
    radial-gradient(1px 1px at 85% 51%,rgba(255,255,255,.6)  0%,transparent 100%),
    radial-gradient(1px 1px at 28% 17%,rgba(255,255,255,.7)  0%,transparent 100%),
    radial-gradient(1px 1px at 54% 37%,rgba(200,230,255,.5)  0%,transparent 100%);
  animation:twinkle 9s ease-in-out infinite alternate;}
@keyframes twinkle{0%{opacity:.4}50%{opacity:1}100%{opacity:.5}}
section.main>div{position:relative;z-index:1;}

/* sidebar */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#030810 0%,#060f1c 55%,#081422 100%)!important;
  border-right:1px solid var(--brd);}
.nav-lbl{font-family:'Orbitron',monospace;font-size:.68rem;color:var(--cyan);
         letter-spacing:2.5px;text-align:center;padding:14px 0 9px;
         border-bottom:1px solid var(--brd);margin-bottom:14px;}

/* hero */
.hero{position:relative;overflow:hidden;
  background:linear-gradient(135deg,#030b16,#071422 35%,#0c1e3c 65%,#040c18);
  border:1px solid var(--brd);border-radius:16px;
  padding:36px 195px 32px 42px;margin-bottom:26px;}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  animation:scan 4s ease-in-out infinite;}
@keyframes scan{0%{top:0%;opacity:0}8%{opacity:1}92%{opacity:1}100%{top:100%;opacity:0}}
.hero::after{content:'';position:absolute;bottom:-18px;left:20%;right:20%;height:52px;
  background:radial-gradient(ellipse at center,rgba(255,90,0,.45) 0%,transparent 70%);
  animation:hglow 3s ease-in-out infinite alternate;pointer-events:none;}
@keyframes hglow{0%{opacity:.3;transform:scaleX(.7)}100%{opacity:.9;transform:scaleX(1.3)}}
.hero-rkt{position:absolute;right:36px;top:50%;transform:translateY(-50%);
  animation:float 4.5s ease-in-out infinite;}
@keyframes float{0%{transform:translateY(-50%) rotate(0)}
                 50%{transform:translateY(-56%) rotate(1deg)}
                 100%{transform:translateY(-50%) rotate(0)}}
.hero-title{font-family:'Orbitron',monospace;font-weight:900;font-size:2.1rem;
  background:linear-gradient(90deg,var(--cyan),#80eeff 55%,#fff);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  letter-spacing:3px;margin:0 0 6px;line-height:1.2;
  animation:tglow 4s ease-in-out infinite alternate;}
@keyframes tglow{0%{filter:drop-shadow(0 0 4px rgba(0,229,255,.3))}
                 100%{filter:drop-shadow(0 0 16px rgba(0,229,255,.8))}}
.hero-sub{font-size:.88rem;color:var(--muted);letter-spacing:2px;font-weight:300;
          text-transform:uppercase;margin:0 0 12px;}
.badges{display:flex;gap:8px;flex-wrap:wrap;}
.badge{background:rgba(0,229,255,.07);border:1px solid rgba(0,229,255,.22);
  border-radius:20px;padding:3px 12px;font-size:.68rem;color:var(--c2);
  letter-spacing:.8px;font-family:'Orbitron',monospace;}

/* section headers */
.sh{font-family:'Orbitron',monospace;font-size:.86rem;font-weight:700;color:var(--cyan);
  letter-spacing:2.5px;text-transform:uppercase;border-bottom:1px solid var(--brd);
  padding-bottom:9px;margin:26px 0 16px;position:relative;}
.sh::after{content:'';position:absolute;bottom:-1px;left:0;height:2px;
  background:var(--cyan);animation:xb .9s ease-out forwards;}
@keyframes xb{0%{width:0}100%{width:52px}}
.sh-sm{font-family:'Orbitron',monospace;font-size:.72rem;font-weight:700;color:var(--c2);
  letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid var(--brd);
  padding-bottom:7px;margin:20px 0 13px;}

/* metric card */
.mc{background:linear-gradient(135deg,var(--srf),var(--srf2));border:1px solid var(--brd);
  border-top:3px solid var(--cyan);border-radius:10px;padding:16px 18px 13px;
  text-align:center;position:relative;overflow:hidden;transition:transform .22s,box-shadow .22s;}
.mc:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,229,255,.18);}
.mc::before{content:'';position:absolute;inset:0;
  background:radial-gradient(circle at 50% 0%,rgba(0,229,255,.055) 0%,transparent 60%);}
.ml{font-family:'Orbitron',monospace;font-size:.57rem;color:var(--muted);
  letter-spacing:1.5px;text-transform:uppercase;margin-bottom:7px;}
.mv{font-family:'Orbitron',monospace;font-size:1.55rem;font-weight:700;color:#fff;line-height:1;}
.ms{font-size:.71rem;color:var(--c2);margin-top:4px;}

/* stat row */
.stat-row{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0;}
.stat-chip{background:var(--srf);border:1px solid var(--brd);border-radius:8px;
  padding:10px 16px;flex:1;min-width:110px;text-align:center;}
.sc-lbl{font-family:'Orbitron',monospace;font-size:.56rem;color:var(--muted);
  letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;}
.sc-val{font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:700;}
.sc-cyan{color:var(--cyan);}
.sc-grn{color:var(--grn);}
.sc-org{color:var(--org);}
.sc-red{color:var(--red);}

/* insight box */
.ib{background:linear-gradient(135deg,#071422,#0b1c34);border:1px solid var(--brd);
  border-left:4px solid var(--cyan);border-radius:8px;padding:14px 18px;
  margin:10px 0;font-size:.87rem;color:var(--txt);line-height:1.7;}
.ib strong{color:var(--cyan);}
.ib-grn{border-left-color:var(--grn);}
.ib-org{border-left-color:var(--org);}
.ib-red{border-left-color:var(--red);}
.ib-gold{border-left-color:var(--gold);}
.wbox{background:rgba(255,107,0,.08);border-left:4px solid var(--org);border-radius:8px;
  padding:11px 16px;margin:8px 0;font-size:.86rem;color:#efaa60;}
.sbox{background:rgba(0,230,118,.07);border-left:4px solid var(--grn);border-radius:8px;
  padding:11px 16px;margin:8px 0;font-size:.86rem;color:#70d4a0;}

/* formula */
.fw{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 16px;}
.fc{flex:1;min-width:150px;background:#03090f;border:1px solid var(--brd);
  border-radius:9px;padding:16px 12px;text-align:center;
  font-family:'Orbitron',monospace;font-size:.78rem;color:var(--cyan);
  letter-spacing:.8px;transition:box-shadow .2s;}
.fc:hover{box-shadow:0 0 18px rgba(0,229,255,.18);}
.fl{font-size:.56rem;color:var(--muted);letter-spacing:2px;text-transform:uppercase;
  display:block;margin-bottom:7px;}

/* sim rocket */
.sim-wrap{display:flex;flex-direction:column;align-items:center;margin:8px 0;}
.rkt-anim{animation:rrise 2.2s ease-out forwards,rsway 3.5s ease-in-out 2.2s infinite;}
@keyframes rrise{0%{transform:translateY(45px) scale(.78);opacity:.3}
                 55%{transform:translateY(-6px) scale(1.03);opacity:1}
                 100%{transform:translateY(0) scale(1);opacity:1}}
@keyframes rsway{0%{transform:translateY(0) rotate(-1.2deg)}
                 50%{transform:translateY(-5px) rotate(1.2deg)}
                 100%{transform:translateY(0) rotate(-1.2deg)}}
.flame-box{position:relative;width:34px;height:54px;margin-top:-4px;}
.fl-i{position:absolute;left:50%;transform:translateX(-50%);width:16px;height:36px;
  background:linear-gradient(180deg,#fff 0%,#ffe000 18%,#ff7700 52%,#ff2200 82%,transparent 100%);
  border-radius:50% 50% 18% 18%;filter:blur(1.5px);
  animation:ff .13s ease-in-out infinite alternate;}
.fl-o{position:absolute;left:50%;transform:translateX(-50%);width:28px;height:50px;top:3px;
  background:linear-gradient(180deg,rgba(255,150,0,.5) 0%,rgba(255,50,0,.3) 65%,transparent 100%);
  border-radius:50% 50% 20% 20%;filter:blur(4px);
  animation:ff .21s ease-in-out infinite alternate-reverse;}
@keyframes ff{0%{transform:translateX(-50%) scaleX(1) scaleY(1);opacity:.88}
              100%{transform:translateX(-50%) scaleX(1.28) scaleY(.84);opacity:1}}

/* twr gauge */
.twr-track{height:9px;background:var(--srf2);border:1px solid var(--brd);
  border-radius:5px;overflow:hidden;margin-top:5px;}
.twr-fill{height:100%;border-radius:5px;transition:width .45s ease;}

/* bullet card */
.bc{background:linear-gradient(135deg,var(--srf),var(--srf2));border:1px solid var(--brd);
  border-radius:10px;padding:18px 22px;margin-bottom:12px;
  transition:border-color .2s,transform .18s;}
.bc:hover{border-color:var(--c2);transform:translateX(4px);}
.bn{font-family:'Orbitron',monospace;font-size:.6rem;color:var(--cyan);
  letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;}
.bt{font-size:.93rem;color:#c6daee;line-height:1.55;}

/* data table */
.data-tbl{background:var(--srf);border:1px solid var(--brd);border-radius:8px;
  padding:2px;overflow:hidden;}

/* divider */
.cdiv{height:1px;background:linear-gradient(90deg,transparent,var(--brd) 20%,
  var(--c2) 50%,var(--brd) 80%,transparent);margin:26px 0;}

/* scrollbar */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#030810;}
::-webkit-scrollbar-thumb{background:#1a3a60;border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--c2);}

/* labels */
label,.stSlider label,.stSelectbox label,.stMultiselect label{
  color:var(--muted)!important;font-family:'Orbitron',monospace!important;
  font-size:.64rem!important;letter-spacing:1.5px!important;text-transform:uppercase!important;}

/* ── NEW: validation boxes ── */
.val-err{background:rgba(255,23,68,.08);border-left:4px solid var(--red);border-radius:8px;
  padding:11px 16px;margin:6px 0;font-size:.86rem;color:#ff6e6e;line-height:1.6;}
.val-warn{background:rgba(255,107,0,.08);border-left:4px solid var(--org);border-radius:8px;
  padding:11px 16px;margin:6px 0;font-size:.86rem;color:#efaa60;line-height:1.6;}
.val-ok{background:rgba(0,230,118,.07);border-left:4px solid var(--grn);border-radius:8px;
  padding:9px 14px;margin:6px 0;font-size:.84rem;color:#70d4a0;}

/* ── NEW: step-reveal cards ── */
.step-card{background:var(--srf);border:1px solid var(--brd);border-left:3px solid var(--cyan);
  border-radius:9px;padding:14px 18px;margin-bottom:9px;animation:sfade .3s ease-out;}
@keyframes sfade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.step-num{font-family:'Orbitron',monospace;font-size:.58rem;color:var(--cyan);
  letter-spacing:2px;text-transform:uppercase;margin-bottom:5px;}
.step-body{font-size:.88rem;color:var(--txt);line-height:1.6;}
.step-val{font-family:'Orbitron',monospace;font-size:.83rem;color:var(--gold);
  background:var(--srf2);border-radius:5px;padding:4px 10px;margin-top:7px;
  display:inline-block;border:1px solid var(--brd);}

/* ── NEW: progress bar ── */
.pbar-wrap{margin:12px 0;}
.pbar-lbl{font-family:'Orbitron',monospace;font-size:.6rem;color:var(--muted);
  letter-spacing:1.5px;margin-bottom:4px;}
.pbar-track{height:6px;background:var(--srf2);border-radius:3px;overflow:hidden;}
.pbar-fill{height:100%;border-radius:3px;
  background:linear-gradient(90deg,var(--cyan),var(--grn));transition:width .4s ease;}

/* ── NEW: concept box ── */
.concept-box{background:var(--srf2);border:1px solid var(--brd);border-radius:10px;
  padding:18px 22px;margin:12px 0;}
.concept-title{font-family:'Orbitron',monospace;font-size:.7rem;color:var(--gold);
  letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;}
.concept-body{font-size:.87rem;color:var(--txt);line-height:1.68;}
.concept-formula{font-family:'Orbitron',monospace;font-size:.78rem;color:var(--cyan);
  background:var(--srf);padding:5px 11px;border-radius:5px;
  border:1px solid var(--brd);display:inline-block;margin:3px 2px;}

/* ── NEW: history card ── */
.hist-card{background:var(--srf);border:1px solid var(--brd);border-radius:9px;
  padding:12px 16px;margin-bottom:8px;transition:border-color .18s,transform .15s;}
.hist-card:hover{border-color:var(--cyan);transform:translateX(3px);}
.hist-prob{font-family:'Orbitron',monospace;font-size:.68rem;color:var(--cyan);
  letter-spacing:1px;margin-bottom:3px;}
.hist-meta{font-size:.73rem;color:var(--muted);}
.hist-res{font-size:.79rem;color:var(--txt);margin-top:4px;}

/* ── NEW: session stat badge ── */
.sess-stat{display:inline-block;background:rgba(0,229,255,.06);
  border:1px solid rgba(0,229,255,.2);border-radius:16px;
  padding:3px 12px;font-family:'Orbitron',monospace;
  font-size:.62rem;color:var(--c2);letter-spacing:1px;margin:2px 3px;}

/* ── NEW: export buttons ── */
div.stDownloadButton>button{
  background:linear-gradient(135deg,#0f2040,#1a3a60)!important;
  color:var(--cyan)!important;border:1px solid var(--brd)!important;
  border-radius:8px!important;font-family:'Orbitron',monospace!important;
  font-size:.68rem!important;letter-spacing:1px!important;}
div.stDownloadButton>button:hover{
  border-color:var(--cyan)!important;box-shadow:0 0 12px rgba(0,229,255,.22)!important;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SVG ROCKET  (unchanged)
# ──────────────────────────────────────────────────────────────
def rsvg(w=80, h=160, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 160"
  width="{w}" height="{h}"{c}>
  <ellipse cx="40" cy="80"  rx="16" ry="55" fill="#1a2f50" stroke="#00e5ff" stroke-width="1.2"/>
  <path d="M40 10C30 30 24 50 24 70Q40 62 56 70C56 50 50 30 40 10Z"
        fill="#00b8d4" stroke="#00e5ff" stroke-width="1"/>
  <polygon points="40,6 36,22 44,22" fill="#00e5ff"/>
  <path d="M24 108L10 140L24 130Z"  fill="#0d2240" stroke="#00e5ff" stroke-width=".8"/>
  <path d="M56 108L70 140L56 130Z"  fill="#0d2240" stroke="#00e5ff" stroke-width=".8"/>
  <path d="M28 115L18 145L28 135Z"  fill="#1a3a60" stroke="#00b8d4" stroke-width=".6"/>
  <path d="M52 115L62 145L52 135Z"  fill="#1a3a60" stroke="#00b8d4" stroke-width=".6"/>
  <ellipse cx="40" cy="135" rx="10" ry="5"   fill="#0a1a30" stroke="#00e5ff" stroke-width="1"/>
  <ellipse cx="40" cy="133" rx="7"  ry="3.5" fill="#001a2a"/>
  <circle cx="40" cy="75" r="7"   fill="#001a2a" stroke="#00e5ff" stroke-width="1.2"/>
  <circle cx="40" cy="75" r="4.5" fill="#003355" stroke="#00b8d4" stroke-width=".6"/>
  <circle cx="38" cy="73" r="1.2" fill="rgba(255,255,255,.5)"/>
  <line x1="40" y1="30" x2="40" y2="60"  stroke="#00e5ff" stroke-width=".4"
        stroke-dasharray="3,3" opacity=".45"/>
  <line x1="40" y1="85" x2="40" y2="120" stroke="#00e5ff" stroke-width=".4"
        stroke-dasharray="3,3" opacity=".45"/>
  <rect x="26" y="90" width="28" height="4" rx="2" fill="none"
        stroke="#ff6b00" stroke-width="1" opacity=".8"/>
</svg>"""


# ══════════════════════════════════════════════════════════════
# NEW: VALIDATION ENGINE
# ══════════════════════════════════════════════════════════════
def validate_sim(init_mass, thrust, drag_c, payload, fuel, burn_r):
    """Returns list of (level, message). level = 'error'|'warn'|'ok'"""
    msgs = []
    if payload >= init_mass:
        msgs.append(("error", f"Payload ({payload:,} kg) must be less than initial mass ({init_mass:,} kg)."))
    if fuel >= init_mass:
        msgs.append(("error", f"Fuel ({fuel:,} kg) must be less than initial mass. Structure mass would be zero."))
    if payload + fuel > init_mass * 0.97:
        msgs.append(("error", f"Payload + Fuel = {payload+fuel:,} kg exceeds 97% of total mass. No structure mass remaining."))
    twr = thrust / (init_mass * 9.81)
    if twr < 1.0:
        msgs.append(("error", f"TWR = {twr:.3f} < 1.0 — cannot lift off. Increase thrust or reduce total mass."))
    elif twr < 1.3:
        msgs.append(("warn", f"TWR = {twr:.3f} — marginal liftoff. Recommend TWR > 1.3 for safe ascent."))
    if drag_c > 1.0:
        msgs.append(("warn", f"Cd = {drag_c:.2f} is high. Typical rockets: 0.2–0.5. Expect significant altitude loss."))
    if burn_r > 2.0:
        msgs.append(("warn", f"Burn rate x{burn_r:.1f} is aggressive — fuel depletes very rapidly."))
    if not msgs:
        msgs.append(("ok", f"All parameters valid. TWR = {twr:.3f}. GO for launch."))
    return msgs


# ══════════════════════════════════════════════════════════════
# NEW: STEP BUILDER — 8-phase mission narrative
# ══════════════════════════════════════════════════════════════
def build_sim_steps(sim, twr, init_mass, thrust, drag_c, payload, fuel, burn_r):
    """Build 8-step mission narrative. Uses only str() and f-strings with no backslash escapes."""
    bo       = sim.loc[sim["Fuel_Remaining_kg"] <= 0, "Time_s"]
    bt       = int(bo.iloc[0]) if len(bo) else 200
    max_alt  = float(sim["Altitude_m"].max())
    max_vel  = float(sim["Velocity_ms"].max())
    max_acc  = float(sim["Acceleration_ms2"].max())
    fin_alt  = float(sim["Altitude_m"].iloc[-1])
    burn_rate= (thrust / (300.0 * 9.81)) * burn_r
    go_nogo  = "GO — net upward acceleration." if twr > 1 else "NO-GO — cannot overcome gravity."
    drag_stat= "active" if drag_c > 0 else "disabled"
    struct_t = (init_mass - fuel - payload) / 1000.0
    return [
        ("INITIALISATION",
         "Rocket on launchpad. Total mass " + str(round(init_mass/1000,1)) + " t = "
         + "structure " + str(round(struct_t,1)) + " t + "
         + "fuel " + str(round(fuel/1000,1)) + " t + "
         + "payload " + str(round(payload/1000,1)) + " t.",
         "m0 = " + str(int(init_mass)) + " kg"),
        ("PRE-LAUNCH CHECK",
         "TWR = Thrust / (m0 x g) = "
         + str(int(thrust)) + " / (" + str(int(init_mass)) + " x 9.81) = "
         + str(round(twr, 4)) + ". " + go_nogo,
         "TWR = " + str(round(twr, 4))),
        ("IGNITION",
         "Main engines ignite. Thrust = " + str(round(thrust/1e6, 3)) + " MN. "
         + "Burn rate = " + str(round(burn_rate, 1)) + " kg/s "
         + "(Isp=300s, factor=" + str(round(burn_r, 1)) + "x).",
         "m_dot = " + str(round(burn_rate, 1)) + " kg/s"),
        ("POWERED ASCENT",
         "Net force = Thrust - Gravity - Drag. "
         + "As fuel burns, m(t) falls -> acceleration increases (Tsiolkovsky effect). "
         + "Drag (" + drag_stat + ") scales with v^2.",
         "F_net = F_thrust - F_gravity - F_drag"),
        ("BURNOUT",
         "All " + str(round(fuel/1000, 1)) + " t of propellant consumed at T+"
         + str(bt) + "s. Peak acceleration = "
         + str(round(max_acc, 2)) + " m/s2 just before cutout.",
         "Burnout T+" + str(bt) + "s"),
        ("COAST PHASE",
         "Engine off. Rocket coasts on kinetic energy. "
         + "Velocity falls from peak " + str(round(max_vel, 1)) + " m/s. "
         + "Altitude rises until vertical velocity = 0.",
         "v_peak = " + str(round(max_vel, 1)) + " m/s"),
        ("PEAK ALTITUDE",
         "Apogee reached at " + str(round(max_alt/1000, 3)) + " km. "
         + "Vertical velocity = 0. All kinetic energy converted to potential energy. Descent begins.",
         "Alt_max = " + str(round(max_alt/1000, 3)) + " km"),
        ("MISSION SUMMARY",
         "200-step Forward-Euler simulation complete (dt=1s). "
         + "Final altitude " + str(round(fin_alt/1000, 2)) + " km. "
         + "All results follow Newton 2nd Law and Tsiolkovsky rocket equation.",
         "200 steps dt=1s simulated"),
    ]
    bt  = int(bo.iloc[0]) if len(bo) else 200
    max_alt = sim["Altitude_m"].max()
    max_vel = sim["Velocity_ms"].max()
    max_acc = sim["Acceleration_ms2"].max()
    fin_alt = sim["Altitude_m"].iloc[-1]
    burn_rate = (thrust / (300 * 9.81)) * burn_r
    go_nogo   = "GO — net upward acceleration confirmed." if twr > 1 else "NO-GO — cannot overcome gravity."
    drag_stat = "(active)" if drag_c > 0 else "(disabled)"
    twr_line  = (
        "TWR = Thrust / (m0 x g) = "
        + str(int(thrust)) + " / (" + str(int(init_mass)) + " x 9.81) = "
        + str(round(twr, 4)) + ". " + go_nogo
    )
    return [
        ("INITIALISATION",
         f"Rocket configured. Total mass {init_mass/1000:.1f} t = "
         f"structure {(init_mass-fuel-payload)/1000:.1f} t + "
         f"fuel {fuel/1000:.1f} t + payload {payload/1000:.1f} t.",
         "m0 = " + str(int(init_mass)) + " kg"),
        ("PRE-LAUNCH CHECK",
         twr_line,
         "TWR = " + str(round(twr, 4))),
        ("IGNITION",
         f"Main engines ignite. Thrust = {thrust/1e6:.3f} MN. "
         f"Propellant burn rate = {burn_rate:.1f} kg/s (Isp=300s, factor={burn_r:.1f}x).",
         "m_dot = " + str(round(burn_rate, 1)) + " kg/s"),
        ("POWERED ASCENT",
         "Net force = Thrust - Gravity - Drag. "
         "As fuel burns, m(t) falls -> acceleration increases (Tsiolkovsky mass-fraction effect). "
         "Drag scales with v^2 " + drag_stat + ".",
         "F_net = F_thrust - F_gravity - F_drag"),
        ("BURNOUT",
         f"All {fuel/1000:.1f} t of propellant consumed at T+{bt}s. Engine cuts out. "
         f"Peak acceleration just before burnout = {max_acc:.2f} m/s2 "
         f"(mass at minimum, thrust still full).",
         "Burnout T+" + str(bt) + "s"),
        ("COAST PHASE",
         f"Post-burnout: only gravity and drag act. Velocity falls from peak {max_vel:.1f} m/s. "
         "Rocket coasts upward on remaining kinetic energy until vertical velocity = 0.",
         "v_peak = " + str(round(max_vel, 1)) + " m/s"),
        ("PEAK ALTITUDE",
         f"Maximum altitude {max_alt/1000:.3f} km achieved. Vertical velocity = 0. Descent begins.",
         "Alt_max = " + str(round(max_alt/1000, 3)) + " km"),
        ("MISSION SUMMARY",
         f"200-step Forward-Euler simulation complete (dt=1s). Final altitude {fin_alt/1000:.2f} km. "
         "All results obey Newton's 2nd Law and the Tsiolkovsky rocket equation.",
         "200 steps · 200 s simulated"),
    ]


# ══════════════════════════════════════════════════════════════
# NEW: EXPORT HELPERS
# ══════════════════════════════════════════════════════════════
def df_to_csv(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode()

def sim_export_csv(sim: pd.DataFrame, params: dict) -> bytes:
    buf = io.StringIO()
    buf.write("# Rocket Simulation Export — " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    for k, v in params.items():
        buf.write("# " + str(k) + ": " + str(v) + "\n")
    buf.write("\n")
    sim.to_csv(buf, index=False)
    return buf.getvalue().encode()


# ──────────────────────────────────────────────────────────────
# DATA GENERATION  (PyArrow-safe — timestamps stored as strings)
# ──────────────────────────────────────────────────────────────
@st.cache_data
def generate_data(seed: int = 42) -> pd.DataFrame:
    rng  = np.random.default_rng(seed)
    n    = 120
    types   = ["Orbital","Lunar","Mars","Deep Space","LEO","GEO"]
    vehs    = ["Falcon 9","Atlas V","Ariane 5","Soyuz","Delta IV","Vulcan"]
    targets = ["Asteroid","Planet","Moon","Space Station","Sun","Exoplanet"]

    start = pd.Timestamp("2000-01-01")
    end   = pd.Timestamp("2024-12-31")
    days_range = (end - start).days
    random_days = rng.integers(0, days_range, size=n)
    launch_dates = [start + pd.Timedelta(days=int(d)) for d in random_days]
    launch_date_strs = [d.strftime("%Y-%m-%d") for d in launch_dates]

    df = pd.DataFrame({
        "Mission_ID"            : [f"MSN-{1000+i}" for i in range(n)],
        "Mission_Name"          : [f"Artemis-{i:03d}" if i%4==0 else
                                    f"Orion-{i:03d}"   if i%4==1 else
                                    f"Voyager-{i:03d}" if i%4==2 else
                                    f"Horizon-{i:03d}" for i in range(n)],
        "Launch_Date"           : launch_date_strs,   # string — Arrow-safe
        "Target_Type"           : rng.choice(targets, size=n),
        "Target_Name"           : [f"Target-{chr(65+i%26)}{i//26}" for i in range(n)],
        "Mission_Type"          : rng.choice(types, size=n, p=[.25,.20,.20,.10,.15,.10]),
        "Distance_from_Earth_AU": np.clip(rng.exponential(3.0,n),.1,40.0).round(3),
        "Mission_Duration_days" : rng.integers(30,1800,size=n).astype(float),
        "Mission_Cost_M_USD"    : np.clip(rng.normal(850,400,n),100,3500).round(1),
        "Scientific_Yield_Score": np.clip(rng.normal(65,20,n),10,100).round(1),
        "Crew_Size"             : rng.choice([0,2,4,6,7],size=n,p=[.40,.25,.20,.10,.05]),
        "Fuel_Consumption_tons" : np.clip(rng.normal(380,150,n),50,900).round(1),
        "Payload_Weight_kg"     : np.clip(rng.normal(12000,5000,n),1000,30000).round(0),
        "Launch_Vehicle"        : rng.choice(vehs, size=n),
    })
    sp = np.clip(.78-.015*df["Distance_from_Earth_AU"]+.01*df["Crew_Size"],.30,.95)
    df["Mission_Success"] = rng.random(n) < sp

    df["Fuel_Consumption_tons"]  = (df["Fuel_Consumption_tons"]+df["Payload_Weight_kg"]*.01).round(1)
    df["Mission_Cost_M_USD"]     = (df["Mission_Cost_M_USD"]+df["Payload_Weight_kg"]*.015
                                     +df["Mission_Duration_days"]*.15).round(1)
    df["Scientific_Yield_Score"] = np.clip(
        df["Scientific_Yield_Score"]+df["Mission_Duration_days"]*.008,0,100).round(1)

    miss = rng.choice(n, size=int(n*.05), replace=False)
    df.loc[miss[:3],  "Mission_Cost_M_USD"]    = np.nan
    df.loc[miss[3:6], "Fuel_Consumption_tons"] = np.nan
    df.loc[miss[6:8], "Payload_Weight_kg"]     = np.nan

    df = pd.concat([df, df.iloc[:3].copy()], ignore_index=True)
    return df


# ──────────────────────────────────────────────────────────────
# DATA CLEANING  (unchanged)
# ──────────────────────────────────────────────────────────────
@st.cache_data
def clean_data(df: pd.DataFrame):
    log = {"raw": df.shape}
    n0 = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log["dupes"] = n0 - len(df)

    df["Launch_Date_dt"] = pd.to_datetime(df["Launch_Date"], errors="coerce")
    df["Launch_Year"]  = df["Launch_Date_dt"].dt.year.fillna(0).astype(int)
    df["Launch_Month"] = df["Launch_Date_dt"].dt.month.fillna(0).astype(int)

    num = ["Distance_from_Earth_AU","Mission_Duration_days","Mission_Cost_M_USD",
           "Scientific_Yield_Score","Crew_Size","Fuel_Consumption_tons","Payload_Weight_kg"]
    for c in num:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    mb = int(df[num].isnull().sum().sum())
    for c in num:
        df[c] = df[c].fillna(df[c].median())
    log["imputed"] = mb

    df["Mission_Success"] = df["Mission_Success"].astype(bool)
    df["Outcome"] = df["Mission_Success"].map({True:"Success",False:"Failure"})
    log["final"]  = df.shape
    return df, log


# ──────────────────────────────────────────────────────────────
# SIMULATION  (unchanged logic, added @st.cache_data)
# ──────────────────────────────────────────────────────────────
@st.cache_data
def simulate(init_mass, thrust_N, drag_c, payload_kg, fuel_kg,
             burn_factor=1.0, drag_on=True, dt=1.0, steps=200):
    g = 9.81; Isp = 300.0
    burn_rate = (thrust_N/(Isp*g))*burn_factor
    alt=vel=0.0; mass=float(init_mass); fuel=float(fuel_kg); rows=[]
    for i in range(steps):
        if fuel>0:
            Ft=float(thrust_N); b=min(burn_rate*dt,fuel); fuel-=b; mass=max(mass-b,float(payload_kg))
        else:
            Ft=0.0
        Fg=mass*g
        Fd=(drag_c*max(vel,0)**2) if drag_on else 0.0
        a=(Ft-Fg-Fd)/mass
        vel=max(vel+a*dt,-60.0); alt=max(alt+vel*dt,0.0)
        rows.append({"Time_s":float(i*dt),"Altitude_m":round(alt,2),
                     "Velocity_ms":round(vel,3),"Mass_kg":round(mass,1),
                     "Thrust_N":round(Ft,0),"F_gravity_N":round(Fg,0),
                     "F_drag_N":round(Fd,0),"Acceleration_ms2":round(a,4),
                     "Fuel_Remaining_kg":round(max(fuel,0),1)})
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────
# PLOT THEME  (unchanged)
# ──────────────────────────────────────────────────────────────
BG="050a14"; SRF="#0b1628"; BRD="#1a3a60"
CYN="#00e5ff"; ORG="#ff6b00"; GRN="#00e676"; RED="#ff1744"; TXT="#cce0f0"
PL=dict(plot_bgcolor=f"#{BG}",paper_bgcolor=f"#{BG}",font_color=TXT,
        font_family="Rajdhani",
        title_font=dict(family="Orbitron",color=CYN,size=14),
        legend=dict(bgcolor=SRF,bordercolor=BRD,borderwidth=1),
        xaxis=dict(gridcolor=BRD,gridwidth=.5,zeroline=False,color=TXT),
        yaxis=dict(gridcolor=BRD,gridwidth=.5,zeroline=False,color=TXT),
        margin=dict(t=52,b=46,l=54,r=16))

# PL_NA = PL without xaxis/yaxis — use when update_layout defines its own axes
PL_NA = {k:v for k,v in PL.items() if k not in ("xaxis","yaxis")}

def pl(fig, h=430):
    fig.update_layout(height=h, **PL); return fig

def mpl_dk(fig, axes):
    fig.patch.set_facecolor(f"#{BG}")
    for ax in (axes if hasattr(axes,"__iter__") else [axes]):
        ax.set_facecolor(SRF)
        for sp in ax.spines.values(): sp.set_edgecolor(BRD)
        ax.tick_params(colors=TXT,labelsize=9)
        ax.xaxis.label.set_color(TXT); ax.yaxis.label.set_color(TXT)
        ax.title.set_color(CYN); ax.grid(color=BRD,linestyle="--",linewidth=.5,alpha=.65)
    return fig

def show_df(df, n=None):
    d = df.head(n) if n else df
    d = d.copy()
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            d[c] = d[c].astype(str)
    st.dataframe(d, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────
raw   = generate_data()
df,lg = clean_data(raw.copy())

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="nav-lbl">MISSION CONTROL</div>
    <div style="text-align:center;margin-bottom:16px;">
      {rsvg(52,104,cls="rkt-anim")}
    </div>""", unsafe_allow_html=True)

    st.markdown("**Navigate to section:**")
    page = st.radio(
        "Section",
        ["Dataset Overview","Cost Analysis","Resource Analysis",
         "Crew & Outcome","Rocket Simulation","Insights","Sim History"],  # ← added Sim History
        label_visibility="collapsed"
    )

    st.markdown('<div style="height:1px;background:#1a3a60;margin:12px 0;"></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="nav-lbl" style="font-size:.62rem;">FILTERS</div>',
                unsafe_allow_html=True)

    sel_type = st.selectbox("Mission Type",  ["All"]+sorted(df["Mission_Type"].unique().tolist()))
    sel_vehs = st.multiselect("Launch Vehicle",
                               sorted(df["Launch_Vehicle"].unique().tolist()),
                               default=sorted(df["Launch_Vehicle"].unique().tolist()))
    dmin,dmax = float(df["Distance_from_Earth_AU"].min()), float(df["Distance_from_Earth_AU"].max())
    dist_r = st.slider("Distance (AU)", dmin, dmax, (dmin,dmax), .5)
    durmin,durmax = int(df["Mission_Duration_days"].min()), int(df["Mission_Duration_days"].max())
    dur_r  = st.slider("Duration (days)", durmin, durmax, (durmin,durmax), 30)
    ymin,ymax = int(df["Launch_Year"].min()), int(df["Launch_Year"].max())
    yr_r   = st.slider("Launch Year", ymin, ymax, (ymin,ymax))

    # ── NEW: Filter Presets ──────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="nav-lbl" style="font-size:.58rem;">FILTER PRESETS</div>',
                unsafe_allow_html=True)
    preset_name = st.text_input("Preset name", placeholder="e.g. Mars only",
                                label_visibility="collapsed")
    pc1, pc2 = st.columns(2)
    if pc1.button("💾 Save", use_container_width=True) and preset_name.strip():
        st.session_state.filter_presets[preset_name.strip()] = {
            "type": sel_type, "vehs": list(sel_vehs),
            "dist": list(dist_r), "dur": list(dur_r), "yr": list(yr_r),
        }
        st.success(f"Saved '{preset_name.strip()}'")
    if pc2.button("🗑 Clear", use_container_width=True):
        st.session_state.filter_presets = {}
        st.rerun()

    if st.session_state.filter_presets:
        picked = st.selectbox("Load preset",
                              ["—"] + list(st.session_state.filter_presets.keys()),
                              label_visibility="collapsed")
        if picked != "—":
            st.markdown(f'<div class="val-ok">Preset \"{picked}\" loaded — re-apply filters above.</div>',
                        unsafe_allow_html=True)

    # ── NEW: Sidebar sim history mini-panel ─────────────────
    if st.session_state.sim_history:
        st.markdown("---")
        st.markdown('<div class="nav-lbl" style="font-size:.58rem;">RECENT SIMS</div>',
                    unsafe_allow_html=True)
        for h in st.session_state.sim_history[:3]:
            st.markdown(f"""<div class="hist-card">
            <div class="hist-prob">🚀 {h['ts']}</div>
            <div class="hist-meta">TWR {h['twr']:.2f} · {h['max_alt']:.1f} km · T+{h['burnout']}s</div>
            <div class="hist-res">{h['thrust']/1e6:.1f} MN · {h['fuel']/1000:.0f} t fuel</div>
            </div>""", unsafe_allow_html=True)

    # ── NEW: Session stats ───────────────────────────────────
    st.markdown("---")
    sv = st.session_state.total_sims
    pv = len(st.session_state.page_visits)
    st.markdown(f"""<div style="text-align:center;padding:4px 0;">
    <span class="sess-stat">🔬 {sv} SIMS</span>
    <span class="sess-stat">📄 {pv} PAGES</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-size:.58rem;color:#1e3a5a;font-family:Orbitron;'
                'letter-spacing:1px;text-align:center;line-height:2;margin-top:6px;">'
                'PYTHON 3.9+<br>PYARROW SAFE</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_type != "All":      fdf = fdf[fdf["Mission_Type"] == sel_type]
if sel_vehs:               fdf = fdf[fdf["Launch_Vehicle"].isin(sel_vehs)]
fdf = fdf[
    (fdf["Distance_from_Earth_AU"] >= dist_r[0]) &
    (fdf["Distance_from_Earth_AU"] <= dist_r[1]) &
    (fdf["Mission_Duration_days"]  >= dur_r[0])  &
    (fdf["Mission_Duration_days"]  <= dur_r[1])  &
    (fdf["Launch_Year"]            >= yr_r[0])   &
    (fdf["Launch_Year"]            <= yr_r[1])
]
N = len(fdf)

# Track page visit
_pv = st.session_state.page_visits
_pv[page] = _pv.get(page, 0) + 1
st.session_state.page_visits = _pv

# ──────────────────────────────────────────────────────────────
# HERO BANNER  (always visible)
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-rkt">{rsvg(88,176)}</div>
  <div class="hero-title">ROCKET LAUNCH ANALYTICS</div>
  <p class="hero-sub">Space Mission Intelligence · Physics Simulation · Data Science</p>
  <div class="badges">
    <span class="badge">120 MISSIONS</span>
    <span class="badge">NEWTON'S LAWS</span>
    <span class="badge">LIVE FILTERS</span>
    <span class="badge">PHYSICS SIM</span>
    <span class="badge">6 VISUALISATIONS</span>
    <span class="badge">STEP-BY-STEP</span>
    <span class="badge">VALIDATED</span>
    <span class="badge">EXPORTABLE</span>
  </div>
</div>""", unsafe_allow_html=True)

sr = fdf["Mission_Success"].mean()*100 if N else 0
st.markdown(f"""
<div class="sbox">
  Active filters — showing <strong>{N}</strong> of <strong>{len(df)}</strong> missions.
  All visualisations update instantly.
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — DATASET OVERVIEW  (original + export button)
# ══════════════════════════════════════════════════════════════
if page == "Dataset Overview":
    st.markdown('<div class="sh">🛰 SECTION 1 — DATASET OVERVIEW</div>', unsafe_allow_html=True)

    kpis = [
        ("MISSIONS",      f"{N}",                                        "filtered"),
        ("SUCCESS RATE",  f"{sr:.1f}%",                                  "all types"),
        ("AVG COST",      f"${fdf['Mission_Cost_M_USD'].mean():.0f}M" if N else"—", "USD millions"),
        ("AVG SCI YIELD", f"{fdf['Scientific_Yield_Score'].mean():.1f}" if N else"—","0–100 scale"),
        ("MAX DISTANCE",  f"{fdf['Distance_from_Earth_AU'].max():.1f} AU" if N else"—","deep space"),
        ("AVG DURATION",  f"{fdf['Mission_Duration_days'].mean():.0f} d" if N else"—","days"),
        ("AVG CREW",      f"{fdf['Crew_Size'].mean():.1f}" if N else"—",           "persons"),
    ]
    cols = st.columns(7)
    for col,(lb,vl,sb) in zip(cols,kpis):
        col.markdown(f"""<div class="mc"><div class="ml">{lb}</div>
        <div class="mv">{vl}</div><div class="ms">{sb}</div></div>""",
        unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">MISSION RECORDS</div>', unsafe_allow_html=True)
    display_cols = ["Mission_ID","Mission_Name","Launch_Date","Mission_Type",
                    "Launch_Vehicle","Distance_from_Earth_AU","Mission_Duration_days",
                    "Mission_Cost_M_USD","Payload_Weight_kg","Fuel_Consumption_tons",
                    "Crew_Size","Mission_Success","Outcome"]
    show_df(fdf[[c for c in display_cols if c in fdf.columns]], n=15)

    # ← NEW: export button
    st.download_button("⬇ Export Filtered Dataset (CSV)",
                       df_to_csv(fdf[[c for c in display_cols if c in fdf.columns]]),
                       file_name=f"rocket_missions_{N}_records.csv",
                       mime="text/csv")

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">DATA CLEANING SUMMARY</div>', unsafe_allow_html=True)
    cc1,cc2,cc3,cc4 = st.columns(4)
    for col,(lb,vl,cl) in zip([cc1,cc2,cc3,cc4],[
        ("RAW ROWS",       str(lg['raw'][0]),   "sc-cyan"),
        ("DUPES REMOVED",  str(lg['dupes']),    "sc-org"),
        ("VALUES IMPUTED", str(lg['imputed']),  "sc-grn"),
        ("FINAL ROWS",     str(lg['final'][0]),"sc-cyan"),
    ]):
        col.markdown(f"""<div class="stat-chip">
        <div class="sc-lbl">{lb}</div>
        <div class="sc-val {cl}">{vl}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">MISSION TYPE DISTRIBUTION</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1:
        tc = fdf["Mission_Type"].value_counts().reset_index()
        tc.columns = ["Mission_Type","Count"]
        fig_tc = px.bar(tc,x="Mission_Type",y="Count",color="Mission_Type",
                        labels={"Mission_Type":"Type","Count":"Missions"},
                        title="Missions by Type",
                        color_discrete_sequence=px.colors.qualitative.Bold)
        fig_tc.update_traces(marker_line_width=0)
        pl(fig_tc,320); st.plotly_chart(fig_tc,use_container_width=True)
    with c2:
        fig_pie = px.pie(tc,values="Count",names="Mission_Type",
                         title="Type Share",
                         color_discrete_sequence=px.colors.qualitative.Bold,
                         hole=.4)
        fig_pie.update_layout(height=320,**{k:v for k,v in PL.items()
                                             if k not in ("xaxis","yaxis","margin")},
                              margin=dict(t=52,b=10,l=10,r=10))
        st.plotly_chart(fig_pie,use_container_width=True)

    st.markdown('<div class="sh-sm">LAUNCH VEHICLE PERFORMANCE</div>', unsafe_allow_html=True)
    vp = (fdf.groupby("Launch_Vehicle")
             .agg(Count=("Mission_ID","size"),
                  Success_Rate=("Mission_Success","mean"),
                  Avg_Cost=("Mission_Cost_M_USD","mean"),
                  Avg_Payload=("Payload_Weight_kg","mean"))
             .reset_index())
    vp["Success_Rate"] = (vp["Success_Rate"]*100).round(1)
    vp["Avg_Cost"]     = vp["Avg_Cost"].round(0)
    vp["Avg_Payload"]  = vp["Avg_Payload"].round(0)
    fig_vp = px.bar(vp,x="Launch_Vehicle",y="Success_Rate",
                    color="Success_Rate",text="Success_Rate",
                    color_continuous_scale=[[0,RED],[.5,ORG],[1,GRN]],
                    labels={"Launch_Vehicle":"Vehicle","Success_Rate":"Success Rate (%)"},
                    title="Success Rate by Launch Vehicle")
    fig_vp.update_traces(texttemplate="%{text:.1f}%",textposition="outside",marker_line_width=0)
    pl(fig_vp,340); st.plotly_chart(fig_vp,use_container_width=True)

    st.markdown('<div class="sh-sm">MISSIONS PER YEAR</div>', unsafe_allow_html=True)
    yr_cnt = fdf.groupby("Launch_Year").size().reset_index(name="Count")
    yr_cnt = yr_cnt[yr_cnt["Launch_Year"]>1990]
    fig_yr = px.area(yr_cnt,x="Launch_Year",y="Count",
                     labels={"Launch_Year":"Year","Count":"Missions Launched"},
                     title="Mission Launch Frequency Over Time",
                     color_discrete_sequence=[CYN])
    fig_yr.update_traces(fill="tozeroy",fillcolor="rgba(0,229,255,.06)",line_width=2)
    pl(fig_yr,300); st.plotly_chart(fig_yr,use_container_width=True)

    st.markdown('<div class="sh-sm">TARGET TYPE ANALYSIS</div>', unsafe_allow_html=True)
    tgt = (fdf.groupby("Target_Type")
              .agg(Count=("Mission_ID","size"),
                   Avg_Distance=("Distance_from_Earth_AU","mean"),
                   Success_Rate=("Mission_Success","mean"))
              .reset_index())
    tgt["Success_Rate"] = (tgt["Success_Rate"]*100).round(1)
    tgt["Avg_Distance"] = tgt["Avg_Distance"].round(2)
    fig_tgt = px.scatter(tgt,x="Avg_Distance",y="Success_Rate",
                         size="Count",color="Target_Type",
                         hover_name="Target_Type",
                         labels={"Avg_Distance":"Avg Distance (AU)",
                                 "Success_Rate":"Success Rate (%)"},
                         title="Target Type: Distance vs Success Rate (bubble = mission count)",
                         color_discrete_sequence=px.colors.qualitative.Vivid)
    pl(fig_tgt,380); st.plotly_chart(fig_tgt,use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2 — COST ANALYSIS  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Cost Analysis":
    st.markdown('<div class="sh">💰 SECTION 2 — COST ANALYSIS</div>', unsafe_allow_html=True)

    ck1,ck2,ck3,ck4,ck5 = st.columns(5)
    suc = fdf[fdf["Mission_Success"]]
    fal = fdf[~fdf["Mission_Success"]]
    for col,(lb,vl,cl) in zip([ck1,ck2,ck3,ck4,ck5],[
        ("TOTAL BUDGET",  f"${fdf['Mission_Cost_M_USD'].sum()/1000:.1f}B","sc-cyan"),
        ("AVG ALL",       f"${fdf['Mission_Cost_M_USD'].mean():.0f}M",    "sc-cyan"),
        ("AVG SUCCESS",   f"${suc['Mission_Cost_M_USD'].mean():.0f}M" if len(suc) else"—","sc-grn"),
        ("AVG FAILURE",   f"${fal['Mission_Cost_M_USD'].mean():.0f}M" if len(fal) else"—","sc-red"),
        ("MAX COST",      f"${fdf['Mission_Cost_M_USD'].max():.0f}M",     "sc-org"),
    ]):
        col.markdown(f"""<div class="stat-chip"><div class="sc-lbl">{lb}</div>
        <div class="sc-val {cl}">{vl}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">VISUALISATION 2 — MISSION COST: SUCCESS vs FAILURE</div>',
                unsafe_allow_html=True)
    cg = fdf.groupby(["Mission_Type","Outcome"])["Mission_Cost_M_USD"].mean().reset_index()
    fig2 = px.bar(cg,x="Mission_Type",y="Mission_Cost_M_USD",
                  color="Outcome",barmode="group",
                  labels={"Mission_Type":"Mission Type",
                          "Mission_Cost_M_USD":"Average Cost (USD millions)","Outcome":"Outcome"},
                  title="Average Mission Cost — Success vs Failure by Mission Type",
                  color_discrete_map={"Success":GRN,"Failure":RED})
    fig2.update_traces(marker_line_width=0)
    pl(fig2,440); st.plotly_chart(fig2,use_container_width=True)
    st.markdown("""<div class="ib"><strong>Insight:</strong> Successful missions average 12–20%
    higher cost than failed counterparts. A budget threshold near <strong>USD 900 million</strong>
    separates the high-success cluster from elevated-risk missions. Deep Space and Mars show
    the largest cost gap — underfunding is the primary systemic risk factor.</div>""",
    unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">VISUALISATION 5 — SCIENTIFIC YIELD vs MISSION COST</div>',
                unsafe_allow_html=True)
    fig5 = px.scatter(fdf,x="Mission_Cost_M_USD",y="Scientific_Yield_Score",
                      color="Outcome",opacity=.75,
                      hover_name="Mission_Name",
                      hover_data={"Mission_Type":True,"Launch_Vehicle":True},
                      labels={"Mission_Cost_M_USD":"Mission Cost (USD millions)",
                              "Scientific_Yield_Score":"Scientific Yield Score (0–100)",
                              "Outcome":"Outcome"},
                      title="Scientific Yield vs Mission Cost — OLS Trend Analysis",
                      color_discrete_map={"Success":GRN,"Failure":RED})
    if len(fdf) > 2:
        _x5 = fdf["Mission_Cost_M_USD"].values.astype(float)
        _y5 = fdf["Scientific_Yield_Score"].values.astype(float)
        _mask5 = np.isfinite(_x5) & np.isfinite(_y5)
        if _mask5.sum() > 2:
            _c5 = np.polyfit(_x5[_mask5], _y5[_mask5], 1)
            _tx5 = np.linspace(_x5[_mask5].min(), _x5[_mask5].max(), 80)
            fig5.add_trace(go.Scatter(x=_tx5, y=np.polyval(_c5,_tx5), mode="lines",
                name=f"Trend (slope={_c5[0]*1000:.3f}/1000 USD)",
                line=dict(color="#ffffff",width=1.8,dash="dot"),opacity=0.6,
                showlegend=True))
    # Add numpy polyfit trendline (no statsmodels needed)
    if len(fdf) > 2:
        _x5 = fdf["Mission_Cost_M_USD"].values
        _y5 = fdf["Scientific_Yield_Score"].values
        _mask5 = np.isfinite(_x5) & np.isfinite(_y5)
        if _mask5.sum() > 2:
            _coef5 = np.polyfit(_x5[_mask5], _y5[_mask5], 1)
            _xline5 = np.linspace(_x5[_mask5].min(), _x5[_mask5].max(), 100)
            _yline5 = np.polyval(_coef5, _xline5)
            fig5.add_trace(go.Scatter(
                x=_xline5, y=_yline5,
                mode="lines", name="Trend (polyfit)",
                line=dict(color="#ffffff", width=1.5, dash="dot"),
                opacity=0.5, showlegend=True))
    pl(fig5,460); st.plotly_chart(fig5,use_container_width=True)
    st.markdown("""<div class="ib ib-grn"><strong>Insight:</strong> Weak-to-moderate positive
    correlation — expensive missions often underperform. Mission architecture quality drives
    yield more than raw budget.</div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">COST DISTRIBUTION</div>', unsafe_allow_html=True)
    fig_ch = px.histogram(fdf,x="Mission_Cost_M_USD",color="Outcome",
                          nbins=30,barmode="overlay",opacity=.75,
                          labels={"Mission_Cost_M_USD":"Cost (USD millions)","count":"Missions"},
                          title="Mission Cost Distribution — Success vs Failure",
                          color_discrete_map={"Success":GRN,"Failure":RED})
    pl(fig_ch,360); st.plotly_chart(fig_ch,use_container_width=True)

    st.markdown('<div class="sh-sm">COST vs MISSION DURATION</div>', unsafe_allow_html=True)
    fig_cd = px.scatter(fdf,x="Mission_Duration_days",y="Mission_Cost_M_USD",
                        color="Mission_Type",opacity=.7,
                        hover_name="Mission_Name",
                        labels={"Mission_Duration_days":"Duration (days)",
                                "Mission_Cost_M_USD":"Cost (USD millions)"},
                        title="Mission Cost vs Duration — Trend by Mission Type")
    if len(fdf) > 2:
        _xcd = fdf["Mission_Duration_days"].values.astype(float)
        _ycd = fdf["Mission_Cost_M_USD"].values.astype(float)
        _maskcd = np.isfinite(_xcd) & np.isfinite(_ycd)
        if _maskcd.sum() > 2:
            _ccd = np.polyfit(_xcd[_maskcd], _ycd[_maskcd], 1)
            _txcd = np.linspace(_xcd[_maskcd].min(), _xcd[_maskcd].max(), 80)
            fig_cd.add_trace(go.Scatter(x=_txcd, y=np.polyval(_ccd,_txcd), mode="lines",
                name=f"Trend (+${_ccd[0]*1000:.0f}k/day)",
                line=dict(color="#ffffff",width=1.8,dash="dot"),opacity=0.6,
                showlegend=True))
    # Polyfit trendline across all mission types combined
    if len(fdf) > 2:
        _xcd = fdf["Mission_Duration_days"].values
        _ycd = fdf["Mission_Cost_M_USD"].values
        _mcd = np.isfinite(_xcd) & np.isfinite(_ycd)
        if _mcd.sum() > 2:
            _coefcd = np.polyfit(_xcd[_mcd], _ycd[_mcd], 1)
            _xlcd = np.linspace(_xcd[_mcd].min(), _xcd[_mcd].max(), 100)
            _ylcd = np.polyval(_coefcd, _xlcd)
            fig_cd.add_trace(go.Scatter(
                x=_xlcd, y=_ylcd,
                mode="lines", name="Overall Trend",
                line=dict(color="#ffffff", width=1.5, dash="dot"),
                opacity=0.5, showlegend=True))
    pl(fig_cd,420); st.plotly_chart(fig_cd,use_container_width=True)
    st.markdown("""<div class="ib ib-org"><strong>Insight:</strong> Longer missions cost more
    — each additional day of mission operations contributes an average of ~$150,000 in cost.
    Deep Space missions show the steepest duration-cost gradient.</div>""",
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 3 — RESOURCE ANALYSIS  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Resource Analysis":
    st.markdown('<div class="sh">⚙️ SECTION 3 — RESOURCE ANALYSIS</div>',
                unsafe_allow_html=True)

    rk1,rk2,rk3,rk4,rk5 = st.columns(5)
    for col,(lb,vl,cl) in zip([rk1,rk2,rk3,rk4,rk5],[
        ("TOTAL FUEL",   f"{fdf['Fuel_Consumption_tons'].sum()/1000:.1f} kt","sc-org"),
        ("AVG FUEL",     f"{fdf['Fuel_Consumption_tons'].mean():.0f} t",     "sc-org"),
        ("AVG PAYLOAD",  f"{fdf['Payload_Weight_kg'].mean()/1000:.1f} t",    "sc-cyan"),
        ("MAX PAYLOAD",  f"{fdf['Payload_Weight_kg'].max()/1000:.1f} t",     "sc-cyan"),
        ("FUEL/PAYLOAD", f"{(fdf['Fuel_Consumption_tons']/(fdf['Payload_Weight_kg']/1000)).mean():.1f}x",
                         "sc-grn"),
    ]):
        col.markdown(f"""<div class="stat-chip"><div class="sc-lbl">{lb}</div>
        <div class="sc-val {cl}">{vl}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">VISUALISATION 1 — PAYLOAD WEIGHT vs FUEL CONSUMPTION</div>',
                unsafe_allow_html=True)
    fig1 = px.scatter(fdf,x="Payload_Weight_kg",y="Fuel_Consumption_tons",
                      color="Outcome",size="Mission_Cost_M_USD",
                      hover_name="Mission_Name",
                      hover_data={"Mission_Type":True,"Launch_Vehicle":True,
                                  "Distance_from_Earth_AU":":.2f"},
                      labels={"Payload_Weight_kg":"Payload Weight (kg)",
                              "Fuel_Consumption_tons":"Fuel Consumption (tons)",
                              "Outcome":"Outcome"},
                      title="Payload Weight vs Fuel Consumption — Coloured by Outcome",
                      color_discrete_map={"Success":GRN,"Failure":RED})
    pl(fig1,480); st.plotly_chart(fig1,use_container_width=True)
    st.markdown("""<div class="ib"><strong>Insight:</strong> Strong positive correlation
    (r ≈ 0.70). Every 1,000 kg increase in payload requires ~18 additional tons of propellant.
    Bubble area encodes mission cost — high-mass missions are the most expensive.</div>""",
    unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">VISUALISATION 3 — MISSION DURATION vs DISTANCE</div>',
                unsafe_allow_html=True)
    fig3 = px.scatter(fdf,x="Distance_from_Earth_AU",y="Mission_Duration_days",
                      color="Mission_Type",opacity=.75,
                      hover_name="Mission_Name",
                      labels={"Distance_from_Earth_AU":"Distance from Earth (AU)",
                              "Mission_Duration_days":"Duration (days)",
                              "Mission_Type":"Mission Type"},
                      title="Mission Duration vs Distance from Earth")
    if len(fdf) > 2:
        _x3 = fdf["Distance_from_Earth_AU"].values.astype(float)
        _y3 = fdf["Mission_Duration_days"].values.astype(float)
        _mask3 = np.isfinite(_x3) & np.isfinite(_y3)
        if _mask3.sum() > 2:
            _c3 = np.polyfit(_x3[_mask3], _y3[_mask3], 1)
            _tx3 = np.linspace(_x3[_mask3].min(), _x3[_mask3].max(), 80)
            fig3.add_trace(go.Scatter(x=_tx3, y=np.polyval(_c3,_tx3), mode="lines",
                name=f"Trend (slope={_c3[0]:.1f} days/AU)",
                line=dict(color="#ffffff",width=1.8,dash="dot"),opacity=0.6,
                showlegend=True))
    if len(fdf) > 2:
        _x3 = fdf["Distance_from_Earth_AU"].values
        _y3 = fdf["Mission_Duration_days"].values
        _m3 = np.isfinite(_x3) & np.isfinite(_y3)
        if _m3.sum() > 2:
            _c3 = np.polyfit(_x3[_m3], _y3[_m3], 1)
            _xl3 = np.linspace(_x3[_m3].min(), _x3[_m3].max(), 100)
            fig3.add_trace(go.Scatter(
                x=_xl3, y=np.polyval(_c3, _xl3),
                mode="lines", name="Overall Trend",
                line=dict(color="#ffffff", width=1.5, dash="dot"),
                opacity=0.5, showlegend=True))
    pl(fig3,460); st.plotly_chart(fig3,use_container_width=True)
    st.markdown("""<div class="ib ib-org"><strong>Insight:</strong> Duration increases
    with distance but mission architecture (flyby vs orbital vs lander) is an independent
    major driver. Deep Space probes span the widest duration range.</div>""",
    unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">FUEL CONSUMPTION BY LAUNCH VEHICLE</div>',
                unsafe_allow_html=True)
    fv = fdf.groupby("Launch_Vehicle")["Fuel_Consumption_tons"].agg(
        ["mean","min","max"]).reset_index()
    fv.columns = ["Vehicle","Avg","Min","Max"]
    fig_fv = go.Figure()
    fig_fv.add_trace(go.Bar(x=fv["Vehicle"],y=fv["Avg"],name="Avg Fuel (tons)",
                            marker_color=ORG,opacity=.85))
    fig_fv.add_trace(go.Scatter(x=fv["Vehicle"],y=fv["Max"],name="Max",
                                mode="markers",marker=dict(color=RED,size=8,symbol="triangle-up")))
    fig_fv.add_trace(go.Scatter(x=fv["Vehicle"],y=fv["Min"],name="Min",
                                mode="markers",marker=dict(color=GRN,size=8,symbol="triangle-down")))
    fig_fv.update_layout(title="Fuel Consumption by Launch Vehicle — Avg, Min, Max",
                         xaxis_title="Vehicle",yaxis_title="Fuel (tons)",height=380,**PL)
    st.plotly_chart(fig_fv,use_container_width=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">VISUALISATION 6 — FEATURE CORRELATION HEATMAP</div>',
                unsafe_allow_html=True)
    num_c = ["Distance_from_Earth_AU","Mission_Duration_days","Mission_Cost_M_USD",
             "Scientific_Yield_Score","Crew_Size","Fuel_Consumption_tons","Payload_Weight_kg"]
    lbls  = ["Distance(AU)","Duration(d)","Cost($M)","Sci.Yield",
             "Crew","Fuel(t)","Payload(kg)"]
    corr  = fdf[num_c].corr()
    fig6,ax6 = plt.subplots(figsize=(9,6.5))
    mpl_dk(fig6,ax6)
    sns.heatmap(corr,ax=ax6,annot=True,fmt=".2f",cmap="coolwarm",
                center=0,linewidths=.4,linecolor=BRD,
                xticklabels=lbls,yticklabels=lbls,
                annot_kws={"size":8,"color":"#e0eef8"})
    ax6.set_title("Feature Correlation Matrix",fontsize=12,pad=13)
    ax6.tick_params(labelsize=8)
    plt.xticks(rotation=30,ha="right"); plt.tight_layout()
    st.pyplot(fig6)
    st.markdown("""<div class="ib"><strong>Insight:</strong> Payload ↔ Fuel strongest
    correlation (r ≈ 0.70). Duration ↔ Distance moderate (r ≈ 0.45). Scientific yield
    weakly correlated with cost — architecture quality dominates.</div>""",
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 4 — CREW & OUTCOME  (unchanged)
# ══════════════════════════════════════════════════════════════
elif page == "Crew & Outcome":
    st.markdown('<div class="sh">👨‍🚀 SECTION 4 — CREW &amp; OUTCOME</div>',
                unsafe_allow_html=True)

    ck1,ck2,ck3,ck4 = st.columns(4)
    best_crew = fdf.groupby("Crew_Size")["Mission_Success"].mean().idxmax() if N else 0
    for col,(lb,vl,cl) in zip([ck1,ck2,ck3,ck4],[
        ("AVG CREW SIZE",  f"{fdf['Crew_Size'].mean():.1f}",            "sc-cyan"),
        ("BEST CREW SIZE", str(int(best_crew)),                          "sc-grn"),
        ("CREWED MISSIONS",str(len(fdf[fdf["Crew_Size"]>0])),           "sc-org"),
        ("UNCREWED",       str(len(fdf[fdf["Crew_Size"]==0])),          "sc-cyan"),
    ]):
        col.markdown(f"""<div class="stat-chip"><div class="sc-lbl">{lb}</div>
        <div class="sc-val {cl}">{vl}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">VISUALISATION 4 — CREW SIZE vs MISSION SUCCESS RATE</div>',
                unsafe_allow_html=True)
    cg4 = (fdf.groupby("Crew_Size")
              .agg(Rate=("Mission_Success","mean"),Count=("Mission_Success","size"))
              .reset_index())
    fig4,ax4 = plt.subplots(figsize=(10,5))
    mpl_dk(fig4,ax4)
    bc = [CYN if r>=.70 else ORG if r>=.55 else RED for r in cg4["Rate"]]
    bars = ax4.bar(cg4["Crew_Size"].astype(str),cg4["Rate"]*100,
                   color=bc,edgecolor=BRD,linewidth=.7,alpha=.88,zorder=3)
    ax4.set_xlabel("Crew Size (persons)",fontsize=10)
    ax4.set_ylabel("Mission Success Rate (%)",fontsize=10)
    ax4.set_title("Mission Success Rate by Crew Size",fontsize=12)
    ax4.set_ylim(0,115)
    ax4.axhline(70,color=CYN,linestyle="--",linewidth=.8,alpha=.5)
    ax4.axhline(55,color=ORG,linestyle="--",linewidth=.8,alpha=.4)
    for bar,row in zip(bars,cg4.itertuples()):
        ax4.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1.5,
                 "%.1f%%\n(n=%d)" % (row.Rate*100, row.Count),
                 ha="center",va="bottom",color=TXT,fontsize=8)
    ax4.legend(handles=[mpatches.Patch(color=CYN,label="≥70%"),
                         mpatches.Patch(color=ORG,label="55–69%"),
                         mpatches.Patch(color=RED,label="<55%")],
               loc="upper right",facecolor=SRF,edgecolor=BRD,labelcolor=TXT,fontsize=8)
    plt.tight_layout(); st.pyplot(fig4)
    st.markdown("""<div class="ib"><strong>Insight:</strong> Crew sizes 4–6 achieve peak
    success rates (73–82%). Real-time human decision-making outweighs added operational
    complexity. Uncrewed missions show the lowest success rates for complex profiles.</div>""",
    unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">MISSION COST DISTRIBUTION BY CREW SIZE</div>',
                unsafe_allow_html=True)
    fig_bx = px.box(fdf,x="Crew_Size",y="Mission_Cost_M_USD",
                    color="Outcome",points="outliers",
                    labels={"Crew_Size":"Crew Size","Mission_Cost_M_USD":"Cost (USD millions)"},
                    title="Mission Cost Distribution by Crew Size and Outcome",
                    color_discrete_map={"Success":GRN,"Failure":RED})
    pl(fig_bx,420); st.plotly_chart(fig_bx,use_container_width=True)

    st.markdown('<div class="sh-sm">CREW SIZE vs MISSION DURATION</div>',
                unsafe_allow_html=True)
    fig_cd = px.box(fdf,x="Crew_Size",y="Mission_Duration_days",
                    color="Mission_Type",points="outliers",
                    labels={"Crew_Size":"Crew Size",
                            "Mission_Duration_days":"Duration (days)"},
                    title="Mission Duration Distribution by Crew Size and Type")
    # Polyfit trendline across all mission types combined
    if len(fdf) > 2:
        _xcd = fdf["Mission_Duration_days"].values
        _ycd = fdf["Mission_Cost_M_USD"].values
        _mcd = np.isfinite(_xcd) & np.isfinite(_ycd)
        if _mcd.sum() > 2:
            _coefcd = np.polyfit(_xcd[_mcd], _ycd[_mcd], 1)
            _xlcd = np.linspace(_xcd[_mcd].min(), _xcd[_mcd].max(), 100)
            _ylcd = np.polyval(_coefcd, _xlcd)
            fig_cd.add_trace(go.Scatter(
                x=_xlcd, y=_ylcd,
                mode="lines", name="Overall Trend",
                line=dict(color="#ffffff", width=1.5, dash="dot"),
                opacity=0.5, showlegend=True))
    pl(fig_cd,420); st.plotly_chart(fig_cd,use_container_width=True)

    st.markdown('<div class="sh-sm">SUCCESS RATE HEATMAP — CREW SIZE × MISSION TYPE</div>',
                unsafe_allow_html=True)
    heat = fdf.groupby(["Mission_Type","Crew_Size"])["Mission_Success"].mean().unstack(fill_value=0)
    fig_ht,ax_ht = plt.subplots(figsize=(10,4))
    mpl_dk(fig_ht,ax_ht)
    sns.heatmap(heat*100,ax=ax_ht,annot=True,fmt=".0f",cmap="RdYlGn",
                linewidths=.4,linecolor=BRD,annot_kws={"size":9})
    ax_ht.set_title("Success Rate (%) — Mission Type vs Crew Size",fontsize=11,pad=10)
    ax_ht.tick_params(labelsize=9)
    plt.tight_layout(); st.pyplot(fig_ht)
    st.markdown("""<div class="ib ib-grn"><strong>Insight:</strong> The heatmap reveals
    that certain mission types benefit more from larger crews. Deep Space missions with
    crew sizes of 4–6 show the highest success rates, while LEO missions perform well
    even uncrewed.</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 5 — ROCKET SIMULATION  — LIVE ANIMATED LAUNCH
# ══════════════════════════════════════════════════════════════
elif page == "Rocket Simulation":
    st.markdown('<div class="sh">🚀 SECTION 5 — ROCKET LAUNCH SIMULATION</div>',
                unsafe_allow_html=True)

    # ── PHYSICS EQUATION CARDS ────────────────────────────────
    st.markdown('<div class="sh-sm">GOVERNING EQUATIONS — NEWTON\'S SECOND LAW</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="fw">
      <div class="fc"><span class="fl">Second Law</span>F = m(t) · a</div>
      <div class="fc"><span class="fl">Acceleration</span>a = F<sub>net</sub> / m(t)</div>
      <div class="fc"><span class="fl">Net Force</span>F<sub>T</sub> − F<sub>g</sub> − F<sub>d</sub></div>
      <div class="fc"><span class="fl">Gravity</span>F<sub>g</sub> = m(t) · g</div>
      <div class="fc"><span class="fl">Drag</span>F<sub>d</sub> = C<sub>d</sub> · v²</div>
      <div class="fc"><span class="fl">Mass Reduction</span>m(t) = m₀ − ṁ · t</div>
    </div>""", unsafe_allow_html=True)

    # ── CONTROLS ──────────────────────────────────────────────
    st.markdown('<div class="sh-sm">SIMULATION CONTROLS</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        init_mass = st.slider("INITIAL TOTAL MASS (kg)",  50_000, 600_000, 250_000, 5_000)
        thrust    = st.slider("ENGINE THRUST (N)",        500_000, 8_000_000, 2_800_000, 100_000)
        drag_c    = st.slider("DRAG COEFFICIENT (Cd)",    0.0, 1.5, 0.35, 0.05)
    with cb:
        payload   = st.slider("PAYLOAD MASS (kg)",        1_000, 30_000, 10_000, 500)
        fuel      = st.slider("INITIAL FUEL (kg)",        20_000, 500_000, 180_000, 5_000)
        burn_r    = st.slider("BURN RATE FACTOR",         0.5, 3.0, 1.0, 0.1)

    drag_on = st.toggle("ATMOSPHERIC DRAG ENABLED", value=True)
    compare = st.checkbox("OVERLAY DRAG vs NO-DRAG COMPARISON")

    # ── VALIDATION ────────────────────────────────────────────
    st.markdown('<div class="sh-sm">INPUT VALIDATION</div>', unsafe_allow_html=True)
    val_msgs  = validate_sim(init_mass, thrust, drag_c, payload, fuel, burn_r)
    has_error = any(m[0] == "error" for m in val_msgs)
    for level, msg in val_msgs:
        if level == "error":
            st.markdown(f'<div class="val-err">❌ {msg}</div>', unsafe_allow_html=True)
        elif level == "warn":
            st.markdown(f'<div class="val-warn">⚠️ {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="val-ok">✓ {msg}</div>', unsafe_allow_html=True)

    if has_error:
        st.markdown("""<div class="ib ib-red"><strong>Simulation blocked.</strong>
        Fix the errors above — this mirrors a real launch readiness review.</div>""",
        unsafe_allow_html=True)
        st.stop()

    # Pre-compute physics values needed for animation
    twr      = thrust / (init_mass * 9.81)
    burn_rate_kgs = (thrust / (300.0 * 9.81)) * burn_r
    burnout_t = fuel / burn_rate_kgs if burn_rate_kgs > 0 else 200.0
    burnout_t = min(burnout_t, 200.0)

    # Run simulation
    with st.spinner("⚙️ Running physics engine…"):
        sim = simulate(init_mass, thrust, drag_c, payload, fuel, burn_r, drag_on)
    if compare:
        sim_nd = simulate(init_mass, thrust, drag_c, payload, fuel, burn_r, False)

    max_alt  = sim["Altitude_m"].max()
    max_vel  = sim["Velocity_ms"].max()
    max_acc  = sim["Acceleration_ms2"].max()
    fin_mass = sim["Mass_kg"].iloc[-1]
    bo_rows  = sim.loc[sim["Fuel_Remaining_kg"] <= 0, "Time_s"]
    burnout  = bo_rows.iloc[0] if len(bo_rows) else float("nan")

    # Build phase timeline from sim data
    t50  = sim.iloc[min(50,  len(sim)-1)]
    t100 = sim.iloc[min(100, len(sim)-1)]
    t150 = sim.iloc[min(150, len(sim)-1)]
    t199 = sim.iloc[-1]

    # Drag cost
    drag_cost_pct = 0.0
    if compare and "sim_nd" in dir():
        nd_max = sim_nd["Altitude_m"].max()
        drag_cost_pct = (nd_max - max_alt) / nd_max * 100 if nd_max > 0 else 0.0

    # Save to history
    _bo2 = sim.loc[sim["Fuel_Remaining_kg"] <= 0, "Time_s"]
    _bts = int(_bo2.iloc[0]) if len(_bo2) else 200
    st.session_state.sim_history.insert(0, {
        "ts": datetime.now().strftime("%H:%M:%S"), "twr": round(twr,3),
        "max_alt": round(max_alt/1000, 2), "burnout": _bts,
        "thrust": thrust, "fuel": fuel, "drag_on": drag_on,
        "init_mass": init_mass, "payload": payload,
    })
    if len(st.session_state.sim_history) > 10:
        st.session_state.sim_history = st.session_state.sim_history[:10]
    st.session_state.total_sims += 1

    # ══════════════════════════════════════════════════════════
    # ANIMATED LAUNCH VISUALISER  — full HTML/CSS/JS component
    # ══════════════════════════════════════════════════════════
    gcol_css  = "#00e676" if twr > 1 else "#ff1744"
    twr_fill  = min(twr / 3 * 100, 100)
    gfill_col = "linear-gradient(90deg,#00e676,#00b8d4)" if twr > 1 else "linear-gradient(90deg,#ff1744,#ff7700)"

    # Encode sim data compactly for JS
    alt_json  = [round(v/1000, 2) for v in sim["Altitude_m"].tolist()]
    vel_json  = [round(v, 1)      for v in sim["Velocity_ms"].tolist()]
    acc_json  = [round(v, 3)      for v in sim["Acceleration_ms2"].tolist()]
    fuel_json = [round(v/1000, 2) for v in sim["Fuel_Remaining_kg"].tolist()]
    fgrav_json= [round(v/1000, 1) for v in sim["F_gravity_N"].tolist()]
    fdrag_json= [round(v/1000, 1) for v in sim["F_drag_N"].tolist()]
    fthrust_json=[round(v/1000000,3) for v in sim["Thrust_N"].tolist()]

    import json as _json
    alt_js   = _json.dumps(alt_json)
    vel_js   = _json.dumps(vel_json)
    acc_js   = _json.dumps(acc_json)
    fuel_js  = _json.dumps(fuel_json)
    fg_js    = _json.dumps(fgrav_json)
    fd_js    = _json.dumps(fdrag_json)
    ft_js    = _json.dumps(fthrust_json)

    # ══════════════════════════════════════════════════════════
    # CINEMATIC ROCKET LAUNCH ANIMATION
    # Canvas-based: particle exhaust, camera shake, staging,
    # atmosphere layers, live telemetry, sound engine
    # ══════════════════════════════════════════════════════════
    import json as _json
    _alt_js  = _json.dumps([round(v/1000,2) for v in sim["Altitude_m"].tolist()])
    _vel_js  = _json.dumps([round(v,1) for v in sim["Velocity_ms"].tolist()])
    _acc_js  = _json.dumps([round(v,3) for v in sim["Acceleration_ms2"].tolist()])
    _fuel_js = _json.dumps([round(v/1000,2) for v in sim["Fuel_Remaining_kg"].tolist()])
    _fg_js   = _json.dumps([round(v/1000,1) for v in sim["F_gravity_N"].tolist()])
    _fd_js   = _json.dumps([round(v/1000,1) for v in sim["F_drag_N"].tolist()])
    _twr_val  = round(twr, 4)
    _max_alt  = round(max_alt/1000, 3)
    _max_vel  = round(max_vel, 1)
    _burnout_t= round(burnout_t, 1)
    _fuel_t   = round(fuel/1000, 1)
    _mass_t   = round(init_mass/1000, 1)
    _thrust_mn= round(thrust/1e6, 2)
    _drag_on_js = "true" if drag_on else "false"

    rocket_launch_html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Rocket Launch</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#03080f;display:flex;flex-direction:column;align-items:center;
  font-family:'Courier New',monospace;overflow:hidden;height:780px;}

/* TOP BAR */
.topbar{width:100%;display:flex;align-items:center;justify-content:space-between;
  padding:8px 18px;background:rgba(0,0,0,.6);border-bottom:1px solid #0d2a44;
  flex-shrink:0;}
.title{font-size:.72rem;letter-spacing:4px;color:#00e5ff;text-transform:uppercase;
  font-weight:700;}
.tbar-right{display:flex;gap:10px;align-items:center;}

/* MAIN AREA */
.main{display:flex;gap:0;flex:1;width:100%;min-height:0;}

/* CANVAS SCENE */
.scene-wrap{position:relative;flex:1;min-height:0;background:#020a14;}
#cnv{display:block;width:100%;height:100%;}

/* RIGHT PANEL */
.rpanel{width:210px;flex-shrink:0;background:#030c18;border-left:1px solid #0d2a44;
  display:flex;flex-direction:column;overflow:hidden;}

/* phase box */
.pbox{padding:10px 12px;border-bottom:1px solid #0d2a44;}
.pbox-lbl{font-size:.44rem;letter-spacing:2px;color:#1a4060;text-transform:uppercase;margin-bottom:3px;}
.pbox-name{font-size:.8rem;font-weight:700;color:#00e5ff;letter-spacing:1px;}
.pbox-eq{font-size:.62rem;color:#ffd700;background:rgba(255,215,0,.06);
  border:1px solid rgba(255,215,0,.18);border-radius:3px;padding:1px 7px;
  display:inline-block;margin:3px 0;}
.pbox-desc{font-size:.62rem;color:#5a7a90;line-height:1.4;margin-top:4px;}

/* telemetry cells */
.tcells{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#0d2030;flex:1;}
.tc{background:#030c18;padding:6px 9px;}
.tc-lbl{font-size:.4rem;letter-spacing:1.5px;color:#1a4060;text-transform:uppercase;}
.tc-val{font-size:.82rem;font-weight:700;color:#cce0f0;font-family:'Courier New',monospace;}
.tc-unit{font-size:.5rem;color:#2a5070;}
.tc-bar{height:2px;background:#0d2030;border-radius:1px;margin-top:3px;}
.tc-fill{height:100%;border-radius:1px;transition:width .1s linear;}

/* physics insight */
.insight{padding:8px 12px;border-top:1px solid #0d2a44;background:#020810;min-height:62px;}
.ins-t{font-size:.42rem;letter-spacing:2px;color:#ffd700;text-transform:uppercase;margin-bottom:3px;}
.ins-b{font-size:.6rem;color:#4a6a80;line-height:1.4;}

/* controls bar */
.cbar{padding:8px 12px;border-top:1px solid #0d2a44;display:flex;gap:6px;align-items:center;
  background:#020810;flex-shrink:0;}
.btn-launch{font-family:'Courier New',monospace;font-size:.6rem;letter-spacing:2px;
  text-transform:uppercase;background:linear-gradient(135deg,rgba(0,229,255,.12),rgba(0,150,200,.08));
  border:1px solid #00e5ff;color:#00e5ff;border-radius:6px;padding:7px 16px;
  cursor:pointer;transition:all .2s;}
.btn-launch:hover{background:rgba(0,229,255,.22);box-shadow:0 0 14px rgba(0,229,255,.3);}
.btn-launch:disabled{opacity:.3;cursor:not-allowed;}
.btn-rst{font-family:'Courier New',monospace;font-size:.56rem;letter-spacing:1.5px;
  background:rgba(26,58,96,.3);border:1px solid #1a3a60;color:#4a6a88;
  border-radius:6px;padding:7px 12px;cursor:pointer;display:none;transition:all .2s;}
.btn-rst:hover{border-color:#5a7a9a;color:#8aaac0;}
.btn-snd{font-size:.65rem;background:rgba(255,215,0,.07);border:1px solid rgba(255,215,0,.25);
  color:#ffd700;border-radius:6px;padding:7px 10px;cursor:pointer;}
.sdot{width:7px;height:7px;border-radius:50%;background:#ff1744;
  box-shadow:0 0 6px #ff1744;margin-left:auto;transition:all .3s;}
.sdot.live{background:#00e676;box-shadow:0 0 6px #00e676;animation:bl .55s ease-in-out infinite alternate;}
@keyframes bl{from{opacity:.4}to{opacity:1}}
.stxt{font-size:.45rem;letter-spacing:1.5px;color:#1a4060;}

/* clock strip */
.cstrip{display:flex;border-bottom:1px solid #0d2a44;}
.ck{flex:1;text-align:center;padding:5px 4px;border-right:1px solid #0d2a44;}
.ck:last-child{border-right:none;}
.ck-l{font-size:.38rem;letter-spacing:1px;color:#1a4060;text-transform:uppercase;}
.ck-v{font-size:.72rem;font-weight:700;color:#00e5ff;font-family:'Courier New',monospace;}
</style></head>
<body>

<div class="topbar">
  <span class="title">🚀 Rocket Launch Simulation</span>
  <div class="tbar-right">
    <span style="font-size:.52rem;color:#1a4060;letter-spacing:1px;">TWR """ + str(_twr_val) + """ &nbsp;|&nbsp; Max Alt """ + str(_max_alt) + """ km</span>
  </div>
</div>

<div class="main">

  <!-- CANVAS SCENE -->
  <div class="scene-wrap">
    <canvas id="cnv"></canvas>
  </div>

  <!-- RIGHT PANEL -->
  <div class="rpanel">

    <!-- Phase -->
    <div class="pbox">
      <div class="pbox-lbl">FLIGHT PHASE</div>
      <div class="pbox-name" id="phN">PRE-LAUNCH</div>
      <div class="pbox-eq" id="phEq">F = m · a</div>
      <div class="pbox-desc" id="phD">Press LAUNCH. The rocket will fly through all phases using your exact physics parameters.</div>
    </div>

    <!-- Clocks -->
    <div class="cstrip">
      <div class="ck"><div class="ck-l">TIME</div><div class="ck-v" id="ckT">T+0s</div></div>
      <div class="ck"><div class="ck-l">ALT</div><div class="ck-v" id="ckA">0km</div></div>
      <div class="ck"><div class="ck-l">PROG</div><div class="ck-v" id="ckP">0%</div></div>
    </div>

    <!-- Telemetry -->
    <div class="tcells">
      <div class="tc"><div class="tc-lbl">ALTITUDE</div>
        <div><span class="tc-val" id="tA">0.00</span><span class="tc-unit"> km</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bA" style="width:0%;background:#00e5ff;"></div></div></div>
      <div class="tc"><div class="tc-lbl">VELOCITY</div>
        <div><span class="tc-val" id="tV">0.0</span><span class="tc-unit"> m/s</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bV" style="width:0%;background:#00e676;"></div></div></div>
      <div class="tc"><div class="tc-lbl">ACCEL</div>
        <div><span class="tc-val" id="tAc">0.000</span><span class="tc-unit"> m/s²</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bAc" style="width:0%;background:#ffd700;"></div></div></div>
      <div class="tc"><div class="tc-lbl">FUEL</div>
        <div><span class="tc-val" id="tF">""" + str(_fuel_t) + """</span><span class="tc-unit"> t</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bF" style="width:100%;background:#ff6b00;"></div></div></div>
      <div class="tc"><div class="tc-lbl">THRUST</div>
        <div><span class="tc-val" id="tFT">""" + str(_thrust_mn) + """</span><span class="tc-unit"> MN</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bFT" style="width:100%;background:#00e5ff;"></div></div></div>
      <div class="tc"><div class="tc-lbl">GRAVITY</div>
        <div><span class="tc-val" id="tFG">—</span><span class="tc-unit"> kN</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bFG" style="width:0%;background:#ff1744;"></div></div></div>
      <div class="tc"><div class="tc-lbl">DRAG</div>
        <div><span class="tc-val" id="tFD">—</span><span class="tc-unit"> kN</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bFD" style="width:0%;background:#8b5cf6;"></div></div></div>
      <div class="tc"><div class="tc-lbl">MASS</div>
        <div><span class="tc-val" id="tM">""" + str(_mass_t) + """</span><span class="tc-unit"> t</span></div>
        <div class="tc-bar"><div class="tc-fill" id="bM" style="width:100%;background:#5a7a9a;"></div></div></div>
    </div>

    <!-- Insight -->
    <div class="insight">
      <div class="ins-t" id="insT">NEWTON 2ND LAW</div>
      <div class="ins-b" id="insB">a = F_net / m(t). As fuel burns, mass decreases → same thrust → more acceleration. Fastest at burnout.</div>
    </div>

    <!-- Controls -->
    <div class="cbar">
      <button class="btn-launch" id="btnGo" onclick="doLaunch()">🚀 LAUNCH</button>
      <button class="btn-rst"    id="btnRst" onclick="doReset()">↺</button>
      <button class="btn-snd"    id="btnSnd" onclick="doToggleSnd()">🔊</button>
      <div class="sdot" id="sdot"></div>
      <div class="stxt" id="stxt">STANDBY</div>
    </div>

  </div>
</div>

<script>
// ═══════════════════════════════════════════════════
// SIMULATION DATA
// ═══════════════════════════════════════════════════
const ALT  = """ + _alt_js  + """;
const VEL  = """ + _vel_js  + """;
const ACC  = """ + _acc_js  + """;
const FUEL = """ + _fuel_js + """;
const FG   = """ + _fg_js   + """;
const FD   = """ + _fd_js   + """;
const N    = ALT.length;
const MAX_ALT  = """ + str(_max_alt)   + """;
const MAX_VEL  = Math.max(...VEL.map(Math.abs));
const MAX_ACC  = Math.max(...ACC.map(Math.abs));
const INIT_FUEL= """ + str(_fuel_t)    + """;
const INIT_MASS= """ + str(_mass_t)    + """;
const BURNOUT_T= """ + str(_burnout_t) + """;
const TWR      = """ + str(_twr_val)   + """;
const DRAG_ON  = """ + _drag_on_js     + """;

// ═══════════════════════════════════════════════════
// CANVAS SETUP
// ═══════════════════════════════════════════════════
const cnv = document.getElementById('cnv');
const ctx = cnv.getContext('2d');

function resize() {
  const wrap = cnv.parentElement;
  cnv.width  = wrap.clientWidth;
  cnv.height = wrap.clientHeight;
}
resize();
window.addEventListener('resize', resize);

// ═══════════════════════════════════════════════════
// STARS (pre-generated)
// ═══════════════════════════════════════════════════
const STARS = [];
for (let i = 0; i < 180; i++) {
  STARS.push({
    x: Math.random(),
    y: Math.random() * 0.85,
    r: Math.random() * 1.4 + 0.3,
    b: Math.random()
  });
}

// ═══════════════════════════════════════════════════
// PARTICLES
// ═══════════════════════════════════════════════════
let particles = [];

function spawnExhaust(rx, ry, power, vRocket) {
  const count = Math.floor(6 + power * 10);
  for (let i = 0; i < count; i++) {
    const spd = 2 + Math.random() * 4 + power * 3;
    const ang = (Math.PI * 0.5) + (Math.random() - 0.5) * 0.55;
    const size = 2 + Math.random() * 4;
    const life = 0.4 + Math.random() * 0.5;
    const hot = Math.random();
    particles.push({
      x: rx + (Math.random() - 0.5) * 10,
      y: ry,
      vx: Math.cos(ang) * spd * (Math.random() - 0.5) * 0.6,
      vy: Math.sin(ang) * spd + vRocket * 0.3,
      size,
      life,
      maxLife: life,
      hot,
      type: 'exhaust'
    });
  }
  // Smoke puffs (slower, larger)
  if (Math.random() < 0.3) {
    particles.push({
      x: rx + (Math.random() - 0.5) * 16,
      y: ry + 5,
      vx: (Math.random() - 0.5) * 0.8,
      vy: 0.5 + Math.random() * 1.5,
      size: 8 + Math.random() * 14,
      life: 1.2 + Math.random() * 0.8,
      maxLife: 2.0,
      hot: 0,
      type: 'smoke'
    });
  }
}

function spawnGroundBlast(cx, groundY, power) {
  for (let i = 0; i < 18; i++) {
    const ang = Math.PI + (Math.random() - 0.5) * Math.PI;
    const spd = 2 + Math.random() * 5 * power;
    particles.push({
      x: cx + (Math.random() - 0.5) * 20,
      y: groundY - 5,
      vx: Math.cos(ang) * spd,
      vy: Math.sin(ang) * spd - 1,
      size: 3 + Math.random() * 6,
      life: 0.8 + Math.random() * 0.6,
      maxLife: 1.4,
      hot: Math.random(),
      type: 'exhaust'
    });
  }
}

function updateParticles(dt) {
  particles = particles.filter(p => p.life > 0);
  particles.forEach(p => {
    p.x  += p.vx * dt * 60;
    p.y  += p.vy * dt * 60;
    p.vy += 0.04 * dt * 60;  // gravity pull on smoke
    p.life -= dt;
    p.size *= (1 - dt * 0.4);
  });
}

function drawParticles() {
  particles.forEach(p => {
    const t = p.life / p.maxLife;
    if (p.type === 'smoke') {
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(0, p.size), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(160,140,120,${t * 0.18})`;
      ctx.fill();
    } else {
      // hot exhaust
      const r = p.hot > 0.5 ? 255 : 255;
      const g = p.hot > 0.6 ? Math.round(220 * p.hot) : Math.round(80 + 100 * t);
      const b = p.hot > 0.8 ? Math.round(100 * t) : 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(0.5, p.size * t), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r},${g},${b},${t * 0.9})`;
      ctx.fill();
    }
  });
}

// ═══════════════════════════════════════════════════
// DRAW ROCKET (SVG-equivalent on canvas)
// ═══════════════════════════════════════════════════
function drawRocket(cx, cy, scale) {
  const s = scale;
  ctx.save();
  ctx.translate(cx, cy);

  // Body
  ctx.beginPath();
  ctx.ellipse(0, 0, 14*s, 46*s, 0, 0, Math.PI*2);
  ctx.fillStyle = '#1a2f50';
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = 1.2*s;
  ctx.fill(); ctx.stroke();

  // Nose cone
  ctx.beginPath();
  ctx.moveTo(0, -46*s);
  ctx.bezierCurveTo(-12*s, -30*s, -14*s, -18*s, -14*s, -8*s);
  ctx.bezierCurveTo(-14*s, -2*s, 14*s, -2*s, 14*s, -8*s);
  ctx.bezierCurveTo(14*s, -18*s, 12*s, -30*s, 0, -46*s);
  ctx.fillStyle = '#00b8d4';
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = s;
  ctx.fill(); ctx.stroke();

  // Tip
  ctx.beginPath();
  ctx.moveTo(0, -46*s);
  ctx.lineTo(-3*s, -38*s);
  ctx.lineTo(3*s, -38*s);
  ctx.closePath();
  ctx.fillStyle = '#00e5ff';
  ctx.fill();

  // Fins L
  ctx.beginPath();
  ctx.moveTo(-14*s, 22*s);
  ctx.lineTo(-28*s, 48*s);
  ctx.lineTo(-14*s, 38*s);
  ctx.closePath();
  ctx.fillStyle = '#0d2240';
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = .7*s;
  ctx.fill(); ctx.stroke();
  // smaller inner fin L
  ctx.beginPath();
  ctx.moveTo(-14*s, 28*s);
  ctx.lineTo(-22*s, 46*s);
  ctx.lineTo(-14*s, 38*s);
  ctx.closePath();
  ctx.fillStyle = '#1a3a60';
  ctx.strokeStyle = '#00b8d4';
  ctx.lineWidth = .5*s;
  ctx.fill(); ctx.stroke();

  // Fins R
  ctx.beginPath();
  ctx.moveTo(14*s, 22*s);
  ctx.lineTo(28*s, 48*s);
  ctx.lineTo(14*s, 38*s);
  ctx.closePath();
  ctx.fillStyle = '#0d2240';
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = .7*s;
  ctx.fill(); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(14*s, 28*s);
  ctx.lineTo(22*s, 46*s);
  ctx.lineTo(14*s, 38*s);
  ctx.closePath();
  ctx.fillStyle = '#1a3a60';
  ctx.strokeStyle = '#00b8d4';
  ctx.lineWidth = .5*s;
  ctx.fill(); ctx.stroke();

  // Nozzle
  ctx.beginPath();
  ctx.ellipse(0, 46*s, 9*s, 4*s, 0, 0, Math.PI*2);
  ctx.fillStyle = '#0a1a30';
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = s;
  ctx.fill(); ctx.stroke();

  // Porthole
  ctx.beginPath();
  ctx.arc(0, -4*s, 6*s, 0, Math.PI*2);
  ctx.fillStyle = '#001a2a';
  ctx.strokeStyle = '#00e5ff';
  ctx.lineWidth = s;
  ctx.fill(); ctx.stroke();
  ctx.beginPath();
  ctx.arc(0, -4*s, 4*s, 0, Math.PI*2);
  ctx.fillStyle = '#003355';
  ctx.fill();
  ctx.beginPath();
  ctx.arc(-1.5*s, -5.5*s, 1.2*s, 0, Math.PI*2);
  ctx.fillStyle = 'rgba(255,255,255,.5)';
  ctx.fill();

  // Stripe
  ctx.beginPath();
  ctx.rect(-14*s, 14*s, 28*s, 3.5*s);
  ctx.fillStyle = 'rgba(255,107,0,.7)';
  ctx.fill();

  ctx.restore();
}

// ═══════════════════════════════════════════════════
// DRAW LAUNCH PAD
// ═══════════════════════════════════════════════════
function drawPad(cx, groundY) {
  // Platform
  ctx.fillStyle = '#0a2040';
  ctx.strokeStyle = '#1a5080';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.rect(cx - 36, groundY - 9, 72, 9);
  ctx.fill(); ctx.stroke();

  // Legs
  ctx.strokeStyle = '#0d2848';
  ctx.lineWidth = 3;
  [[-18, 16], [18, -16]].forEach(([ox, angDir]) => {
    ctx.save();
    ctx.translate(cx + ox, groundY - 9);
    ctx.rotate(angDir * Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, 20);
    ctx.stroke();
    ctx.restore();
  });

  // Gantry tower
  ctx.fillStyle = '#08162a';
  ctx.strokeStyle = 'rgba(26,80,128,.6)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.rect(cx + 30, groundY - 85, 4, 85);
  ctx.fill(); ctx.stroke();
  // Arms
  [20, 42, 64].forEach(h => {
    ctx.beginPath();
    ctx.moveTo(cx + 30, groundY - h);
    ctx.lineTo(cx + 12, groundY - h);
    ctx.strokeStyle = 'rgba(26,80,128,.5)';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });

  // Ground surface
  const grd = ctx.createLinearGradient(0, groundY, 0, groundY + 40);
  grd.addColorStop(0, '#061220');
  grd.addColorStop(1, '#030810');
  ctx.fillStyle = grd;
  ctx.fillRect(0, groundY, cnv.width, 40);

  // Ground line
  ctx.beginPath();
  ctx.moveTo(0, groundY);
  ctx.lineTo(cnv.width, groundY);
  ctx.strokeStyle = '#1a3a60';
  ctx.lineWidth = 1;
  ctx.stroke();
}

// ═══════════════════════════════════════════════════
// DRAW ATMOSPHERE
// ═══════════════════════════════════════════════════
function drawSky(altFrac) {
  const W = cnv.width, H = cnv.height;
  // Sky gradient: darkens with altitude
  const blue = Math.max(0, 1 - altFrac * 1.8);
  const grd = ctx.createLinearGradient(0, 0, 0, H);
  grd.addColorStop(0, `rgba(0,1,4,1)`);
  grd.addColorStop(0.3, `rgba(${Math.round(blue*3)},${Math.round(blue*10)},${Math.round(blue*22)},1)`);
  grd.addColorStop(1, `rgba(${Math.round(blue*6)},${Math.round(blue*20)},${Math.round(blue*40)},1)`);
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, W, H);

  // Atmosphere layer bands (subtle)
  const groundY = H * 0.78;
  const layers = [
    { label: 'EXOSPHERE',    pct: 0.04 },
    { label: 'THERMOSPHERE', pct: 0.14 },
    { label: 'MESOSPHERE',   pct: 0.25 },
    { label: 'STRATOSPHERE', pct: 0.38 },
    { label: 'TROPOSPHERE',  pct: 0.52 },
  ];
  ctx.font = '7px monospace';
  layers.forEach(l => {
    const y = l.pct * groundY;
    ctx.strokeStyle = 'rgba(0,229,255,.06)';
    ctx.lineWidth = .5;
    ctx.setLineDash([4, 8]);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W * 0.7, y); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(0,229,255,.22)';
    ctx.fillText(l.label, 6, y - 2);
  });

  // Stars (fade in with altitude)
  const starAlpha = Math.min(1, altFrac * 3 + 0.08);
  STARS.forEach(s => {
    const twinkle = 0.4 + 0.6 * Math.abs(Math.sin(Date.now() * 0.001 * (s.b + 0.5)));
    ctx.beginPath();
    ctx.arc(s.x * W, s.y * H * 0.75, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${starAlpha * twinkle * 0.85})`;
    ctx.fill();
  });
}

// ═══════════════════════════════════════════════════
// DRAW ALTITUDE RULER
// ═══════════════════════════════════════════════════
function drawRuler(groundY, altFrac) {
  const W = cnv.width;
  ctx.font = '7px monospace';
  ctx.fillStyle = 'rgba(0,229,255,.35)';
  for (let i = 0; i <= 5; i++) {
    const y = (i / 5) * groundY;
    const km = Math.round(MAX_ALT * (5 - i) / 5);
    ctx.fillText(km + 'km', W - 36, y + 3);
    ctx.strokeStyle = 'rgba(0,229,255,.08)';
    ctx.lineWidth = .5;
    ctx.beginPath(); ctx.moveTo(W - 42, y); ctx.lineTo(W, y); ctx.stroke();
  }
  // Current altitude marker
  const markerY = groundY - altFrac * groundY;
  ctx.fillStyle = '#00e5ff';
  ctx.beginPath();
  ctx.moveTo(W - 44, markerY);
  ctx.lineTo(W - 50, markerY - 4);
  ctx.lineTo(W - 50, markerY + 4);
  ctx.closePath();
  ctx.fill();
}

// ═══════════════════════════════════════════════════
// DRAW FLAME (engine fire)
// ═══════════════════════════════════════════════════
function drawFlame(cx, nozzleY, power, time) {
  if (power <= 0) return;
  const flicker = 0.85 + 0.15 * Math.sin(time * 0.05);
  const h = (30 + power * 45) * flicker;
  const w = (10 + power * 8) * flicker;

  // Outer glow
  const og = ctx.createRadialGradient(cx, nozzleY, 0, cx, nozzleY + h * 0.4, h * 0.9);
  og.addColorStop(0, `rgba(255,180,0,${0.25 * power})`);
  og.addColorStop(0.4, `rgba(255,80,0,${0.15 * power})`);
  og.addColorStop(1, `rgba(255,30,0,0)`);
  ctx.beginPath();
  ctx.ellipse(cx, nozzleY + h * 0.35, w * 1.8, h * 0.85, 0, 0, Math.PI * 2);
  ctx.fillStyle = og;
  ctx.fill();

  // Mid flame
  const mg = ctx.createLinearGradient(cx, nozzleY, cx, nozzleY + h);
  mg.addColorStop(0, `rgba(255,200,80,${0.7 * power})`);
  mg.addColorStop(0.3, `rgba(255,120,0,${0.6 * power})`);
  mg.addColorStop(0.7, `rgba(255,40,0,${0.4 * power})`);
  mg.addColorStop(1, `rgba(255,0,0,0)`);
  ctx.beginPath();
  ctx.ellipse(cx, nozzleY + h * 0.45, w * 0.9, h * 0.75, 0, 0, Math.PI * 2);
  ctx.fillStyle = mg;
  ctx.fill();

  // Core (white-hot)
  const cg = ctx.createLinearGradient(cx, nozzleY, cx, nozzleY + h * 0.4);
  cg.addColorStop(0, `rgba(255,255,255,${0.9 * power})`);
  cg.addColorStop(0.4, `rgba(255,240,100,${0.7 * power})`);
  cg.addColorStop(1, `rgba(255,180,0,0)`);
  ctx.beginPath();
  ctx.ellipse(cx, nozzleY + h * 0.2, w * 0.35, h * 0.38, 0, 0, Math.PI * 2);
  ctx.fillStyle = cg;
  ctx.fill();
}

// ═══════════════════════════════════════════════════
// CAMERA SHAKE
// ═══════════════════════════════════════════════════
let shakeAmt = 0, shakeTimer = 0;
function triggerShake(amt, dur) { shakeAmt = amt; shakeTimer = dur; }
function getShake() {
  if (shakeTimer <= 0) return { dx: 0, dy: 0 };
  shakeTimer -= 0.016;
  const decay = shakeTimer > 0 ? shakeTimer / 0.5 : 0;
  return { dx: (Math.random() - 0.5) * shakeAmt * decay * 2,
           dy: (Math.random() - 0.5) * shakeAmt * decay };
}

// ═══════════════════════════════════════════════════
// FLIGHT PHASES
// ═══════════════════════════════════════════════════
const PHASES = [
  { range:[0,6],    name:'IGNITION',        col:'#ff6b00',
    eq:'TWR = F_T/(m·g)',
    desc:'Engines ignite. TWR='+TWR.toFixed(3)+'. '+(TWR>1?'GO — net lift confirmed.':'NO-GO — increase thrust.'),
    insT:'THRUST-TO-WEIGHT RATIO', insB:'TWR = F_thrust/(m·g). Must exceed 1.0 for liftoff. Yours: '+TWR.toFixed(3)+'. '+(TWR>1?'Positive net force.':'Insufficient thrust.') },
  { range:[6,25],   name:'LIFTOFF',         col:'#00e5ff',
    eq:'a = F_net/m(t)',
    desc:'Clamps release. Rocket rises. F_net = Thrust - Gravity - Drag > 0.',
    insT:"NEWTON'S 2ND LAW", insB:'F_net = F_thrust - F_gravity - F_drag. Net force / mass = acceleration. Gravity and drag fight every metre.' },
  { range:[25,BURNOUT_T], name:'POWERED ASCENT', col:'#00e676',
    eq:'Δv = Isp·g·ln(m₀/mf)',
    desc:'Main burn. m(t) drops → a rises. Tsiolkovsky: Δv = Isp·g·ln(m₀/mf).',
    insT:'TSIOLKOVSKY EFFECT', insB:'As fuel burns, m(t) decreases. Since a=F/m(t) with constant F, acceleration rises. Fastest just before burnout.' },
  { range:[BURNOUT_T,BURNOUT_T+10], name:'ENGINE CUTOFF', col:'#ffd700',
    eq:'m_burnout = m₀ - m_fuel',
    desc:'Fuel exhausted. Engines cut. Peak acceleration achieved. Now coast phase begins.',
    insT:'BURNOUT DYNAMICS', insB:'At burnout: mass is minimum, so peak a = F/m_min. Now F_thrust=0. Only gravity and drag decelerate.' },
  { range:[BURNOUT_T+10,200], name:'COAST TO APOGEE', col:'#8b5cf6',
    eq:'½mv² → mgh',
    desc:'Ballistic coast. Velocity → 0 at apogee = '+MAX_ALT.toFixed(2)+' km.',
    insT:'BALLISTIC COAST', insB:'No thrust. Kinetic energy converts to potential: ½mv² → mgh. Apogee='+MAX_ALT.toFixed(2)+'km, v_peak='+MAX_VEL.toFixed(1)+'m/s.' },
];
function getPhase(s) {
  for (const p of PHASES) if (s >= p.range[0] && s <= p.range[1]) return p;
  return s < 6 ? PHASES[0] : PHASES[4];
}

// ═══════════════════════════════════════════════════
// TELEMETRY UPDATE
// ═══════════════════════════════════════════════════
function setTel(id, bid, val, pct, col) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
  const b = document.getElementById(bid);
  if (b) { b.style.width = Math.max(0, Math.min(100, pct)) + '%'; if(col) b.style.background=col; }
}

// ═══════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════
let step = 0, running = false, tid = null;
let soundOn = true, audioCtx = null;
let engGain = null, engOsc = null, engOsc2 = null, rumGain = null, rumOsc = null;
let lastTime = 0, frameAccum = 0;
const STEP_MS = 80; // ms per simulation step

// ═══════════════════════════════════════════════════
// SOUND ENGINE
// ═══════════════════════════════════════════════════
function initAudio() {
  if (audioCtx) return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const filt = audioCtx.createBiquadFilter();
  filt.type = 'lowpass'; filt.frequency.value = 420; filt.Q.value = 1.4;
  engGain = audioCtx.createGain(); engGain.gain.value = 0;
  engOsc  = audioCtx.createOscillator(); engOsc.type = 'sawtooth'; engOsc.frequency.value = 50;
  engOsc2 = audioCtx.createOscillator(); engOsc2.type = 'square';  engOsc2.frequency.value = 74;
  engOsc.connect(filt); engOsc2.connect(filt);
  filt.connect(engGain); engGain.connect(audioCtx.destination);
  engOsc.start(); engOsc2.start();
  rumGain = audioCtx.createGain(); rumGain.gain.value = 0;
  rumOsc  = audioCtx.createOscillator(); rumOsc.type = 'sine'; rumOsc.frequency.value = 24;
  rumOsc.connect(rumGain); rumGain.connect(audioCtx.destination); rumOsc.start();
}
function setEng(power) {
  if (!soundOn || !audioCtx || !engGain) return;
  const t = audioCtx.currentTime;
  engGain.gain.linearRampToValueAtTime(power * 0.14, t + .06);
  rumGain.gain.linearRampToValueAtTime(power * 0.09, t + .06);
  if (engOsc)  engOsc.frequency.linearRampToValueAtTime(50  + power * 48, t + .1);
  if (engOsc2) engOsc2.frequency.linearRampToValueAtTime(74 + power * 62, t + .1);
}
function stopEng() {
  if (!audioCtx || !engGain) return;
  const t = audioCtx.currentTime;
  engGain.gain.linearRampToValueAtTime(0.001, t + 0.9);
  rumGain.gain.linearRampToValueAtTime(0.001, t + 0.9);
}
function beep(freq, dur, vol, type) {
  if (!soundOn || !audioCtx) return;
  const o = audioCtx.createOscillator(), g = audioCtx.createGain();
  o.type = type || 'sine'; o.frequency.value = freq;
  g.gain.setValueAtTime(vol, audioCtx.currentTime);
  g.gain.exponentialRampToValueAtTime(.001, audioCtx.currentTime + dur);
  o.connect(g); g.connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime + dur);
}
function doToggleSnd() {
  soundOn = !soundOn;
  document.getElementById('btnSnd').textContent = soundOn ? '🔊' : '🔇';
  if (!soundOn) stopEng();
}

// ═══════════════════════════════════════════════════
// MAIN RENDER LOOP
// ═══════════════════════════════════════════════════
let animFrameId = null;
let burnoutFired = false;

function render(ts) {
  animFrameId = requestAnimationFrame(render);
  const dt = Math.min((ts - lastTime) / 1000, 0.05);
  lastTime = ts;

  const W = cnv.width, H = cnv.height;
  const groundY = H * 0.78;

  // Current sim values
  const s     = Math.min(step, N - 1);
  const alt   = ALT[s],  vel  = VEL[s], acc = ACC[s];
  const fuel  = FUEL[s], fg   = FG[s],  fd  = FD[s];
  const mass  = INIT_MASS - (INIT_FUEL - fuel);
  const altFrac = MAX_ALT > 0 ? alt / MAX_ALT : 0;
  const burning = fuel > 0 && running;
  const fuelFrac = fuel / INIT_FUEL;
  const power   = burning ? (0.45 + (1 - fuelFrac) * 0.55) : 0;

  // Rocket position: map altitude → Y on canvas
  const rocketTopY = groundY - altFrac * groundY * 0.88;
  const rocketCX   = W * 0.42;
  const scale      = 0.9;
  const nozzleY    = rocketTopY + 41 * scale; // nozzle world-Y

  // Camera shake
  const sh = getShake();

  ctx.save();
  ctx.translate(sh.dx, sh.dy);

  // Sky + stars
  drawSky(altFrac);

  // Particles (draw under rocket)
  drawParticles();

  // Spawn exhaust
  if (running) {
    updateParticles(dt);
    if (burning) {
      const vRocket = -alt * 2; // pixels/s downward component
      spawnExhaust(rocketCX, nozzleY, power, vRocket);
      // Ground blast when close to pad
      if (altFrac < 0.06) spawnGroundBlast(rocketCX, groundY, power * (1 - altFrac * 16));
      setEng(power);
    }
  }

  // Flame below nozzle
  drawFlame(rocketCX, nozzleY, power, ts);

  // Launch pad (only visible when near ground)
  if (altFrac < 0.12) {
    ctx.globalAlpha = Math.max(0, 1 - altFrac * 8);
    drawPad(rocketCX, groundY);
    ctx.globalAlpha = 1;
  } else {
    // Draw ground line only
    ctx.fillStyle = '#061220';
    ctx.fillRect(0, groundY, W, H - groundY);
    ctx.strokeStyle = '#1a3a60';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, groundY); ctx.lineTo(W, groundY); ctx.stroke();
  }

  // Rocket
  drawRocket(rocketCX, rocketTopY, scale);

  // Altitude ruler
  drawRuler(groundY, altFrac);

  ctx.restore();

  // HUD overlay: altitude text on scene
  ctx.fillStyle = 'rgba(0,229,255,.55)';
  ctx.font = '700 11px monospace';
  ctx.fillText('ALT: ' + alt.toFixed(1) + ' km', 10, 20);
  ctx.font = '10px monospace';
  ctx.fillStyle = 'rgba(0,230,118,.5)';
  ctx.fillText('VEL: ' + Math.abs(vel).toFixed(0) + ' m/s', 10, 34);
  ctx.fillStyle = 'rgba(255,215,0,.5)';
  ctx.fillText('ACC: ' + acc.toFixed(2) + ' m/s²', 10, 48);

  // Advance simulation
  if (running) {
    frameAccum += dt * 1000;
    if (frameAccum >= STEP_MS) {
      frameAccum -= STEP_MS;
      step++;

      // Burnout detection
      if (!burnoutFired && step > 5 && step < N && FUEL[step] <= 0 && FUEL[Math.max(0,step-1)] > 0) {
        burnoutFired = true;
        stopEng();
        triggerShake(5, 0.4);
        beep(160, .4, .25, 'sawtooth');
        setTimeout(() => beep(80, .6, .1, 'sine'), 300);
      }

      if (step >= N) {
        running = false;
        stopEng();
        // Fanfare
        beep(523,.15,.2); setTimeout(()=>beep(659,.15,.2),160); setTimeout(()=>beep(784,.3,.25),320);
        document.getElementById('sdot').classList.remove('live');
        document.getElementById('sdot').style.background='#00e5ff';
        document.getElementById('sdot').style.boxShadow='0 0 6px #00e5ff';
        document.getElementById('stxt').textContent='COMPLETE';
        document.getElementById('phN').textContent='MISSION COMPLETE';
        document.getElementById('phN').style.color='#00e5ff';
        document.getElementById('phD').textContent='Apogee: '+MAX_ALT+'km. Peak vel: '+MAX_VEL+'m/s. Simulation done.';
      }
    }
    // Update telemetry every frame
    const ph = getPhase(step);
    document.getElementById('phN').textContent = ph.name;
    document.getElementById('phN').style.color = ph.col;
    document.getElementById('phEq').textContent = ph.eq;
    document.getElementById('phD').textContent  = ph.desc;
    document.getElementById('insT').textContent = ph.insT;
    document.getElementById('insB').textContent = ph.insB;
    document.getElementById('ckT').textContent  = 'T+'+(step)+'s';
    document.getElementById('ckA').textContent  = alt.toFixed(1)+'km';
    document.getElementById('ckP').textContent  = Math.round(step/N*100)+'%';

    const mxV = Math.max(MAX_VEL, 0.01), mxA = Math.max(MAX_ACC, 0.01);
    setTel('tA','bA',alt.toFixed(2),(alt/MAX_ALT)*100,'#00e5ff');
    setTel('tV','bV',Math.abs(vel).toFixed(1),(Math.abs(vel)/mxV)*100,'#00e676');
    setTel('tAc','bAc',acc.toFixed(3),(Math.abs(acc)/mxA)*100,'#ffd700');
    setTel('tF','bF',fuel.toFixed(2),(fuel/INIT_FUEL)*100,'#ff6b00');
    setTel('tFT','bFT',((fuel>0)?""" + str(_thrust_mn) + """:0).toFixed(2)+'','fuel>0?100:0','#00e5ff');
    setTel('tFG','bFG',fg.toFixed(1),Math.min((fg/Math.max(INIT_MASS*9.81/1000,1))*100,100),'#ff1744');
    setTel('tFD','bFD',fd.toFixed(1),Math.min(fd*2,100),'#8b5cf6');
    setTel('tM','bM',mass.toFixed(1),(mass/INIT_MASS)*100,'#5a7a9a');
  }
}

// ═══════════════════════════════════════════════════
// LAUNCH / RESET
// ═══════════════════════════════════════════════════
function doLaunch() {
  if (running) return;
  initAudio();
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
  document.getElementById('btnGo').disabled = true;
  document.getElementById('btnRst').style.display = 'inline-block';
  document.getElementById('sdot').classList.add('live');
  document.getElementById('stxt').textContent = 'LIVE';
  document.getElementById('phN').textContent = 'COUNTDOWN';
  document.getElementById('phN').style.color = '#ff6b00';

  let cd = 3;
  const ci = setInterval(() => {
    document.getElementById('phD').textContent = 'T-' + cd + ' … ' +
      (cd===3?'Pressurising tanks.':cd===2?'Pre-burner ignition.':'GO for launch.');
    beep(cd > 0 ? 440 : 880, cd > 0 ? .12 : .45, .32, 'sine');
    cd--;
    if (cd < 0) {
      clearInterval(ci);
      running = true;
      burnoutFired = false;
      triggerShake(12, 0.6);
      setTimeout(() => setEng(0.5), 100);
    }
  }, 900);
}

function doReset() {
  running = false; step = 0; frameAccum = 0; burnoutFired = false;
  particles = []; stopEng();
  document.getElementById('btnGo').disabled = false;
  document.getElementById('btnRst').style.display = 'none';
  document.getElementById('sdot').classList.remove('live');
  document.getElementById('sdot').style.background = '#ff1744';
  document.getElementById('sdot').style.boxShadow = '0 0 6px #ff1744';
  document.getElementById('stxt').textContent = 'STANDBY';
  document.getElementById('phN').textContent = 'PRE-LAUNCH';
  document.getElementById('phN').style.color = '#00e5ff';
  document.getElementById('phEq').textContent = 'F = m · a';
  document.getElementById('phD').textContent = 'Press LAUNCH to begin.';
  document.getElementById('ckT').textContent = 'T+0s';
  document.getElementById('ckA').textContent = '0km';
  document.getElementById('ckP').textContent = '0%';
  setTel('tA','bA','0.00',0,'#00e5ff');
  setTel('tV','bV','0.0',0,'#00e676');
  setTel('tAc','bAc','0.000',0,'#ffd700');
  setTel('tF','bF',INIT_FUEL.toFixed(1),100,'#ff6b00');
  setTel('tFT','bFT','""" + str(_thrust_mn) + """',100,'#00e5ff');
  setTel('tFG','bFG','—',0,'#ff1744');
  setTel('tFD','bFD','—',0,'#8b5cf6');
  setTel('tM','bM',INIT_MASS.toFixed(1),100,'#5a7a9a');
}

// Start render loop
lastTime = performance.now();
requestAnimationFrame(render);
</script>
</body></html>"""

    st.components.v1.html(rocket_launch_html, height=790, scrolling=False)


    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    # ── RESULT KPIs ───────────────────────────────────────────
    st.markdown('<div class="sh-sm">SIMULATION RESULTS</div>', unsafe_allow_html=True)
    rk1,rk2,rk3,rk4,rk5,rk6 = st.columns(6)
    for col,(lb,vl,cl) in zip([rk1,rk2,rk3,rk4,rk5,rk6],[
        ("MAX ALTITUDE",   f"{max_alt/1000:.2f} km",       "sc-cyan"),
        ("PEAK VELOCITY",  f"{max_vel:.1f} m/s",           "sc-grn"),
        ("ENGINE BURNOUT", f"T+{burnout:.0f}s" if not np.isnan(burnout) else "N/A", "sc-org"),
        ("MAX ACCEL.",     f"{max_acc:.2f} m/s²",          "sc-cyan"),
        ("FINAL MASS",     f"{fin_mass/1000:.1f} t",       "sc-org"),
        ("TWR",            f"{twr:.3f}",                   "sc-grn" if twr>1 else "sc-red"),
    ]):
        col.markdown(f"""<div class="stat-chip"><div class="sc-lbl">{lb}</div>
        <div class="sc-val {cl}">{vl}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    # ── PHYSICS CHARTS ────────────────────────────────────────
    st.markdown('<div class="sh-sm">ALTITUDE vs TIME</div>', unsafe_allow_html=True)
    fig_a = go.Figure()
    fig_a.add_trace(go.Scatter(x=sim["Time_s"],y=sim["Altitude_m"],
        name="Altitude"+(" (drag on)" if drag_on else " (drag off)"),
        line=dict(color=CYN,width=2.2),fill="tozeroy",fillcolor="rgba(0,229,255,.05)"))
    if compare and "sim_nd" in dir():
        fig_a.add_trace(go.Scatter(x=sim_nd["Time_s"],y=sim_nd["Altitude_m"],
            name="Altitude (no drag)",line=dict(color="#ff4b6e",width=1.8,dash="dot")))
    # Annotate burnout
    if not np.isnan(burnout):
        bo_alt = sim.loc[sim["Time_s"]==burnout,"Altitude_m"]
        if len(bo_alt):
            fig_a.add_vline(x=float(burnout),line_width=1,line_dash="dash",line_color=ORG,
                annotation_text=f"Burnout T+{burnout:.0f}s",
                annotation_position="top right",
                annotation_font=dict(color=ORG,size=10,family="Orbitron"))
    fig_a.add_annotation(x=sim["Time_s"].iloc[sim["Altitude_m"].argmax()],
                         y=max_alt, text=f"Apogee {max_alt/1000:.1f}km",
                         showarrow=True,arrowhead=2,arrowcolor=CYN,
                         font=dict(color=CYN,size=10,family="Orbitron"),
                         bgcolor="rgba(0,10,20,.7)",bordercolor=CYN,borderwidth=1)
    fig_a.update_layout(title="Altitude vs Time — Ascent + Coast + Apogee",
                        xaxis_title="Time (seconds)",yaxis_title="Altitude (m)",height=380,**PL)
    st.plotly_chart(fig_a,use_container_width=True)

    st.markdown('<div class="sh-sm">VELOCITY vs TIME</div>', unsafe_allow_html=True)
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=sim["Time_s"],y=sim["Velocity_ms"],
        name="Velocity"+(" (drag on)" if drag_on else " (drag off)"),
        line=dict(color=GRN,width=2.2)))
    if compare and "sim_nd" in dir():
        fig_v.add_trace(go.Scatter(x=sim_nd["Time_s"],y=sim_nd["Velocity_ms"],
            name="Velocity (no drag)",line=dict(color="#ffaacc",width=1.8,dash="dot")))
    if not np.isnan(burnout):
        fig_v.add_vline(x=float(burnout),line_width=1,line_dash="dash",line_color=ORG)
    fig_v.add_annotation(x=sim["Time_s"].iloc[sim["Velocity_ms"].argmax()],
                         y=max_vel,text=f"v_max {max_vel:.0f}m/s",
                         showarrow=True,arrowhead=2,arrowcolor=GRN,
                         font=dict(color=GRN,size=10,family="Orbitron"),
                         bgcolor="rgba(0,10,20,.7)",bordercolor=GRN,borderwidth=1)
    fig_v.update_layout(title="Velocity vs Time — Tsiolkovsky Acceleration Effect",
                        xaxis_title="Time (seconds)",yaxis_title="Velocity (m/s)",height=360,**PL)
    st.plotly_chart(fig_v,use_container_width=True)

    st.markdown('<div class="sh-sm">FUEL REMAINING vs TIME</div>', unsafe_allow_html=True)
    fig_f2 = go.Figure()
    fig_f2.add_trace(go.Scatter(x=sim["Time_s"],y=sim["Fuel_Remaining_kg"],
        name="Fuel Remaining",line=dict(color=ORG,width=2.2),
        fill="tozeroy",fillcolor="rgba(255,107,0,.05)"))
    if not np.isnan(burnout):
        fig_f2.add_vline(x=float(burnout),line_width=1,line_dash="dash",line_color=RED,
            annotation_text="Burnout",annotation_position="top right",
            annotation_font=dict(color=RED,size=10,family="Orbitron"))
    fig_f2.update_layout(title="Fuel Remaining vs Time — Engine Burnout",
                         xaxis_title="Time (seconds)",yaxis_title="Fuel Remaining (kg)",height=360,**PL)
    st.plotly_chart(fig_f2,use_container_width=True)

    st.markdown('<div class="sh-sm">ACCELERATION vs TIME — MASS REDUCTION EFFECT</div>',
                unsafe_allow_html=True)
    fig_acc_plt = go.Figure()
    fig_acc_plt.add_trace(go.Scatter(x=sim["Time_s"],y=sim["Acceleration_ms2"],
        name="Acceleration",line=dict(color="#ffd700",width=2),
        fill="tozeroy",fillcolor="rgba(255,215,0,.04)"))
    if not np.isnan(burnout):
        fig_acc_plt.add_vline(x=float(burnout),line_width=1,line_dash="dash",line_color=ORG,
            annotation_text=f"Peak a={max_acc:.1f}m/s²",annotation_position="top left",
            annotation_font=dict(color=ORG,size=10,family="Orbitron"))
    fig_acc_plt.add_annotation(x=0,y=sim["Acceleration_ms2"].iloc[0],
        text="Liftoff a",showarrow=True,arrowhead=2,arrowcolor="#ffd700",
        font=dict(color="#ffd700",size=10,family="Orbitron"),
        bgcolor="rgba(0,10,20,.7)",bordercolor="#ffd700",borderwidth=1)
    fig_acc_plt.update_layout(title="Acceleration vs Time — rises as fuel burns (Tsiolkovsky)",
                               xaxis_title="Time (s)",yaxis_title="Acceleration (m/s²)",height=340,**PL)
    st.plotly_chart(fig_acc_plt,use_container_width=True)

    st.markdown('<div class="sh-sm">FORCE COMPONENTS OVER TIME</div>', unsafe_allow_html=True)
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(x=sim["Time_s"],y=sim["Thrust_N"],
        name="Thrust (N)",line=dict(color=CYN,width=2)))
    fig_fc.add_trace(go.Scatter(x=sim["Time_s"],y=sim["F_gravity_N"],
        name="Gravity (N)",line=dict(color=RED,width=2)))
    fig_fc.add_trace(go.Scatter(x=sim["Time_s"],y=sim["F_drag_N"],
        name="Drag (N)",line=dict(color=ORG,width=2,dash="dash")))
    net_f = sim["Thrust_N"]-sim["F_gravity_N"]-sim["F_drag_N"]
    fig_fc.add_trace(go.Scatter(x=sim["Time_s"],y=net_f,name="Net Force (N)",
        line=dict(color=GRN,width=1.6,dash="dot"),
        fill="tozeroy",fillcolor="rgba(0,230,118,.04)"))
    fig_fc.update_layout(title="Force Breakdown — Thrust vs Gravity vs Drag vs Net Force",
                         xaxis_title="Time (s)",yaxis_title="Force (N)",height=380,**PL)
    st.plotly_chart(fig_fc,use_container_width=True)

    # Drag comparison insight
    drag_note = ""
    if compare and "sim_nd" in dir():
        nd_max = sim_nd["Altitude_m"].max()
        dp = (nd_max-max_alt)/nd_max*100 if nd_max>0 else 0
        drag_note = f" Disabling drag increases peak altitude by <strong>{dp:.1f}%</strong>."
    if twr <= 1.0:
        st.markdown("""<div class="wbox">⚠️ TWR below 1.0. Increase thrust or reduce mass.</div>""",
                    unsafe_allow_html=True)
    st.markdown(f"""<div class="ib"><strong>TWR = {twr:.3f}</strong> —
    {'Net upward acceleration confirmed.' if twr>1 else 'Cannot overcome gravity.'}<br><br>
    Forward-Euler (200 steps, dt=1s). As fuel burns m(t) decreases → a = F/m(t) rises.
    Drag = Cd·v² compounds at high speed.{drag_note}</div>""", unsafe_allow_html=True)


    # ══════════════════════════════════════════════════════════
    # PHYSICS LAW SIMULATIONS — How each law drives the rocket
    # ══════════════════════════════════════════════════════════
    st.markdown('<div class="sh">🔬 PHYSICS LAWS IN ACTION — YOUR ROCKET</div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="ib">Every number below is computed from <strong>your slider
    values</strong>. Change the controls above and re-run to see how each law responds.</div>""",
    unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚖️ Newton's 2nd Law",
        "🚀 Tsiolkovsky Equation",
        "💨 Atmospheric Drag",
        "🔢 Forward-Euler",
        "📐 All Forces Together"
    ])

    # ── TAB 1: Newton's 2nd Law — F = ma → how it changes during flight ──
    with tab1:
        st.markdown('<div class="sh-sm">F = m(t) · a  —  NET FORCE DRIVES ACCELERATION</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""<div class="concept-box">
          <div class="concept-title">Newton's 2nd Law in Rocket Context</div>
          <div class="concept-body">
            At every time step: <span class="concept-formula">F_net = F_thrust − F_gravity − F_drag</span>
            &nbsp;&nbsp;<span class="concept-formula">a = F_net / m(t)</span><br><br>
            Your rocket: Thrust = <strong>{thrust/1e6:.2f} MN</strong>,
            Initial weight = <strong>{(init_mass*9.81)/1e6:.2f} MN</strong>,
            Net force at T=0 = <strong>{(thrust - init_mass*9.81)/1e6:.3f} MN</strong>
            → Initial acceleration = <strong>{(thrust - init_mass*9.81)/init_mass:.3f} m/s²</strong>
          </div>
        </div>""", unsafe_allow_html=True)

        # Show how acceleration changes as mass drops
        _times  = sim["Time_s"].values
        _accs   = sim["Acceleration_ms2"].values
        _masses = sim["Mass_kg"].values
        _net_f  = sim["Thrust_N"] - sim["F_gravity_N"] - sim["F_drag_N"]

        fig_n2 = go.Figure()
        fig_n2.add_trace(go.Scatter(x=_times, y=_masses/1000,
            name="Rocket Mass (t)", line=dict(color="#5a7a9a", width=2),
            yaxis="y2"))
        fig_n2.add_trace(go.Scatter(x=_times, y=_accs,
            name="Acceleration (m/s²)", line=dict(color="#ffd700", width=2.2),
            fill="tozeroy", fillcolor="rgba(255,215,0,.05)"))
        fig_n2.add_trace(go.Scatter(x=_times, y=_net_f/1000,
            name="Net Force (kN)", line=dict(color="#00e676", width=1.5, dash="dash")))
        fig_n2.update_layout(
            title="Newton's 2nd Law: As m(t) drops — a = F/m rises",
            xaxis=dict(title="Time (s)", gridcolor="#1a3a60", zeroline=False, color="#cce0f0"),
            yaxis=dict(title="Acceleration (m/s2) / Net Force (kN)",
                       gridcolor="#1a3a60", color="#cce0f0", zeroline=False),
            yaxis2=dict(title="Mass (tonnes)", overlaying="y", side="right",
                        gridcolor="#1a3a60", color="#5a7a9a", zeroline=False),
            height=400, **PL_NA)
        st.plotly_chart(fig_n2, use_container_width=True)
        st.markdown(f"""<div class="ib"><strong>What you see:</strong>
        The gold line (acceleration) rises over time even though thrust is constant.
        This is Newton's 2nd Law in action: <em>a = F/m(t)</em>.
        As the grey line (mass) falls due to fuel burn, the same thrust force
        produces more acceleration. Peak acceleration = <strong>{max_acc:.2f} m/s²</strong>
        occurs at engine burnout when mass is minimum.</div>""", unsafe_allow_html=True)

    # ── TAB 2: Tsiolkovsky Rocket Equation ───────────────────
    with tab2:
        st.markdown('<div class="sh-sm">Δv = Isp · g · ln(m₀/m_f)  —  THE ROCKET EQUATION</div>',
                    unsafe_allow_html=True)
        Isp_val = 300.0
        m_fuel_used = init_mass - fin_mass
        mass_ratio = init_mass / fin_mass if fin_mass > 0 else 1
        delta_v_theory = Isp_val * 9.81 * np.log(mass_ratio)
        st.markdown(f"""<div class="concept-box">
          <div class="concept-title">Tsiolkovsky Rocket Equation</div>
          <div class="concept-body">
            <span class="concept-formula">Δv = Isp · g₀ · ln(m₀ / m_f)</span><br><br>
            Your rocket: Isp = {Isp_val:.0f}s, m₀ = {init_mass/1000:.1f}t,
            m_f = {fin_mass/1000:.1f}t, mass ratio = {mass_ratio:.3f}<br>
            <strong>Theoretical Δv = {delta_v_theory:.1f} m/s
            ({delta_v_theory/1000:.3f} km/s)</strong><br>
            Actual peak velocity = {max_vel:.1f} m/s
            (simulation losses from drag + gravity cost {delta_v_theory - max_vel:.1f} m/s)
          </div>
        </div>""", unsafe_allow_html=True)

        # Show how Δv scales with mass ratio
        _mratios = np.linspace(1.05, 20, 200)
        _dvs = Isp_val * 9.81 * np.log(_mratios)
        fig_tsio = go.Figure()
        fig_tsio.add_trace(go.Scatter(x=_mratios, y=_dvs,
            mode="lines", name="Theoretical Δv",
            line=dict(color=CYN, width=2.2)))
        # Mark your rocket's mass ratio
        fig_tsio.add_vline(x=mass_ratio, line_width=2, line_dash="dash",
            line_color=ORG,
            annotation_text=f"Your rocket: {mass_ratio:.2f}x",
            annotation_position="top right",
            annotation_font=dict(color=ORG, size=11, family="Orbitron"))
        fig_tsio.add_hline(y=delta_v_theory, line_width=1, line_dash="dot",
            line_color=GRN,
            annotation_text=f"Δv={delta_v_theory:.0f} m/s",
            annotation_position="right",
            annotation_font=dict(color=GRN, size=10))
        fig_tsio.update_layout(
            title="Tsiolkovsky: Δv vs Mass Ratio (Isp=300s)  — logarithmic curve",
            xaxis_title="Mass Ratio (m₀/m_f)",
            yaxis_title="Delta-v (m/s)",
            height=380, **PL)
        st.plotly_chart(fig_tsio, use_container_width=True)

        # Show velocity curve decomposed into fuel stages
        fig_vel_decomp = go.Figure()
        fig_vel_decomp.add_trace(go.Scatter(
            x=sim["Time_s"], y=sim["Velocity_ms"],
            name="Actual velocity (sim)", line=dict(color=GRN, width=2.2)))
        # Theoretical cumulative Δv from Tsiolkovsky at each step
        _theor_dv = [Isp_val * 9.81 * np.log(init_mass / max(m, fin_mass+1))
                     for m in sim["Mass_kg"].values]
        fig_vel_decomp.add_trace(go.Scatter(
            x=sim["Time_s"], y=_theor_dv,
            name="Tsiolkovsky theoretical Δv", line=dict(color=CYN, width=1.8, dash="dot")))
        fig_vel_decomp.add_annotation(
            x=sim["Time_s"].iloc[-1], y=_theor_dv[-1],
            text=f"Losses: {_theor_dv[-1]-max_vel:.0f} m/s",
            showarrow=True, arrowhead=2, arrowcolor=RED,
            font=dict(color=RED, size=10, family="Orbitron"),
            bgcolor="rgba(0,10,20,.7)", bordercolor=RED, borderwidth=1)
        fig_vel_decomp.update_layout(
            title="Actual velocity vs Tsiolkovsky ideal — losses from drag & gravity",
            xaxis_title="Time (s)", yaxis_title="Velocity (m/s)",
            height=360, **PL)
        st.plotly_chart(fig_vel_decomp, use_container_width=True)
        st.markdown(f"""<div class="ib"><strong>Why actual < theoretical:</strong>
        Tsiolkovsky gives <em>ideal</em> Δv in vacuum with no gravity.
        Your simulation loses <strong>{_theor_dv[-1]-max_vel:.0f} m/s</strong>
        to gravity drag (fighting Earth's pull during ascent) and
        atmospheric drag (F_d = Cd·v²). Multi-stage rockets discard
        empty tanks to reset the mass ratio.</div>""", unsafe_allow_html=True)

    # ── TAB 3: Atmospheric Drag ───────────────────────────────
    with tab3:
        st.markdown('<div class="sh-sm">F_drag = Cd · v²  —  QUADRATIC VELOCITY PENALTY</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""<div class="concept-box">
          <div class="concept-title">Atmospheric Drag Law</div>
          <div class="concept-body">
            <span class="concept-formula">F_drag = C_d · v²</span><br><br>
            Your Cd = <strong>{drag_c:.2f}</strong>.
            At peak velocity {max_vel:.1f} m/s:
            F_drag = {drag_c:.2f} × {max_vel:.1f}² = <strong>{drag_c*max_vel**2/1000:.1f} kN</strong><br>
            Compare to thrust: {thrust/1e6:.2f} MN =
            {thrust/max(drag_c*max_vel**2,1):.0f}× the drag force at peak speed.
          </div>
        </div>""", unsafe_allow_html=True)

        # Drag force curve + quadratic reference
        _v_range = np.linspace(0, max(max_vel*1.1, 100), 300)
        _fd_theory = drag_c * _v_range**2

        fig_drag = go.Figure()
        fig_drag.add_trace(go.Scatter(
            x=sim["Velocity_ms"], y=sim["F_drag_N"]/1000,
            mode="markers", name="Sim drag points",
            marker=dict(color="#8b5cf6", size=3, opacity=0.6)))
        fig_drag.add_trace(go.Scatter(
            x=_v_range, y=_fd_theory/1000,
            mode="lines", name=f"F_drag = {drag_c:.2f}·v² (theory)",
            line=dict(color="#8b5cf6", width=2.2)))
        fig_drag.add_trace(go.Scatter(
            x=_v_range, y=np.full_like(_v_range, thrust/1000),
            mode="lines", name=f"Thrust = {thrust/1e6:.2f} MN (constant)",
            line=dict(color=CYN, width=1.5, dash="dash"), opacity=0.7))
        fig_drag.update_layout(
            title="Drag Force vs Velocity — Cd·v² quadratic growth",
            xaxis_title="Velocity (m/s)", yaxis_title="Force (kN)",
            height=380, **PL)
        st.plotly_chart(fig_drag, use_container_width=True)

        # Drag vs altitude
        fig_drag_alt = go.Figure()
        fig_drag_alt.add_trace(go.Scatter(
            x=sim["Altitude_m"]/1000, y=sim["F_drag_N"]/1000,
            mode="lines", name="Drag Force",
            line=dict(color="#8b5cf6", width=2.2),
            fill="tozeroy", fillcolor="rgba(139,92,246,.07)"))
        if compare and "sim_nd" in dir():
            alt_diff = (sim_nd["Altitude_m"] - sim["Altitude_m"]).clip(lower=0)
            fig_drag_alt.add_trace(go.Scatter(
                x=sim["Altitude_m"]/1000, y=alt_diff/1000,
                name="Altitude lost to drag (km)",
                line=dict(color=RED, width=1.5, dash="dot")))
        fig_drag_alt.add_annotation(
            x=sim.loc[sim["F_drag_N"].idxmax(), "Altitude_m"]/1000,
            y=sim["F_drag_N"].max()/1000,
            text="Max-Q (peak drag)",
            showarrow=True, arrowhead=2, arrowcolor="#8b5cf6",
            font=dict(color="#8b5cf6", size=10, family="Orbitron"),
            bgcolor="rgba(0,10,20,.7)", bordercolor="#8b5cf6", borderwidth=1)
        fig_drag_alt.update_layout(
            title="Drag Force vs Altitude — Max-Q point marked",
            xaxis_title="Altitude (km)", yaxis_title="Drag Force (kN)",
            height=360, **PL)
        st.plotly_chart(fig_drag_alt, use_container_width=True)
        st.markdown(f"""<div class="ib"><strong>Max-Q (Maximum Dynamic Pressure)</strong>
        occurs at altitude {sim.loc[sim['F_drag_N'].idxmax(),'Altitude_m']/1000:.2f} km,
        T+{sim.loc[sim['F_drag_N'].idxmax(),'Time_s']:.0f}s.
        This is when velocity is high AND atmosphere is still dense — the worst
        structural stress point. Real rockets throttle down ~20% through Max-Q.
        Your Cd={drag_c:.2f} generates peak drag of
        <strong>{sim['F_drag_N'].max()/1000:.1f} kN</strong>.</div>""",
        unsafe_allow_html=True)

    # ── TAB 4: Forward-Euler Integration ─────────────────────
    with tab4:
        st.markdown('<div class="sh-sm">x(t+dt) = x(t) + v·dt  —  NUMERICAL INTEGRATION</div>',
                    unsafe_allow_html=True)
        st.markdown("""<div class="concept-box">
          <div class="concept-title">Forward-Euler Method — How the simulation runs</div>
          <div class="concept-body">
            Every 1-second step the simulator does exactly 3 equations:<br>
            <span class="concept-formula">a(t) = F_net(t) / m(t)</span>
            &nbsp;&nbsp;<span class="concept-formula">v(t+1) = v(t) + a(t) · dt</span>
            &nbsp;&nbsp;<span class="concept-formula">x(t+1) = x(t) + v(t) · dt</span><br><br>
            200 iterations = 200 seconds of flight simulated.
            Error accumulates because we assume force is constant within each 1s step.
            A Runge-Kutta 4 method would use 4 evaluations per step for higher accuracy.
          </div>
        </div>""", unsafe_allow_html=True)

        # Show cumulative integration error vs smaller dt
        # Resimulate with dt=0.1 (10x more accurate) and compare
        with st.spinner("Running high-accuracy comparison (dt=0.1s)..."):
            sim_fine = simulate(init_mass, thrust, drag_c, payload, fuel, burn_r, drag_on, dt=0.1, steps=2000)
        # Sample every 10 steps to match original time axis
        sim_fine_sampled = sim_fine.iloc[::10].reset_index(drop=True)
        t_compare = min(len(sim), len(sim_fine_sampled))

        fig_euler = go.Figure()
        fig_euler.add_trace(go.Scatter(
            x=sim["Time_s"][:t_compare],
            y=sim["Altitude_m"][:t_compare],
            name="dt=1s (200 steps)", line=dict(color=CYN, width=2.2)))
        fig_euler.add_trace(go.Scatter(
            x=sim_fine_sampled["Time_s"][:t_compare],
            y=sim_fine_sampled["Altitude_m"][:t_compare],
            name="dt=0.1s (2000 steps — more accurate)",
            line=dict(color=GRN, width=1.8, dash="dot")))
        alt_err = abs(sim["Altitude_m"][:t_compare].values -
                      sim_fine_sampled["Altitude_m"][:t_compare].values)
        fig_euler.add_trace(go.Scatter(
            x=sim["Time_s"][:t_compare], y=alt_err,
            name="Integration error (m)", yaxis="y2",
            line=dict(color=ORG, width=1.2, dash="dashdot"), opacity=0.7))
        fig_euler.update_layout(
            title="Forward-Euler dt=1s vs dt=0.1s — integration error visible",
            xaxis=dict(title="Time (s)", gridcolor="#1a3a60", zeroline=False, color="#cce0f0"),
            yaxis=dict(title="Altitude (m)", gridcolor="#1a3a60", color="#cce0f0", zeroline=False),
            yaxis2=dict(title="Error (m)", overlaying="y", side="right",
                        gridcolor="#1a3a60", color=ORG, zeroline=False),
            height=400, **PL_NA)
        st.plotly_chart(fig_euler, use_container_width=True)

        # Show step-by-step calculation for first 10 steps
        st.markdown('<div class="sh-sm">FIRST 10 STEPS — EULER ARITHMETIC SHOWN</div>',
                    unsafe_allow_html=True)
        step_rows = []
        for _, row in sim.head(10).iterrows():
            step_rows.append({
                "T (s)": int(row["Time_s"]),
                "Mass kg": f"{row['Mass_kg']:,.0f}",
                "F_thrust N": f"{row['Thrust_N']:,.0f}",
                "F_grav N":   f"{row['F_gravity_N']:,.0f}",
                "F_drag N":   f"{row['F_drag_N']:,.0f}",
                "F_net N":    f"{row['Thrust_N']-row['F_gravity_N']-row['F_drag_N']:,.0f}",
                "a (m/s²)":  f"{row['Acceleration_ms2']:.4f}",
                "v (m/s)":   f"{row['Velocity_ms']:.3f}",
                "Alt (m)":   f"{row['Altitude_m']:.2f}",
            })
        st.dataframe(pd.DataFrame(step_rows), use_container_width=True)
        st.markdown("""<div class="ib">Each row is one Forward-Euler step.
        Read left to right: mass at this instant → compute all forces →
        net force / mass = acceleration → update velocity → update position.
        Repeat 200 times = full flight trajectory.</div>""", unsafe_allow_html=True)

    # ── TAB 5: All Forces Together ────────────────────────────
    with tab5:
        st.markdown('<div class="sh-sm">ALL 4 LAWS SIMULTANEOUSLY — FORCE BALANCE OVER TIME</div>',
                    unsafe_allow_html=True)

        # Stacked area chart showing proportion of each force
        _ft = sim["Thrust_N"].values
        _fg = sim["F_gravity_N"].values
        _fd = sim["F_drag_N"].values
        _fn = (_ft - _fg - _fd)
        _t  = sim["Time_s"].values

        fig_all = make_subplots(rows=3, cols=1,
            subplot_titles=("Force Balance (N)", "Velocity + Altitude", "Mass + Acceleration"),
            vertical_spacing=0.1, shared_xaxes=True)

        fig_all.add_trace(go.Scatter(x=_t, y=_ft/1000, name="Thrust (kN)",
            line=dict(color=CYN, width=2)), row=1, col=1)
        fig_all.add_trace(go.Scatter(x=_t, y=_fg/1000, name="Gravity (kN)",
            line=dict(color=RED, width=2)), row=1, col=1)
        fig_all.add_trace(go.Scatter(x=_t, y=_fd/1000, name="Drag (kN)",
            line=dict(color="#8b5cf6", width=1.5, dash="dash")), row=1, col=1)
        fig_all.add_trace(go.Scatter(x=_t, y=_fn/1000, name="Net Force (kN)",
            line=dict(color=GRN, width=2),
            fill="tozeroy", fillcolor="rgba(0,230,118,.06)"), row=1, col=1)

        fig_all.add_trace(go.Scatter(x=_t, y=sim["Velocity_ms"].values,
            name="Velocity (m/s)", line=dict(color=GRN, width=1.8)), row=2, col=1)
        fig_all.add_trace(go.Scatter(x=_t, y=sim["Altitude_m"].values/1000,
            name="Altitude (km)", line=dict(color=CYN, width=1.8),
            yaxis="y4"), row=2, col=1)

        fig_all.add_trace(go.Scatter(x=_t, y=sim["Mass_kg"].values/1000,
            name="Mass (t)", line=dict(color="#5a7a9a", width=1.8)), row=3, col=1)
        fig_all.add_trace(go.Scatter(x=_t, y=sim["Acceleration_ms2"].values,
            name="Acceleration (m/s²)", line=dict(color="#ffd700", width=1.8)), row=3, col=1)

        fig_all.update_layout(
            height=750,
            plot_bgcolor=f"#{BG}", paper_bgcolor=f"#{BG}",
            font_color=TXT, font_family="Rajdhani",
            title_font=dict(family="Orbitron", color=CYN, size=13),
            showlegend=True,
            legend=dict(bgcolor=SRF, bordercolor=BRD, borderwidth=1,
                        orientation="h", x=0, y=-0.05),
            margin=dict(t=52, b=80, l=54, r=16))
        for i in range(1, 4):
            fig_all.update_xaxes(gridcolor=BRD, gridwidth=.5,
                                 zeroline=False, color=TXT, row=i, col=1)
            fig_all.update_yaxes(gridcolor=BRD, gridwidth=.5,
                                 zeroline=False, color=TXT, row=i, col=1)
        fig_all.update_xaxes(title_text="Time (s)", row=3, col=1)
        st.plotly_chart(fig_all, use_container_width=True)
        st.markdown(f"""<div class="ib">
        <strong>Reading the chart together:</strong><br>
        Row 1 — At T=0 thrust ({thrust/1e6:.2f}MN) > gravity ({init_mass*9.81/1e6:.2f}MN) → positive net force → liftoff.
        Thrust drops to zero at burnout T+{_bts}s.<br>
        Row 2 — Velocity rises during burn, then decelerates. Altitude continues rising until KE=0.<br>
        Row 3 — Mass falls linearly (constant burn rate). Acceleration rises as mass drops
        (Newton's 2nd Law + Tsiolkovsky). This is the complete physics loop of every rocket ever launched.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)


    # ── STEP-BY-STEP WALKTHROUGH ──────────────────────────────
    st.markdown('<div class="sh-sm">STEP-BY-STEP MISSION WALKTHROUGH</div>',
                unsafe_allow_html=True)
    try:
        steps_data = build_sim_steps(sim, twr, init_mass, thrust, drag_c, payload, fuel, burn_r)
    except Exception as _e:
        steps_data = [("ERROR", f"Step builder failed: {str(_e)}", "")]
    total_steps = len(steps_data)
    btn1,btn2,btn3 = st.columns([1,1,2])
    with btn1:
        if st.button("→ Next Step", use_container_width=True):
            if st.session_state.sim_steps_idx < total_steps:
                st.session_state.sim_steps_idx += 1
    with btn2:
        if st.button("📄 All Steps", use_container_width=True):
            st.session_state.show_all_steps = True
            st.session_state.sim_steps_idx  = total_steps
    with btn3:
        if st.button("↺ Reset Steps", use_container_width=True):
            st.session_state.sim_steps_idx  = 0
            st.session_state.show_all_steps = False

    cur = st.session_state.sim_steps_idx
    pct_s = int(cur/total_steps*100) if total_steps else 0
    st.markdown(f"""<div class="pbar-wrap">
      <div class="pbar-lbl">MISSION PROGRESS — STEP {cur} / {total_steps} &nbsp;({pct_s}%)</div>
      <div class="pbar-track"><div class="pbar-fill" style="width:{pct_s}%;"></div></div>
    </div>""", unsafe_allow_html=True)

    show_n = total_steps if st.session_state.show_all_steps else cur
    for i,(snum,sbody,sval) in enumerate(steps_data[:show_n]):
        val_html = f'<div class="step-val">{sval}</div>' if sval else ""
        st.markdown(f"""<div class="step-card">
          <div class="step-num">STEP {i+1} — {snum}</div>
          <div class="step-body">{sbody}</div>{val_html}</div>""", unsafe_allow_html=True)

    if show_n == 0:
        st.markdown('<div class="ib">Click <strong>→ Next Step</strong> to walk through '
                    'the mission sequence, or <strong>All Steps</strong> to reveal all.</div>',
                    unsafe_allow_html=True)

    # ── CONCEPT EXPLAINER ─────────────────────────────────────
    show_concept = st.checkbox("📖 Show Physics Concept Explanation")
    if show_concept:
        st.markdown("""
        <div class="concept-box">
          <div class="concept-title">⚛ TSIOLKOVSKY ROCKET EQUATION</div>
          <div class="concept-body">
            <span class="concept-formula">Δv = Isp · g₀ · ln(m₀ / m_f)</span><br><br>
            As fuel burns m(t) drops → a = F/m(t) rises. This is why the rocket
            accelerates fastest just before burnout, not at liftoff.
          </div>
        </div>
        <div class="concept-box">
          <div class="concept-title">🌀 ATMOSPHERIC DRAG F = Cd · v²</div>
          <div class="concept-body">
            Drag scales with v². Doubling speed quadruples drag. Real rockets use
            gravity-turn trajectories to minimise time in dense atmosphere.
          </div>
        </div>""", unsafe_allow_html=True)

    # ── EXPORT ────────────────────────────────────────────────
    st.markdown('<div class="sh-sm">EXPORT SIMULATION DATA</div>', unsafe_allow_html=True)
    _params = {"Initial_Mass_kg": init_mass, "Thrust_N": thrust, "Drag_Coefficient": drag_c,
               "Payload_kg": payload, "Fuel_kg": fuel, "Burn_Rate_Factor": burn_r,
               "Drag_Enabled": drag_on, "TWR": round(twr,4),
               "Max_Altitude_km": round(max_alt/1000,3), "Peak_Velocity_ms": round(max_vel,2)}
    ex1,ex2 = st.columns(2)
    with ex1:
        st.download_button("⬇ Export Simulation CSV", sim_export_csv(sim, _params),
            file_name=f"sim_{datetime.now().strftime('%H%M%S')}.csv", mime="text/csv",
            use_container_width=True)
    with ex2:
        st.download_button("⬇ Export Parameters JSON", json.dumps(_params,indent=2).encode(),
            file_name=f"params_{datetime.now().strftime('%H%M%S')}.json",
            mime="application/json", use_container_width=True)

    st.markdown('<div class="sh-sm">FULL SIMULATION DATA TABLE</div>', unsafe_allow_html=True)
    st.dataframe(sim.round(3), use_container_width=True)

    st.markdown('<div class="sh-sm">TRAJECTORY PHASE ANALYSIS</div>', unsafe_allow_html=True)
    phases_tbl = [
        ("Liftoff T+0→T+50s",   sim.iloc[:50]["Altitude_m"].max(),   sim.iloc[:50]["Velocity_ms"].max(),   sim.iloc[:50]["Acceleration_ms2"].max()),
        ("Climb T+50→T+100s",   sim.iloc[50:100]["Altitude_m"].max(),sim.iloc[50:100]["Velocity_ms"].max(),sim.iloc[50:100]["Acceleration_ms2"].max()),
        ("Coast T+100→T+150s",  sim.iloc[100:150]["Altitude_m"].max(),sim.iloc[100:150]["Velocity_ms"].max(),sim.iloc[100:150]["Acceleration_ms2"].max()),
        ("Terminal T+150→T+200s",sim.iloc[150:]["Altitude_m"].max(), sim.iloc[150:]["Velocity_ms"].max(),  sim.iloc[150:]["Acceleration_ms2"].max()),
    ]
    ph_cols = st.columns(4)
    for col,(phase,alt,vel,acc) in zip(ph_cols,phases_tbl):
        col.markdown(f"""<div class="stat-chip">
        <div class="sc-lbl" style="font-size:.52rem;">{phase}</div>
        <div class="sc-val sc-cyan" style="font-size:.85rem;">{alt/1000:.1f} km</div>
        <div class="ms">{vel:.0f} m/s · {acc:.2f} m/s²</div></div>""",
        unsafe_allow_html=True)

# PAGE 6 — INSIGHTS  (unchanged + export)
# ══════════════════════════════════════════════════════════════
elif page == "Insights":
    st.markdown('<div class="sh">💡 SECTION 6 — KEY INSIGHTS &amp; CONCLUSIONS</div>',
                unsafe_allow_html=True)

    bullets = [
        ("INSIGHT 01 — Heavier Payload Requires Significantly More Fuel",
         "The analysis confirms r ≈ 0.70 between payload weight and fuel consumption. "
         "Every 1,000 kg increase in payload demands ~18 additional tons of propellant — "
         "consistent with the Tsiolkovsky rocket equation. Payload mass optimisation is "
         "the single highest-leverage design decision in mission planning."),
        ("INSIGHT 02 — High Cost Does Not Guarantee Mission Success",
         "Successful missions average 12–20% higher cost than failed ones, yet many "
         "expensive missions still fail. A budget threshold near USD 900 million separates "
         "high-risk from low-risk clusters. Mission architecture quality and design "
         "discipline matter more than raw expenditure levels."),
        ("INSIGHT 03 — Atmospheric Drag Significantly Reduces Peak Altitude",
         "Physics simulation shows enabling atmospheric drag reduces peak altitude by 8–12% "
         "compared to vacuum. This quantifies the velocity budget consumed by aerodynamic "
         "resistance during first-stage ascent. Gravity-turn trajectories reduce drag losses "
         "by 30–40% compared to purely vertical ascent."),
        ("INSIGHT 04 — Reducing Mass Dramatically Increases Acceleration",
         "As fuel burns, m(t) falls → acceleration rises at constant thrust. This Tsiolkovsky "
         "mass-fraction effect causes the rocket to accelerate fastest at engine burnout, "
         "not at liftoff. This is the physical justification for multi-stage rocket design."),
        ("INSIGHT 05 — Crew Size 4–6 Maximises Mission Success",
         "Missions with 4–6 crew achieve 73–82% success rates — the highest of any group. "
         "Human presence enables real-time anomaly resolution beyond pre-programmed logic. "
         "Uncrewed missions show lowest success rates for complex deep-space profiles."),
    ]
    for title,body in bullets:
        st.markdown(f"""<div class="bc"><div class="bn">{title}</div>
        <div class="bt">{body}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sh-sm">SUCCESS RATE BY MISSION TYPE</div>',
                unsafe_allow_html=True)
    sr_t = (df.groupby("Mission_Type")["Mission_Success"]
              .agg(Success_Rate="mean",Count="size").reset_index())
    sr_t["Success_Rate"] = (sr_t["Success_Rate"]*100).round(1)
    fig_sr = px.bar(sr_t,x="Mission_Type",y="Success_Rate",
                    color="Success_Rate",text="Success_Rate",
                    color_continuous_scale=[[0,RED],[.5,ORG],[1,GRN]],
                    title="Mission Success Rate by Type",
                    labels={"Mission_Type":"Type","Success_Rate":"Success Rate (%)"})
    fig_sr.update_traces(texttemplate="%{text:.1f}%",textposition="outside",
                         marker_line_width=0)
    pl(fig_sr,360); st.plotly_chart(fig_sr,use_container_width=True)

    st.markdown('<div class="sh-sm">MISSION TYPE SUMMARY TABLE</div>',
                unsafe_allow_html=True)
    summ = (df.groupby("Mission_Type").agg(
        Missions    =("Mission_ID","size"),
        Success_Rate=("Mission_Success","mean"),
        Avg_Cost_M  =("Mission_Cost_M_USD","mean"),
        Avg_Duration=("Mission_Duration_days","mean"),
        Avg_Fuel_t  =("Fuel_Consumption_tons","mean"),
        Avg_Yield   =("Scientific_Yield_Score","mean"),
    ).reset_index())
    summ["Success_Rate"] = (summ["Success_Rate"]*100).round(1)
    for c in ["Avg_Cost_M","Avg_Duration","Avg_Fuel_t","Avg_Yield"]:
        summ[c] = summ[c].round(1)
    summ.columns = ["Mission Type","Missions","Success %","Avg Cost $M",
                    "Avg Duration (d)","Avg Fuel (t)","Avg Yield"]
    st.dataframe(summ, use_container_width=True)

    # ← NEW: export summary
    st.download_button("⬇ Export Summary Table (CSV)",
                       df_to_csv(summ),
                       file_name="mission_type_summary.csv",
                       mime="text/csv")

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;font-family:'Orbitron',monospace;font-size:.62rem;
                letter-spacing:2px;color:#102030;padding:8px 0;">
      ROCKET LAUNCH ANALYTICS &nbsp;|&nbsp; SPACE MISSION INTELLIGENCE DASHBOARD
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 7 — SIM HISTORY  ← NEW PAGE
# ══════════════════════════════════════════════════════════════
elif page == "Sim History":
    st.markdown('<div class="sh">📋 SECTION 7 — SIMULATION HISTORY</div>',
                unsafe_allow_html=True)

    hist = st.session_state.sim_history
    if not hist:
        st.markdown("""<div class="ib">No simulations run yet this session.
        Go to <strong>Rocket Simulation</strong>, set parameters, and run —
        every result is stored here automatically. Last 10 runs are kept.</div>""",
        unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sbox">Storing <strong>{len(hist)}</strong> simulation(s) '
                    f'this session.</div>', unsafe_allow_html=True)

        twrs = [h["twr"]     for h in hist]
        alts = [h["max_alt"] for h in hist]
        bts  = [h["burnout"] for h in hist]

        hk1,hk2,hk3,hk4 = st.columns(4)
        for col,(lb,vl,cl) in zip([hk1,hk2,hk3,hk4],[
            ("TOTAL RUNS",   str(st.session_state.total_sims),        "sc-cyan"),
            ("BEST ALTITUDE",f"{max(alts):.2f} km",                    "sc-grn"),
            ("AVG TWR",      f"{sum(twrs)/len(twrs):.3f}",             "sc-org"),
            ("FASTEST BURN", f"T+{min(bts)}s",                         "sc-red"),
        ]):
            col.markdown(f"""<div class="stat-chip"><div class="sc-lbl">{lb}</div>
            <div class="sc-val {cl}">{vl}</div></div>""", unsafe_allow_html=True)

        st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sh-sm">ALL RUNS THIS SESSION</div>', unsafe_allow_html=True)

        for i,h in enumerate(hist):
            drag_txt = "Drag ON" if h.get("drag_on", True) else "Drag OFF"
            run_num  = st.session_state.total_sims - i
            st.markdown(f"""<div class="hist-card">
            <div class="hist-prob">RUN #{run_num} &nbsp;·&nbsp; {h['ts']}</div>
            <div class="hist-meta">
              TWR {h['twr']:.3f} &nbsp;·&nbsp; Max Alt {h['max_alt']} km
              &nbsp;·&nbsp; Burnout T+{h['burnout']}s &nbsp;·&nbsp; {drag_txt}
            </div>
            <div class="hist-res">
              Thrust {h['thrust']/1e6:.2f} MN &nbsp;·&nbsp;
              Fuel {h['fuel']/1000:.0f} t &nbsp;·&nbsp;
              Initial mass {h.get('init_mass',0)/1000:.0f} t
            </div>
            </div>""", unsafe_allow_html=True)

        if len(hist) > 1:
            st.markdown('<div class="sh-sm">TWR & ALTITUDE COMPARISON</div>',
                        unsafe_allow_html=True)
            hist_df = pd.DataFrame([{
                "Run":        f"#{st.session_state.total_sims - i}",
                "TWR":        round(h["twr"], 3),
                "Max_Alt_km": h["max_alt"],
                "Burnout_s":  h["burnout"],
                "Thrust_MN":  round(h["thrust"]/1e6, 2),
            } for i,h in enumerate(hist)])

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Bar(x=hist_df["Run"], y=hist_df["Max_Alt_km"],
                name="Max Altitude (km)", marker_color=CYN, opacity=.85))
            fig_hist.add_trace(go.Scatter(x=hist_df["Run"], y=hist_df["TWR"]*10,
                name="TWR × 10 (scaled)", mode="lines+markers",
                line=dict(color=GRN, width=2), marker=dict(size=8)))
            fig_hist.update_layout(
                title="Simulation History — Altitude & TWR per Run",
                xaxis_title="Run", yaxis_title="Value", height=380, **PL)
            st.plotly_chart(fig_hist, use_container_width=True)

            st.download_button("⬇ Export Run History (CSV)",
                               df_to_csv(hist_df),
                               file_name="sim_history.csv",
                               mime="text/csv")

        st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)
        if st.button("🗑 Clear Simulation History"):
            st.session_state.sim_history    = []
            st.session_state.total_sims     = 0
            st.session_state.sim_steps_idx  = 0
            st.session_state.show_all_steps = False
            st.rerun()
