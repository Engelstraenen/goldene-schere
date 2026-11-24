// Wächter Lintorf-Bilder (24.11.2026). Nutzt SB aus sjinn_queue.js. Limit per MutationObserver, Toasts nie entfernen.
(function(){
const wk=new Worker(URL.createObjectURL(new Blob(['onmessage=e=>setTimeout(()=>postMessage(e.data),e.data.ms)'])));
const cb={};let n=0;wk.onmessage=e=>{cb[e.data.id]();delete cb[e.data.id]};
window.wsleep=ms=>new Promise(r=>{const id=++n;cb[id]=r;wk.postMessage({id,ms})});
SB.limN=SB.limN||0;
if(!SB.mo){SB.mo=new MutationObserver(ms=>{for(const m of ms)for(const nd of m.addedNodes){const t=(nd.textContent||'');if(/maximum limit|concurrent task/i.test(t))SB.limN++;}});SB.mo.observe(document.body,{childList:true,subtree:true});}
SB.seen=id=>document.body.innerText.includes(id+' ')||[...document.querySelectorAll('img[alt]')].some(i=>i.alt.startsWith(id+' '));
SB.go=async()=>{const my=SB.runId=Date.now();SB.G={log:[],done:{}};const ta=()=>document.querySelector('textarea');
 for(const j of SB.GQ){let t=0;
  while(SB.runId===my&&!SB.seen(j.id)&&t<120){t++;
   const dlg=document.querySelector('[role=dialog]');if(dlg&&!/Upload images/.test(dlg.innerText)){const c=[...dlg.querySelectorAll('button')].find(b=>/Close/i.test(b.getAttribute('aria-label')||b.innerText));c&&c.click();await wsleep(800);}
   await SB.clearRefs();const r=await SB.setRef(j.ref);await SB.setAR(j.ar);await wsleep(700);
   const bar=SB.bar();if(!/Unlimited · On/.test(bar)||!/0 credits/.test(bar)||!bar.includes(j.ar)||!/4K/.test(bar)){SB.G.log.push(j.id+' BAR '+bar+' ref '+r);await SB.setup(j.ar,'4K');await wsleep(60000);continue;}
   Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta(),j.prompt);ta().dispatchEvent(new Event('input',{bubbles:true}));await wsleep(1200);
   const l0=SB.limN;const gb=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Generate');gb&&gb.click();await wsleep(15000);
   if(SB.seen(j.id)){SB.G.log.push(j.id+' OK '+new Date().toLocaleTimeString());break;}
   SB.G.log.push(j.id+(SB.limN>l0?' LIMIT ':' none ')+new Date().toLocaleTimeString());await wsleep(45000);}
  SB.G.done[j.id]=SB.seen(j.id);}
 if(SB.runId===my)SB.G.msg='fertig';};
})();
