import json
import tempfile
import webbrowser
from huffman_tree import tree_to_dict


# ─────────────────────────────────────────
# Open interactive HTML tree in browser
# ─────────────────────────────────────────
def show_tree(root, codes, stats):
    tree_json  = json.dumps(tree_to_dict(root))
    stats_json = json.dumps(stats)
    codes_json = json.dumps([
        {"char": repr(c).strip("'"), "code": codes[c]}
        for c in sorted(codes, key=lambda x: len(codes[x]))
    ])

    html = _build_html(tree_json, stats_json, codes_json)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                     mode="w", encoding="utf-8")
    tmp.write(html)
    tmp.close()
    webbrowser.open("file://" + tmp.name)


# ─────────────────────────────────────────
# HTML template
# ─────────────────────────────────────────
def _build_html(tree_json, stats_json, codes_json):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Huffman Tree Visualizer</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#0d0d0f; --surface:#16161a; --surface2:#1e1e24;
    --border:#2a2a35; --accent:#7c6af7; --accent2:#f97066;
    --green:#34d399; --text:#e8e8f0; --muted:#6b6b80;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:'Syne',sans-serif; background:var(--bg); color:var(--text);
          height:100vh; display:flex; flex-direction:column; overflow:hidden; }}

  /* Header */
  header {{ display:flex; align-items:center; gap:24px; padding:14px 28px;
            background:var(--surface); border-bottom:1px solid var(--border); flex-shrink:0; }}
  header h1 {{ font-size:18px; font-weight:800; letter-spacing:.03em; }}
  header h1 span {{ color:var(--accent); }}
  .pills {{ display:flex; gap:10px; margin-left:auto; flex-wrap:wrap; }}
  .pill {{ font-family:'JetBrains Mono',monospace; font-size:11px; padding:5px 12px;
           border-radius:20px; border:1px solid var(--border); background:var(--surface2); }}
  .pill b {{ color:var(--green); }}

  /* Tabs */
  .tabs {{ display:flex; padding:0 28px; background:var(--surface);
           border-bottom:1px solid var(--border); flex-shrink:0; }}
  .tab {{ padding:10px 20px; font-size:13px; font-weight:700; cursor:pointer;
          border-bottom:2px solid transparent; color:var(--muted); transition:all .2s; letter-spacing:.04em; }}
  .tab:hover {{ color:var(--text); }}
  .tab.active {{ color:var(--accent); border-bottom-color:var(--accent); }}

  /* Main */
  .main {{ display:flex; flex:1; overflow:hidden; }}

  /* Tree panel */
  #tree-panel {{ flex:1; position:relative; overflow:hidden; display:block; }}
  #tree-panel svg {{ width:100%; height:100%; cursor:grab; }}
  #tree-panel svg:active {{ cursor:grabbing; }}
  .node circle {{ stroke-width:2; transition:filter .2s; }}
  .node.leaf circle     {{ fill:var(--accent2); stroke:#ff9080; }}
  .node.internal circle {{ fill:var(--accent);  stroke:#a090ff; }}
  .node circle:hover {{ filter:brightness(1.3); }}
  .node text {{ font-family:'JetBrains Mono',monospace; font-size:11px; fill:white;
                text-anchor:middle; dominant-baseline:middle; pointer-events:none; font-weight:700; }}
  .node text.sub {{ font-size:9px; fill:rgba(255,255,255,.6); }}
  .link {{ fill:none; stroke:var(--border); stroke-width:1.5; }}
  .edge-label {{ font-family:'JetBrains Mono',monospace; font-size:10px; fill:var(--muted); font-weight:700; }}

  /* Tooltip */
  #tooltip {{ position:absolute; background:var(--surface2); border:1px solid var(--border);
              border-radius:8px; padding:10px 14px; font-size:12px;
              font-family:'JetBrains Mono',monospace; pointer-events:none;
              opacity:0; transition:opacity .15s; max-width:220px; line-height:1.8; }}
  #tooltip b {{ color:var(--accent); }}

  /* Zoom controls */
  .controls {{ position:absolute; bottom:20px; right:20px; display:flex; flex-direction:column; gap:6px; }}
  .ctrl-btn {{ width:36px; height:36px; background:var(--surface2); border:1px solid var(--border);
               color:var(--text); border-radius:8px; font-size:18px; cursor:pointer;
               display:flex; align-items:center; justify-content:center; transition:background .15s; }}
  .ctrl-btn:hover {{ background:var(--border); }}

  /* Legend */
  .legend {{ position:absolute; top:16px; left:16px; background:var(--surface);
             border:1px solid var(--border); border-radius:8px; padding:10px 14px;
             font-size:11px; display:flex; gap:14px; }}
  .leg-item {{ display:flex; align-items:center; gap:6px; }}
  .leg-dot {{ width:10px; height:10px; border-radius:50%; }}

  /* Codes panel */
  #codes-panel {{ display:none; flex:1; overflow:auto; padding:24px 28px; }}
  .codes-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:10px; }}
  .code-card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px;
                padding:12px 16px; display:flex; align-items:center; gap:12px; transition:border-color .2s; }}
  .code-card:hover {{ border-color:var(--accent); }}
  .code-char {{ font-size:22px; font-weight:800; min-width:32px; text-align:center; color:var(--accent2); }}
  .code-bits {{ font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--green); word-break:break-all; }}
  .code-len  {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); margin-top:2px; }}

  /* Encode panel */
  #encode-panel {{ display:none; flex:1; overflow:auto; padding:24px 28px; flex-direction:column; gap:18px; }}
  textarea {{ background:var(--surface); border:1px solid var(--border); border-radius:10px;
              color:var(--text); font-family:'JetBrains Mono',monospace; font-size:13px;
              padding:14px; resize:vertical; outline:none; transition:border-color .2s; min-height:100px; }}
  textarea:focus {{ border-color:var(--accent); }}
  .enc-btn {{ align-self:flex-start; padding:10px 24px; background:var(--accent); color:white;
              border:none; border-radius:8px; font-family:'Syne',sans-serif; font-size:13px;
              font-weight:700; cursor:pointer; transition:all .2s; letter-spacing:.04em; }}
  .enc-btn:hover {{ background:#9585ff; transform:translateY(-1px); }}
  #encode-output {{ background:var(--surface); border:1px solid var(--border); border-radius:10px;
                   padding:14px; font-family:'JetBrains Mono',monospace; font-size:12px;
                   word-break:break-all; line-height:1.8; min-height:60px; }}
  .bit-0 {{ color:var(--accent); }}
  .bit-1 {{ color:var(--accent2); }}
  .char-group {{ display:inline; }}
  .char-group:hover {{ background:rgba(255,255,255,.08); border-radius:3px; }}
  .enc-stats {{ display:flex; gap:16px; flex-wrap:wrap; }}
  .enc-stat {{ background:var(--surface); border:1px solid var(--border); border-radius:8px;
               padding:10px 16px; font-size:12px; font-family:'JetBrains Mono',monospace; }}
  .enc-stat span {{ color:var(--green); font-size:16px; font-weight:700; display:block; }}
</style>
</head>
<body>

<header>
  <h1>Huffman <span>Tree</span> Visualizer</h1>
  <div class="pills" id="pills"></div>
</header>

<div class="tabs">
  <div class="tab active" onclick="switchTab('tree')">🌲 Tree</div>
  <div class="tab" onclick="switchTab('codes')">📋 Code Table</div>
  <div class="tab" onclick="switchTab('encode')">⚡ Encoder</div>
</div>

<div class="main">

  <!-- TREE -->
  <div id="tree-panel">
    <svg id="svg"></svg>
    <div id="tooltip"></div>
    <div class="legend">
      <div class="leg-item"><div class="leg-dot" style="background:#f97066"></div> Leaf</div>
      <div class="leg-item"><div class="leg-dot" style="background:#7c6af7"></div> Internal</div>
    </div>
    <div class="controls">
      <button class="ctrl-btn" onclick="zoomIn()">+</button>
      <button class="ctrl-btn" onclick="zoomOut()">−</button>
      <button class="ctrl-btn" onclick="resetZoom()" style="font-size:13px">⌂</button>
    </div>
  </div>

  <!-- CODES -->
  <div id="codes-panel">
    <div class="codes-grid" id="codes-grid"></div>
  </div>

  <!-- ENCODER -->
  <div id="encode-panel">
    <p style="color:var(--muted);font-size:13px">Type text to see its Huffman encoding. Hover bit groups to identify characters.</p>
    <textarea id="enc-input" placeholder="Type something here..."></textarea>
    <button class="enc-btn" onclick="encodeText()">⚡ Encode</button>
    <div class="enc-stats" id="enc-stats"></div>
    <div id="encode-output"></div>
  </div>

</div>

<script>
const treeData  = {tree_json};
const statsData = {stats_json};
const codesData = {codes_json};

// Build codes lookup
const codesMap = {{}};
codesData.forEach(d => codesMap[d.char] = d.code);

// ── Stat pills
const pills = document.getElementById('pills');
[['Original', statsData.original_kb+' KB'],
 ['Compressed', statsData.compressed_kb+' KB'],
 ['Ratio', statsData.ratio+'%'],
 ['Chars', statsData.unique_chars]
].forEach(([k,v]) => pills.innerHTML += `<div class="pill">${{k}}: <b>${{v}}</b></div>`);

// ── Tabs
function switchTab(tab) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  ['tree','codes','encode'].forEach((t,i) => {{
    const p = document.getElementById(t+'-panel');
    p.style.display = 'none';
    if (t === tab) {{
      document.querySelectorAll('.tab')[i].classList.add('active');
      p.style.display = (t === 'tree') ? 'block' : 'flex';
    }}
  }});
}}

// ── Code cards
const grid = document.getElementById('codes-grid');
[...codesData].sort((a,b)=>a.code.length-b.code.length).forEach(d => {{
  grid.innerHTML += `
    <div class="code-card">
      <div class="code-char">${{d.char===' '?'·':d.char}}</div>
      <div>
        <div class="code-bits">${{d.code}}</div>
        <div class="code-len">${{d.code.length}} bit${{d.code.length>1?'s':''}}</div>
      </div>
    </div>`;
}});

// ── Encoder
function encodeText() {{
  const text = document.getElementById('enc-input').value;
  const out  = document.getElementById('encode-output');
  const stats = document.getElementById('enc-stats');
  if (!text) {{ out.innerHTML='<span style="color:var(--muted)">Enter text above.</span>'; return; }}
  let html='', total=0, skip=0;
  for (const ch of text) {{
    const key  = ch===' '?'\\u0020':ch;
    const code = codesMap[ch] || codesMap[key];
    if (!code) {{ skip++; continue; }}
    total += code.length;
    let bits='';
    for (const b of code) bits += `<span class="bit-${{b}}">${{b}}</span>`;
    html += `<span class="char-group" title="${{ch==' '?'SPACE':ch}} → ${{code}}">${{bits}} </span>`;
  }}
  out.innerHTML = html || '<span style="color:var(--muted)">No encodable characters.</span>';
  const orig = (text.length-skip)*8;
  stats.innerHTML = `
    <div class="enc-stat"><span>${{orig}}</span>Original bits</div>
    <div class="enc-stat"><span>${{total}}</span>Huffman bits</div>
    <div class="enc-stat"><span>${{orig>0?(100-total/orig*100).toFixed(1):0}}%</span>Saved</div>`;
}}
document.getElementById('enc-input').addEventListener('keyup', encodeText);

// ── D3 Tree
const svg   = d3.select('#svg');
const svgEl = document.getElementById('svg');
const g     = svg.append('g');
const tip   = document.getElementById('tooltip');
const zoom  = d3.zoom().scaleExtent([0.05,3]).on('zoom', e => g.attr('transform', e.transform));
svg.call(zoom);
function zoomIn()    {{ svg.transition().call(zoom.scaleBy, 1.3); }}
function zoomOut()   {{ svg.transition().call(zoom.scaleBy, 0.77); }}
function resetZoom() {{ svg.transition().call(zoom.transform, d3.zoomIdentity); drawTree(); }}

function drawTree() {{
  g.selectAll('*').remove();
  const W = svgEl.clientWidth||1200, H = svgEl.clientHeight||700;
  const root = d3.hierarchy(treeData, d => d.children&&d.children.length?d.children:null);
  let leaves=0; root.each(d => {{ if(!d.children) leaves++; }});
  const nodeW = Math.max(36, Math.min(60, (W-80)/leaves*0.8));
  const nodeH = Math.max(60, (H-100)/(root.height+1));
  d3.tree().nodeSize([nodeW*2, nodeH])(root);
  let minX=Infinity; root.each(d=>{{ minX=Math.min(minX,d.x); }});
  let maxX=-Infinity; root.each(d=>{{ maxX=Math.max(maxX,d.x); }});
  const offX = (W-(maxX-minX))/2 - minX;

  // Links
  g.selectAll('.link').data(root.links()).join('path').attr('class','link')
    .attr('d', d => {{
      const sx=d.source.x+offX, sy=d.source.y+50;
      const tx=d.target.x+offX, ty=d.target.y+50;
      return `M${{sx}},${{sy}} C${{sx}},${{(sy+ty)/2}} ${{tx}},${{(sy+ty)/2}} ${{tx}},${{ty}}`;
    }});

  // Edge labels
  g.selectAll('.edge-label').data(root.links()).join('text').attr('class','edge-label')
    .attr('x', d=>(d.source.x+d.target.x)/2+offX)
    .attr('y', d=>(d.source.y+d.target.y)/2+50)
    .attr('text-anchor','middle')
    .text(d => d.source.children ? (d.source.children[0]===d.target?'0':'1') : '');

  const r = Math.max(16, Math.min(26, nodeW*0.55));

  // Nodes
  const node = g.selectAll('.node').data(root.descendants()).join('g')
    .attr('class', d=>'node '+(d.data.isLeaf?'leaf':'internal'))
    .attr('transform', d=>`translate(${{d.x+offX}},${{d.y+50}})`)
    .style('cursor','pointer')
    .on('mouseover', (event,d) => {{
      const lines = d.data.isLeaf
        ? [`<b>Char:</b> ${{d.data.char===' '?'SPACE':d.data.char}}`,
           `<b>Freq:</b> ${{d.data.freq}}`,
           `<b>Code:</b> ${{d.data.code}}`,
           `<b>Bits:</b> ${{d.data.code.length}}`]
        : [`<b>Internal node</b>`,`<b>Freq sum:</b> ${{d.data.freq}}`,`<b>Depth:</b> ${{d.depth}}`];
      tip.innerHTML = lines.join('<br>');
      tip.style.opacity=1;
      tip.style.left=(event.offsetX+14)+'px';
      tip.style.top=(event.offsetY-10)+'px';
    }})
    .on('mousemove', e => {{ tip.style.left=(e.offsetX+14)+'px'; tip.style.top=(e.offsetY-10)+'px'; }})
    .on('mouseout',  () => {{ tip.style.opacity=0; }});

  node.append('circle').attr('r',r);
  node.append('text').attr('y', d=>d.data.isLeaf?-4:0)
    .text(d=>d.data.isLeaf?(d.data.char===' '?'·':d.data.char):d.data.freq)
    .style('font-size',`${{Math.max(9,r*.65)}}px`);
  node.filter(d=>d.data.isLeaf).append('text').attr('class','sub')
    .attr('y',r*.4).text(d=>d.data.freq).style('font-size',`${{Math.max(7,r*.42)}}px`);

  // Auto-fit
  const b=g.node().getBBox();
  const s=Math.min(0.95, Math.min(W/(b.width+40), H/(b.height+40)));
  svg.call(zoom.transform, d3.zoomIdentity
    .translate((W-b.width*s)/2-b.x*s, (H-b.height*s)/2-b.y*s).scale(s));
}}

window.addEventListener('load', drawTree);
window.addEventListener('resize', drawTree);
</script>
</body>
</html>"""