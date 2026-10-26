// PWS full test pass. Usage: node test.js /abs/path/to/site/ pws_consent_<slug>
// Checks every .html page: axe (WCAG 2.1 AA + best practice), storage/cookies/third-party requests,
// first Tab = skip link, SEO basics, broken internal links, section padding, phone overflow,
// tap targets at 390px, 200% zoom overflow and tiny text.
const { chromium } = require('playwright');
const fs=require('fs');const path=require('path');
const AXE=fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8');
const SITE=path.resolve(process.argv[2]||'site')+'/';const KEY=process.argv[3]||'pws_consent';
const pages=fs.readdirSync(SITE).filter(f=>f.endsWith('.html')).sort();
(async()=>{const b=await chromium.launch();let fails=0;const log=(...a)=>console.log(...a);const titles=new Map();
for(const pg of pages){
 const ctx=await b.newContext({viewport:{width:1280,height:900}});const reqs=[];
 const p=await ctx.newPage();p.on('request',r=>{if(!r.url().startsWith('file://')&&!r.url().startsWith('data:'))reqs.push(r.url())});
 await p.goto('file://'+SITE+pg);await p.waitForTimeout(400);
 const st0=await p.evaluate(()=>({ls:Object.keys(localStorage),ss:Object.keys(sessionStorage),ck:document.cookie}));
 const banner=await p.evaluate(()=>{const c=document.querySelector('.cc');return c&&!c.hidden});
 await p.keyboard.press('Tab');const t1=await p.evaluate(()=>document.activeElement.className);
 await p.addScriptTag({content:AXE});
 const ax=await p.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']}});return r.violations.map(v=>v.id+': '+v.nodes.length+' '+v.nodes.slice(0,3).map(n=>n.target.join(' ')).join(' || '))});
 await p.click('.cc button[data-c="reject"]');
 const st1=await p.evaluate(()=>({ls:Object.keys(localStorage),ck:document.cookie}));
 const cookies=await ctx.cookies();
 const ax2=await p.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']}});return r.violations.map(v=>v.id+': '+v.nodes.length+' '+v.nodes.slice(0,3).map(n=>n.target.join(' ')).join(' || '))});
 const seo=await p.evaluate(()=>({t:document.title,d:(document.querySelector('meta[name=description]')||{}).content,h1:document.querySelectorAll('h1').length,noalt:[...document.images].filter(i=>!i.hasAttribute('alt')).length,links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>!/^(https?:|tel:|sms:|mailto:|#)/.test(h))}));
 const broken=seo.links.filter(h=>!fs.existsSync(SITE+h.split('#')[0]));
 if(titles.has(seo.t)){broken.push('DUPLICATE TITLE with '+titles.get(seo.t))}titles.set(seo.t,pg);
 const pad=await p.evaluate(()=>[...document.querySelectorAll('main > section')].map(s=>{const c=getComputedStyle(s);return [s.className||s.getAttribute('aria-label'),parseFloat(c.paddingTop),parseFloat(c.paddingBottom)]}).filter(x=>x[1]<24&&x[2]<24));
 const allAx=[...new Set([...ax,...ax2])];
 log(`\n== ${pg}\n banner:${banner} firstTab:${t1}\n storage before:${JSON.stringify(st0)} after:${JSON.stringify(st1)} cookies:${cookies.length}\n requests:${reqs.length?reqs.join(','):'none'}\n axe:${allAx.length?allAx.join('\n   '):'0 violations'}\n title:${seo.t} | desc:${(seo.d||'').length} chars | h1:${seo.h1} | img no alt:${seo.noalt} | broken links:${broken.join(',')||'none'}\n low padding sections:${JSON.stringify(pad)}`);
 if(allAx.length||st0.ls.length||reqs.length||cookies.length||seo.h1!==1||broken.length||!banner||t1!=='skip')fails++;
 const m=await b.newContext({viewport:{width:390,height:844}});const mp=await m.newPage();await mp.addInitScript(k=>localStorage.setItem(k,JSON.stringify({v:'1.0',choice:'reject',at:'x'})),KEY);
 await mp.goto('file://'+SITE+pg);await mp.waitForTimeout(300);
 const mo=await mp.evaluate(()=>{const sw=document.documentElement.scrollWidth;const small=[];document.querySelectorAll('a,button,input,textarea,select,summary').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width)return;const inText=e.tagName==='A'&&e.closest('p,li,td,address,dd,figcaption')&&!e.classList.contains('btn')&&!e.closest('nav');if(inText)return;if(getComputedStyle(e).visibility==='hidden'||e.closest('[hidden]'))return;if(e.closest('nav')&&!e.closest('[data-tt]')&&e.offsetParent===null)return;if(r.width<43.5||r.height<43.5)small.push(e.tagName+'.'+e.className+' "'+e.textContent.trim().slice(0,18)+'" '+Math.round(r.width)+'x'+Math.round(r.height))});return {sw,small}});
 const z=await b.newContext({viewport:{width:640,height:900},deviceScaleFactor:2});const zp=await z.newPage();await zp.goto('file://'+SITE+pg);await zp.waitForTimeout(300);
 const zo=await zp.evaluate(()=>{const tiny=[];document.querySelectorAll('body *').forEach(e=>{if(e.children.length===0&&e.textContent.trim()&&e.getBoundingClientRect().width&&!e.closest('.sr-only')){const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<12)tiny.push(e.tagName+'.'+e.className+':'+fs)}});return {sw:document.documentElement.scrollWidth,tiny:[...new Set(tiny)].slice(0,5)}});
 log(` mobile scrollWidth:${mo.sw} small targets:${mo.small.length?mo.small.join('; '):'none'}\n 200% zoom scrollWidth:${zo.sw} tiny text:${zo.tiny.join(',')||'none'}`);
 if(mo.sw>390||zo.sw>640)fails++;
 await ctx.close();await m.close();await z.close();
}
console.log('\nPAGES',pages.length,'FAIL COUNT',fails);await b.close()})();
