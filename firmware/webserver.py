# Mini web server non bloccante: serve una dashboard e un endpoint JSON.
# Tiene in RAM uno storico circolare degli ultimi campioni.
import socket
import json

_PAGE = """<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aria Monitor</title>
<style>
 :root{--bg:#0b0d12;--card:#161a23;--card2:#1b2030;--tx:#eef1f7;--mut:#8b93a7;--line:#252b3a}
 *{box-sizing:border-box}
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:var(--bg);color:var(--tx)}
 .wrap{max-width:600px;margin:0 auto;padding:24px 16px 40px}
 .top{display:flex;align-items:baseline;justify-content:space-between;gap:8px;flex-wrap:wrap}
 h1{font-size:22px;font-weight:700;margin:0;letter-spacing:.2px}
 .upd{font-size:12px;color:var(--mut)}
 .dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#2dd4bf;margin-right:5px;vertical-align:middle}
 .dot.off{background:#f43f5e}
 .hero{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;margin-top:16px;position:relative;overflow:hidden}
 .hlabel{font-size:13px;color:var(--mut);letter-spacing:.5px;text-transform:uppercase}
 .co2{font-size:64px;font-weight:800;line-height:1.05;margin:2px 0 4px;transition:color .4s}
 .co2 small{font-size:24px;font-weight:600;color:var(--mut)}
 .badge{display:inline-block;font-size:14px;font-weight:700;padding:7px 14px;border-radius:999px;transition:all .4s}
 svg{width:100%;height:90px;margin-top:14px;display:block}
 .grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
 .card{background:var(--card2);border:1px solid var(--line);border-radius:16px;padding:16px}
 .card .l{font-size:13px;color:var(--mut)}
 .card .v{font-size:30px;font-weight:700;margin-top:2px}
 .btn{width:100%;margin-top:16px;padding:15px;border:0;border-radius:14px;background:#3b82f6;color:#fff;font-size:16px;font-weight:700;cursor:pointer;transition:background .2s}
 .btn:active{background:#2563eb}
 .btn:disabled{opacity:.6}
 .foot{text-align:center;color:var(--mut);font-size:12px;margin-top:16px}
</style></head><body><div class="wrap">
 <div class="top">
   <h1>Aria Monitor</h1>
   <div class="upd"><span id="dot" class="dot"></span><span id="upd">connessione...</span></div>
 </div>

 <div class="hero">
   <div class="hlabel">Anidride carbonica</div>
   <div class="co2" id="co2wrap"><span id="co2">--</span> <small>ppm</small></div>
   <span class="badge" id="badge">--</span>
   <svg id="spark" viewBox="0 0 320 90" preserveAspectRatio="none"></svg>
 </div>

 <div class="grid">
   <div class="card"><div class="l">Temperatura</div><div class="v"><span id="t">--</span>&deg;C</div></div>
   <div class="card"><div class="l">Umidita</div><div class="v"><span id="rh">--</span>%</div></div>
 </div>

 <button class="btn" id="btn" onclick="refresh(true)">Aggiorna ora</button>
 <div class="foot">Aggiornamento automatico ogni 5s &middot; avviso email sopra <span id="al">--</span> ppm</div>
</div>
<script>
function color(co2,warn,alarm){
 if(co2>=alarm) return ['#f43f5e','rgba(244,63,94,.15)','#f43f5e','AERARE SUBITO'];
 if(co2>=warn)  return ['#f59e0b','rgba(245,158,11,.15)','#f59e0b','Aria mediocre'];
 return ['#22c55e','rgba(34,197,94,.15)','#22c55e','Aria buona'];
}
async function refresh(manual){
 const btn=document.getElementById('btn');
 if(manual){btn.disabled=true;btn.textContent='Aggiorno...';}
 try{
  const r=await fetch('/data',{cache:'no-store'});const d=await r.json();
  document.getElementById('co2').textContent=d.co2;
  document.getElementById('t').textContent=(typeof d.temp==='number')?d.temp.toFixed(1):d.temp;
  document.getElementById('rh').textContent=(typeof d.rh==='number')?Math.round(d.rh):d.rh;
  document.getElementById('al').textContent=d.alarm;
  const c=color(d.co2,d.warn,d.alarm);
  document.getElementById('co2').style.color=c[0];
  const b=document.getElementById('badge');
  b.textContent=d.status&&d.status!=='Aria buona'?d.status:c[3];
  b.style.color=c[2];b.style.background=c[1];
  const h=d.history||[];
  if(h.length>1){
   const mn=Math.min(...h),mx=Math.max(...h,mn+50),rng=(mx-mn)||1;
   const pts=h.map((v,i)=>(i*320/(h.length-1)).toFixed(1)+','+(85-((v-mn)/rng)*78).toFixed(1)).join(' ');
   document.getElementById('spark').innerHTML='<polyline fill="none" stroke="'+c[0]+'" stroke-width="2.5" stroke-linejoin="round" points="'+pts+'"/>';
  }
  const now=new Date();
  document.getElementById('upd').textContent='aggiornato '+now.toLocaleTimeString('it-IT');
  document.getElementById('dot').className='dot';
 }catch(e){
  document.getElementById('upd').textContent='riconnessione...';
  document.getElementById('dot').className='dot off';
 }
 if(manual){btn.disabled=false;btn.textContent='Aggiorna ora';}
}
refresh(false);setInterval(()=>refresh(false),5000);
</script></body></html>"""


class WebServer:
    def __init__(self, cfg, history_len=120):
        self.cfg = cfg
        self.history = []
        self.history_len = history_len
        self.latest = {"co2": 0, "temp": 0.0, "rh": 0.0, "status": "avvio"}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", 80))
        self.sock.listen(2)
        self.sock.settimeout(0)   # non bloccante

    def update(self, co2, temp, rh, status):
        self.latest = {"co2": co2, "temp": temp, "rh": rh, "status": status}
        self.history.append(co2)
        if len(self.history) > self.history_len:
            self.history.pop(0)

    def _data_json(self):
        d = dict(self.latest)
        d["history"] = self.history
        d["warn"] = self.cfg.CO2_WARN
        d["alarm"] = self.cfg.CO2_ALARM
        return json.dumps(d)

    def _send_all(self, cl, data):
        # invia TUTTI i byte, anche se send() ne accetta pochi per volta
        if isinstance(data, str):
            data = data.encode()
        view = memoryview(data)
        while view:
            try:
                n = cl.send(view)
            except OSError:
                return
            if not n:
                return
            view = view[n:]

    def poll(self):
        """Da chiamare spesso nel loop: gestisce al piu' una richiesta."""
        try:
            cl, _ = self.sock.accept()
        except OSError:
            return
        try:
            cl.settimeout(2)
            req = cl.recv(256)
            if req and b"GET /data" in req:
                body = self._data_json().encode()
                ctype = "application/json"
            else:
                body = _PAGE.encode()
                ctype = "text/html"
            hdr = ("HTTP/1.0 200 OK\r\nContent-Type: %s\r\n"
                   "Content-Length: %d\r\nConnection: close\r\n\r\n" % (ctype, len(body)))
            self._send_all(cl, hdr)
            self._send_all(cl, body)
        except Exception:
            pass
        finally:
            cl.close()
