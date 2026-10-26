// Page weight after scrolling the whole page (lazy images load). Usage: node weight.js /abs/site/ index.html other.html ...
const { chromium } = require('playwright');const fs=require('fs');const path=require('path');
const SITE=path.resolve(process.argv[2]||'site')+'/';const pages=process.argv.slice(3).length?process.argv.slice(3):['index.html'];
(async()=>{const b=await chromium.launch();
for(const [w,h] of [[1280,900],[390,844]]){for(const pg of pages){
 const c=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:w<500?3:1});const p=await c.newPage();const files=new Map();
 p.on('requestfinished',r=>{const u=r.url();if(u.startsWith('file://')){const f=decodeURIComponent(u.slice(7));try{files.set(f,fs.statSync(f).size)}catch(e){}}});
 await p.goto('file://'+SITE+pg);await p.waitForTimeout(300);
 for(let y=0;y<16000;y+=400){await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(40)}await p.waitForTimeout(500);
 const tot=[...files.values()].reduce((a,b)=>a+b,0);const imgs=[...files].filter(([f])=>/\.(jpe?g|webp|png|avif)$/.test(f)).sort((a,b)=>b[1]-a[1]);
 console.log(w,pg,'total',Math.round(tot/1024)+'KB','largest img',imgs[0]&&imgs[0][0].split('/').pop()+' '+Math.round(imgs[0][1]/1024)+'KB');await c.close()}}
await b.close()})();
