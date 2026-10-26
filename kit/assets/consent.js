/* PWS consent banner. Include as <script src="assets/consent.js" data-key="pws_consent_<slug>"></script>.
   Stores only the visitor's choice in localStorage. No optional tools are loaded by default;
   if a site ever adds one, gate it with PWSConsent.allowed() and update the Cookie Policy first. */
(function(){
var me=document.currentScript,KEY=(me&&me.getAttribute('data-key'))||'pws_consent',VER=(me&&me.getAttribute('data-version'))||'1.0';
function get(){try{var v=JSON.parse(localStorage.getItem(KEY));return v&&v.v===VER?v:null}catch(e){return null}}
function save(c){try{localStorage.setItem(KEY,JSON.stringify({v:VER,choice:c,at:new Date().toISOString()}))}catch(e){}}
window.PWSConsent={allowed:function(){var v=get();return !!(v&&v.choice==='all')}};
var box=document.createElement('div');box.className='cc';box.hidden=true;box.setAttribute('role','dialog');box.setAttribute('aria-modal','false');box.setAttribute('aria-labelledby','ccT');
box.innerHTML='<h2 id="ccT" tabindex="-1">Your privacy</h2><p>No tracking or ads here. This site only remembers your choice.</p>'+
'<div class="btns"><button type="button" class="pri" data-c="all">Accept all</button><button type="button" class="pri" data-c="reject">Reject non-essential</button><button type="button" data-c="manage">Manage</button></div>'+
'<div class="manage" hidden><label><input type="checkbox" disabled checked> Essential (remembers this choice)</label><label><input type="checkbox" id="ccOpt"> Optional tools (none are used on this site today)</label><div class="btns"><button type="button" class="pri" data-c="save">Save choices</button></div></div>';
var sk=document.querySelector('.skip');if(sk&&sk.nextSibling){sk.parentNode.insertBefore(box,sk.nextSibling)}else{document.body.insertBefore(box,document.body.firstChild)}
var last=null;
function open(focus){last=document.activeElement;box.hidden=false;if(focus)box.querySelector('h2').focus()}
function close(){box.hidden=true;if(last&&last.focus)last.focus()}
box.addEventListener('click',function(e){var c=e.target.getAttribute&&e.target.getAttribute('data-c');if(!c)return;
 if(c==='manage'){box.querySelector('.manage').hidden=false;document.getElementById('ccOpt').focus();return}
 save(c==='save'?(document.getElementById('ccOpt').checked?'all':'reject'):c);close()});
box.addEventListener('keydown',function(e){if(e.key==='Escape'){close()}});
document.querySelectorAll('[data-cookie-settings]').forEach(function(b){b.addEventListener('click',function(){box.querySelector('.manage').hidden=false;open(true)})});
if(!get())open(false);
})();
