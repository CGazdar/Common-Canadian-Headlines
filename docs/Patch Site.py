"""Navbar and front-page table update for Common Canadian Headliners.

Run from the project folder (the one that contains docs/):

    python patch_site.py            show what would change
    python patch_site.py --apply    change the files (originals saved as *.bak in docs/)

1. Navbar on all five pages: "Data Downloads" and "Sources" become their own tabs
   (the Data dropdown is removed).
2. Front page: a table under the map. Province, Term, Outlet, Leaning (coloured dot), Mentions,
   plus a per-100,000 rate and the headlines analysed. It follows the chosen terms, the period
   (slider / all quarters) and the selected province. Click a column heading to sort.

It only edits the navbar on about.html, data.html, sources.html and province.html, so any text
you wrote on those pages is left alone. Safe to run twice.
"""
import re
import shutil
import sys
from pathlib import Path

DOCS = Path("docs")
APPLY = "--apply" in sys.argv

DD = re.compile(r'<div class="dd">.*?</div></div>', re.S)


def nav_tabs(old_dd):
    cur_data = 'href="data.html" aria-current="page"' in old_dd
    cur_src = 'href="sources.html" aria-current="page"' in old_dd
    return ('<a class="tab" href="data.html"%s>Data Downloads</a>'
            '<a class="tab" href="sources.html"%s>Sources</a>') % (
        ' aria-current="page"' if cur_data else "", ' aria-current="page"' if cur_src else "")


def patch_nav(text):
    m = DD.search(text)
    if not m:
        return text, False
    return text[:m.start()] + nav_tabs(m.group(0)) + text[m.end():], True


# ---------------------------------------------------------------- front-page table
CSS = '''
/* results table under the map */
.tblwrap{max-height:430px;overflow:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);margin-top:16px}
table.rt{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}
.rt th{position:sticky;top:0;z-index:1;background:var(--card);text-align:left;font-weight:600;color:var(--mute);padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
.rt th button{border:0;background:none;padding:0;font:inherit;color:inherit;cursor:pointer}
.rt th button:hover,.rt th[aria-sort] button{color:var(--fg)}
.rt th[aria-sort] button::after{content:" \\25B2";font-size:9px}
.rt th[aria-sort=descending] button::after{content:" \\25BC"}
.rt td{padding:7px 12px;border-bottom:1px solid var(--line)}
.rt tr:last-child td{border-bottom:0}
.rt tr.pg td{border-top:2px solid var(--line)}
.rt .n{text-align:right}
.rt td.nm{font-weight:600}
.ldot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;vertical-align:-1px}
#tblnote{margin-top:8px}
@media(max-width:760px){.rt{font-size:13px}.rt th,.rt td{padding:7px 8px}}
'''

HTML_ANCHOR = '  <h2 class="viz" id="viz"></h2>\n'
HTML_NEW = ('  <h2 class="viz" id="tblh"></h2>\n'
            '  <div class="tblwrap" id="tblwrap" hidden><table class="rt" id="rt"></table></div>\n'
            '  <p class="note" id="tblnote"></p>\n') + HTML_ANCHOR

JS = r'''
// ---- results table: province, term, outlet, leaning, mentions
const PORDER=["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL","TER","NAT"];   // west to east, the territories, then national outlets
const LORDER={left:0,lean_left:1,center:2,lean_right:3,right:4};
let tsort={k:"prov",dir:1};
function tableRows(){
  const rows=[],idx=sel>=0?[sel]:Q.map((_,i)=>i);
  terms.forEach(t=>Object.keys(D.outlets).forEach(o=>{
    const m=D.outlets[o],p=REG[m.province]||m.province;
    if(prov!=="NAT"&&p!==prov)return;
    let n=0,h=0,any=false;
    idx.forEach(i=>{
      const r=D.rates[t]&&D.rates[t][o]?D.rates[t][o][i]:null,T=D.totals&&D.totals[o]?D.totals[o][i]:null;
      if(r===null||r===undefined||!T)return;
      any=true;n+=Math.round(r/1e5*T);h+=T;                // rates are stored rounded, so the count is rebuilt and rounded to a whole number
    });
    if(any)rows.push({p,t,o,name:m.name,group:m.group,leaning:m.leaning,n,h,rate:h?n/h*1e5:null});
  }));
  return rows;
}
function drawTable(){
  const wrap=$("tblwrap"),head=$("tblh"),note=$("tblnote"),tb=$("rt");
  if(!terms.length){head.innerHTML="Table<small>(Select term to Display)</small>";wrap.hidden=true;note.textContent="";return}
  const rows=tableRows(),k=tsort.k;
  const key={prov:r=>PORDER.indexOf(r.p),term:r=>terms.indexOf(r.t),outlet:r=>r.name.toLowerCase(),lean:r=>(LORDER[r.leaning]!==undefined?LORDER[r.leaning]:2),n:r=>r.n,rate:r=>r.rate===null?-1:r.rate,h:r=>r.h};
  const order=[k,"prov","term","lean","outlet"];
  rows.sort((a,b)=>{for(let j=0;j<order.length;j++){const f=key[order[j]],x=f(a),y=f(b);if(x<y)return j===0?-tsort.dir:-1;if(x>y)return j===0?tsort.dir:1}return 0});
  const period=sel>=0?Q[sel]:"all quarters";
  head.innerHTML="Table<small>"+rows.length.toLocaleString()+" rows · "+period+(prov!=="NAT"?" · "+NAMES[prov]:"")+"</small>";
  const col=(id,label,cls)=>`<th class="${cls||""}"${tsort.k===id?` aria-sort="${tsort.dir>0?"ascending":"descending"}"`:""}><button type="button" data-k="${id}">${label}</button></th>`;
  let html="<thead><tr>"+col("prov","Province")+col("term","Term")+col("outlet","Outlet")+col("lean","Leaning")+col("n","Mentions","n")+col("rate","Per 100,000","n")+col("h","Headlines","n")+"</tr></thead><tbody>";
  let prevP=null;
  rows.forEach(r=>{
    const pn=r.p==="NAT"?"National":NAMES[r.p],ll=LEANLABEL[r.leaning]||GNAME[r.group];
    html+=`<tr${k==="prov"&&prevP!==null&&r.p!==prevP?' class="pg"':""}><td>${pn}</td><td>${cap(r.t)}</td><td class="nm">${r.name}</td>`
      +`<td><span class="ldot" style="background:var(--${r.group})"></span>${ll}</td>`
      +`<td class="n">${r.n.toLocaleString()}</td><td class="n">${r.rate!==null&&r.rate>=1000?Math.round(r.rate).toLocaleString():fmt(r.rate)}</td><td class="n">${r.h.toLocaleString()}</td></tr>`;
    prevP=r.p;
  });
  tb.innerHTML=html+"</tbody>";
  wrap.hidden=!rows.length;
  note.textContent=rows.length
    ?"Mentions count the headlines containing the term in our sample (at most 1,500 per outlet per quarter), so compare outlets by the per-100,000 rate."+(prov!=="NAT"?" Showing "+NAMES[prov]+" only; choose “All of Canada” on the map for every province.":"")
    :"No outlets with data for this selection.";
}
$("rt").addEventListener("click",e=>{
  const b=e.target.closest("button[data-k]");if(!b)return;
  const k=b.dataset.k;
  if(tsort.k===k)tsort.dir=-tsort.dir;else{tsort.k=k;tsort.dir=(k==="n"||k==="rate"||k==="h")?-1:1}
  drawTable();
});
'''


def patch_index(text):
    text, _ = patch_nav(text)
    if "id=\"tblh\"" not in text:
        assert HTML_ANCHOR in text, "index.html: could not find the Visualizations heading"
        text = text.replace(HTML_ANCHOR, HTML_NEW, 1)
        assert "</style>" in text
        text = text.replace("</style>", CSS + "</style>", 1)
        anchor = "function setSel(i){"
        assert anchor in text, "index.html: could not find setSel"
        text = text.replace(anchor, JS + anchor, 1)
        a = "drawChips();drawMap();drawCharts();"
        assert a in text, "index.html: could not find the draw() line"
        text = text.replace(a, "drawChips();drawMap();drawTable();drawCharts();", 1)
    return text


def run(name, fn):
    p = DOCS / name
    if not p.exists():
        print(f"{name}: not found, skipped")
        return
    old = p.read_text(encoding="utf-8")
    new = fn(old)
    if isinstance(new, tuple):
        new = new[0]
    if new == old:
        print(f"{name}: nothing to change")
        return
    print(f"{name}: " + ("updated" if APPLY else "would be updated"))
    if APPLY:
        shutil.copy(p, str(p) + ".bak")
        p.write_text(new, encoding="utf-8")


run("index.html", patch_index)
for n in ("province.html", "about.html", "data.html", "sources.html"):
    run(n, patch_nav)
if not APPLY:
    print("Dry run. Add --apply to save.")