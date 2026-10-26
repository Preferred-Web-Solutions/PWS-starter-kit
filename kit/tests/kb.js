// Keyboard + consent + report-form checks shared by every PWS site.
// Usage: node kb.js /abs/path/to/site/ pws_consent_<slug>
const { chromium } = require('playwright');const path=require('path');
const S='file://'+path.resolve(process.argv[2]||'site')+'/';const KEY=process.argv[3]||'pws_consent';
(async()=>{const b=await chromium.launch();
const c=await b.newContext({viewport:{width:1280,height:900}});const p=await c.newPage();await p.goto(S+'index.html');
const a=async()=>p.evaluate(()=>{const e=document.activeElement;return (e.className||e.tagName)+'|'+(e.textContent||'').trim().slice(0,24)});
await p.keyboard.press('Tab');const t1=await a();await p.keyboard.press('Tab');const t2=await a();
await p.keyboard.press('Enter');const after=await p.evaluate(k=>[document.querySelector('.cc').hidden,localStorage.getItem(k)],KEY);
await p.focus('[data-cookie-settings]');await p.keyboard.press('Enter');const reopen=await p.evaluate(()=>[document.querySelector('.cc').hidden,document.activeElement.id,document.querySelector('.cc .manage').hidden]);
await p.click('.cc [data-c="save"]');const back=await a();
const ol=await p.evaluate(()=>{const l=document.querySelector('main a');l.focus();const s=getComputedStyle(l);return s.outlineStyle+' '+s.outlineWidth});
console.log('skip/banner/cookie settings',{t1,t2,after,reopen,back,focusOutline:ol});
await p.route('https://formspree.io/**',r=>r.fulfill({status:200,body:'{"ok":true}',contentType:'application/json'}));
await p.goto(S+'report.html');await p.click('#rf button');const empty=await p.evaluate(()=>[document.getElementById('rmsg').textContent,document.activeElement.name]);
await p.fill('[name=email]','a@b.co');await p.fill('[name=message]','test');await p.click('#rf button');await p.waitForTimeout(300);
console.log('report form',{empty,sent:await p.evaluate(()=>[document.getElementById('rdone').hidden,document.activeElement.id])});
const rc=await b.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});const rp=await rc.newPage();await rp.goto(S+'index.html');await rp.waitForTimeout(200);
console.log('reduced motion: hidden [data-reveal] count',await rp.evaluate(()=>[...document.querySelectorAll('[data-reveal]')].filter(e=>getComputedStyle(e).opacity!=='1').length));
await b.close()})();
