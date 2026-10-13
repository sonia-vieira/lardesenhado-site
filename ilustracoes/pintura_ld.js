// Pincel do Lar Desenhado (v2, 13/10/2026): guache chapado sobre papel creme, desenhado em código.
// Nenhuma imagem de IA. A mesma semente dá sempre a mesma pintura.
// Uso: <canvas id="c" width="1080" height="1350">, depois este arquivo, depois a cena.
// No fim da cena: window.__pronto = true (o renderizar_canvas.py espera por isso).
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const W = cv.width, H = cv.height;

// Paleta LD (prancha v6)
const P = {
  creme:'#FAF7F1', areia:'#E9DCCB', terracota:'#C36E4D', terraEsc:'#A85A3C',
  salvia:'#899883', salviaEsc:'#5F6E5A', blush:'#DFA58F', dourado:'#D3A55F', marrom:'#60524B'
};

let semente = 139;
function semear(n){ semente = n; }
function rnd(){ semente|=0; semente=semente+0x6D2B79F5|0; let t=Math.imul(semente^semente>>>15,1|semente); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }
const r = (a,b)=>a+(b-a)*rnd();

function ruido(n){ const v=[]; for(let i=0;i<n;i++) v.push(rnd()*2-1); return t=>{ const x=((t%1)+1)%1*(n-1), i=Math.floor(x), f=x-i, g=f*f*(3-2*f); return v[i]*(1-g)+v[Math.min(i+1,n-1)]*g; }; }
function hex(c){ return [parseInt(c.slice(1,3),16),parseInt(c.slice(3,5),16),parseInt(c.slice(5,7),16)]; }
function mistura(c, k){ // k>0 clareia, k<0 escurece; devolve #rrggbb
  const [R,G,B]=hex(c), f=v=>Math.max(0,Math.min(255,Math.round(k>0? v+(255-v)*k : v*(1+k))));
  return '#'+[f(R),f(G),f(B)].map(v=>v.toString(16).padStart(2,'0')).join('');
}

// Contorno de um polígono com a borda tremida (a mão do pintor)
function contorno(pts, amp){
  const n=ruido(24), out=[], tot=pts.length;
  for(let i=0;i<tot;i++){
    const a=pts[i], b=pts[(i+1)%tot], passos=Math.max(4,Math.round(Math.hypot(b[0]-a[0],b[1]-a[1])/12));
    for(let k=0;k<passos;k++){
      const t=k/passos, x=a[0]+(b[0]-a[0])*t, y=a[1]+(b[1]-a[1])*t;
      const d=n((i+t)/tot)*amp + r(-amp,amp)*0.25;
      const nx=-(b[1]-a[1]), ny=(b[0]-a[0]), L=Math.hypot(nx,ny)||1;
      out.push([x+nx/L*d, y+ny/L*d]);
    }
  }
  return out;
}
function caminho(pts){ ctx.beginPath(); pts.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1])); ctx.closePath(); }

// Uma camada de tinta: a mancha, a pincelada seca larga por dentro e a borda quase invisível
function pinta(pts, cor, {amp=6, angulo=0, seca=0.5, alfa=0.95}={}){
  const borda=contorno(pts, amp);
  ctx.save(); caminho(borda); ctx.globalAlpha=alfa; ctx.fillStyle=cor; ctx.fill(); ctx.clip();
  const xs=borda.map(p=>p[0]), ys=borda.map(p=>p[1]);
  const x0=Math.min(...xs)-40, x1=Math.max(...xs)+40, y0=Math.min(...ys)-40, y1=Math.max(...ys)+40;
  const c=Math.cos(angulo), sn=Math.sin(angulo), diag=Math.hypot(x1-x0,y1-y0);
  for(let i=0;i<diag/7;i++){
    const off=-diag/2+i*7+r(-2,2), cx=(x0+x1)/2, cy=(y0+y1)/2;
    let pos=-diag/2;
    while(pos<diag/2){
      const len=r(30,180), gap=r(4,40)*seca;
      const ax=cx+c*pos-sn*off, ay=cy+sn*pos+c*off, bx=cx+c*(pos+len)-sn*off, by=cy+sn*(pos+len)+c*off;
      ctx.globalAlpha=r(0.05,0.2);
      ctx.strokeStyle= rnd()<0.5? mistura(cor, r(0.1,0.35)) : mistura(cor, -r(0.05,0.2));
      ctx.lineWidth=r(3,9);
      if(rnd()<0.07*seca){ ctx.strokeStyle=P.creme; ctx.globalAlpha=r(0.2,0.45); ctx.lineWidth=r(1.5,4); }
      ctx.lineCap='round';
      ctx.beginPath(); ctx.moveTo(ax,ay); ctx.lineTo(bx,by); ctx.stroke();
      pos+=len+gap;
    }
  }
  ctx.restore();
  ctx.save(); ctx.globalAlpha=0.16; ctx.strokeStyle=mistura(cor,-0.15); ctx.lineWidth=2.5;
  caminho(contorno(pts, amp*0.8)); ctx.stroke(); ctx.restore();
}

// Traço solto de pincel (linha de cota, varal, cabo)
function traco(x1,y1,x2,y2,cor,larg=3,alfa=0.8){
  ctx.save(); ctx.globalAlpha=alfa; ctx.strokeStyle=cor; ctx.lineWidth=larg; ctx.lineCap='round';
  const n=ruido(8); ctx.beginPath();
  for(let i=0;i<=20;i++){ const t=i/20, x=x1+(x2-x1)*t, y=y1+(y2-y1)*t, d=n(t)*1.6;
    const nx=-(y2-y1), ny=(x2-x1), L=Math.hypot(nx,ny)||1; i?ctx.lineTo(x+nx/L*d,y+ny/L*d):ctx.moveTo(x+nx/L*d,y+ny/L*d); }
  ctx.stroke(); ctx.restore();
}
// Escrita à mão leve (só para medidas e rótulos curtos)
function escreve(txt,x,y,{tam=34,cor=P.terraEsc,alinhar='left',alfa=0.9}={}){
  ctx.save(); ctx.globalAlpha=alfa; ctx.fillStyle=cor; ctx.textAlign=alinhar;
  ctx.font=`italic 600 ${tam}px Georgia, serif`; ctx.fillText(txt,x,y); ctx.restore();
}

const ret=(x,y,w,h)=>[[x,y],[x+w,y],[x+w,y+h],[x,y+h]];
function arco(cx, base, w, h, n=28){
  const pts=[[cx-w/2,base]];
  for(let i=0;i<=n;i++){ const a=Math.PI+Math.PI*i/n; pts.push([cx+Math.cos(a)*w/2, base-h+w/2+Math.sin(a)*w/2]); }
  pts.push([cx+w/2,base]); return pts;
}
function circ(cx,cy,rx,ry,n=36){ const p=[]; for(let i=0;i<n;i++){const a=2*Math.PI*i/n; p.push([cx+Math.cos(a)*rx, cy+Math.sin(a)*ry]);} return p; }
function estrela(cx,cy,R){ const p=[]; for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5, rr=i%2?R*0.45:R; p.push([cx+Math.cos(a)*rr, cy+Math.sin(a)*rr]);} return p; }
function setor(cx,cy,R,a0,a1,n=12){ const p=[[cx,cy]]; for(let i=0;i<=n;i++){const a=a0+(a1-a0)*i/n; p.push([cx+Math.cos(a)*R, cy+Math.sin(a)*R]);} return p; }

// O papel creme com grão e fibras
function papel(){
  ctx.fillStyle=P.creme; ctx.fillRect(0,0,W,H);
  for(let i=0;i<26000;i++){ ctx.globalAlpha=r(0.02,0.07); ctx.fillStyle=rnd()<0.5?'#cbbfae':'#ffffff'; ctx.fillRect(r(0,W),r(0,H),r(1,2.5),r(1,2.5)); }
  for(let i=0;i<500;i++){ ctx.globalAlpha=r(0.03,0.08); ctx.strokeStyle='#bfb19d'; ctx.lineWidth=0.6; const x=r(0,W),y=r(0,H); ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+r(-14,14),y+r(-6,6)); ctx.stroke(); }
  ctx.globalAlpha=1;
}
function assinatura(){ escreve('Lar Desenhado', 60, H-28, {tam:30, alfa:0.75}); }
