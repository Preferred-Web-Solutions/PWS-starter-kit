// Screenshots: first screen + full page at 1280 and 390. Usage: node shots.js /abs/site/ /abs/outdir pws_consent_<slug> page.html ...
const { chromium } = require('playwright');const path=require('path');const fs=require('fs');
const SITE=path.resolve(process.argv[2])+'/';const OUT=path.resolve(process.argv[3]);const KEY=process.argv[4];const pages=process.argv.slice(5);fs.mkdirSync(OUT,{recursive:true});
(async()=>{const b=await chromium.launch();
for(const [w,h,tag] of [[1280,800,'d'],[390,844,'m']]){const c=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:tag==='m'?2:1});
 await c.addInitScript(k=>localStorage.setItem(k,JSON.stringify({v:'1.0',choice:'reject',at:'x'})),KEY);const p=await c.newPage();
 for(const pg of pages){await p.goto('file://'+SITE+pg);await p.waitForTimeout(500);const n=pg.replace('.html','');
  await p.screenshot({path:`${OUT}/${n}-${tag}.png`});
  for(let y=0;y<20000;y+=500){await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(110)}await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(1500);
  await p.screenshot({path:`${OUT}/${n}-${tag}-full.png`,fullPage:true})}
 await c.close()}
await b.close()})();
