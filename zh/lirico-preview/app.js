const splash=document.getElementById('splash'), app=document.getElementById('app');
setTimeout(()=>{splash.classList.add('hidden');app.classList.remove('hidden')},4000);

const pages=[...document.querySelectorAll('.page')];
const nav=[...document.querySelectorAll('.nav')];
function go(id){pages.forEach(p=>p.classList.toggle('active-page',p.id===id));nav.forEach(b=>b.classList.toggle('active',b.dataset.page===id));window.scrollTo({top:0,behavior:'smooth'})}
nav.forEach(b=>b.addEventListener('click',()=>go(b.dataset.page)));
document.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.go)));

const toast=document.getElementById('toast');
function showToast(msg){toast.textContent=msg;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),1800)}
document.getElementById('selectDemo').onclick=()=>{document.getElementById('homeFileName').textContent='Anafilaxia 1.m4a';showToast('Arquivo selecionado para demonstração')};
document.getElementById('recordDemo').onclick=()=>showToast('Gravação ao vivo simulada nesta prévia');

document.getElementById('txSelect').onclick=()=>{document.getElementById('txTitle').textContent='Anafilaxia 1.m4a';document.getElementById('txSub').textContent='Arquivo selecionado · 4,8 MB';document.getElementById('txStart').classList.remove('hidden')};
document.getElementById('txStart').onclick=()=>{const wrap=document.getElementById('txProgressWrap'),bar=document.getElementById('txProgress'),status=document.getElementById('txStatus');wrap.classList.remove('hidden');status.textContent='Transcrevendo...';let n=0;const t=setInterval(()=>{n+=5;bar.style.width=n+'%';if(n>=100){clearInterval(t);status.textContent='Concluído';status.style.color='#16a34a';showToast('Transcrição concluída') }},90)};

const search=document.getElementById('search'), model=document.getElementById('modelFilter'), filters=[...document.querySelectorAll('.filter')];
let statusFilter='todos';
function filterRows(){const q=search.value.toLowerCase(),m=model.value;document.querySelectorAll('#historyRows tr').forEach(r=>{const okQ=r.dataset.file.toLowerCase().includes(q);const okS=statusFilter==='todos'||r.dataset.status===statusFilter;const okM=m==='Todos os modelos'||r.dataset.model===m;r.style.display=okQ&&okS&&okM?'':'none'})}
search.oninput=filterRows;model.onchange=filterRows;filters.forEach(f=>f.onclick=()=>{filters.forEach(x=>x.classList.remove('active'));f.classList.add('active');statusFilter=f.dataset.filter;filterRows()});
document.querySelectorAll('.open-detail').forEach(b=>b.onclick=e=>{document.getElementById('detailTitle').textContent=e.target.closest('tr').dataset.file;go('detalhe')});
document.querySelectorAll('.link:not(.open-detail)').forEach(b=>b.onclick=()=>showToast(b.textContent+' — ação simulada'));

document.querySelectorAll('.model button').forEach(btn=>btn.onclick=()=>{document.querySelectorAll('.model').forEach(m=>{m.classList.remove('selected');m.querySelector('button').textContent='Selecionar';m.querySelector('button').classList.remove('primary')});const card=btn.closest('.model');card.classList.add('selected');btn.textContent='Selecionado';btn.classList.add('primary');showToast(card.querySelector('h3').textContent+' selecionado')});
document.getElementById('themeSelect').onchange=e=>document.body.classList.toggle('dark',e.target.value==='dark');
document.querySelector('.settings-card>.primary').onclick=()=>showToast('Configurações salvas na prévia');