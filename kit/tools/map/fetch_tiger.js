// Paste into the built-in browser's javascript tool while on
// https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer?f=pjson
// (same origin, so no CORS problems). Set ENV to the map's bounding box: lon0,lat0,lon1,lat1.
// Then download window.__tiger as one JSON file (ask the user before downloading).
const B='https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/';
const ENV='-82.24,40.60,-81.56,41.06';
const L={primary:['Transportation',2,'NAME,MTFCC'],secondary:['Transportation',6,'NAME,MTFCC'],local:['Transportation',8,'NAME,MTFCC'],
 hline:['Hydro',0,'NAME'],harea:['Hydro',1,'NAME'],places:['Places_CouSub_ConCity_SubMCD',4,'NAME'],cdp:['Places_CouSub_ConCity_SubMCD',5,'NAME'],
 cousub:['Places_CouSub_ConCity_SubMCD',1,'NAME,COUNTY'],counties:['State_County',1,'NAME'],military:['Special_Land_Use_Areas',3,'NAME']};
const out={};const log={};
for(const [k,[svc,lyr,fields]] of Object.entries(L)){out[k]=[];let off=0;
 for(let p=0;p<40;p++){const q=new URLSearchParams({geometry:ENV,geometryType:'esriGeometryEnvelope',inSR:'4326',spatialRel:'esriSpatialRelIntersects',outFields:fields,returnGeometry:'true',outSR:'4326',geometryPrecision:'5',maxAllowableOffset:k==='local'?'0.00008':'0.00004',f:'geojson',resultOffset:String(off),resultRecordCount:'1000'});
  try{const r=await fetch(B+svc+'/MapServer/'+lyr+'/query?'+q);const j=await r.json();const fs=j.features||[];out[k].push(...fs);off+=fs.length;
   if(!fs.length||!(j.exceededTransferLimit||(j.properties&&j.properties.exceededTransferLimit))&&fs.length<1000)break}catch(e){log[k]='ERR '+e;break}}
 log[k]=(log[k]||'')+out[k].length}
window.__tiger=out;log
// download: const bl=new Blob([JSON.stringify(window.__tiger)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(bl);a.download='tiger.json';document.body.appendChild(a);a.click();a.remove();
