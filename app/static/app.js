const $ = id => document.getElementById(id);
const fmt = value => new Intl.NumberFormat('es-CO', {maximumFractionDigits: 2}).format(value);
let info;
let accessKey = '';
async function api(path, method = 'GET', body) {
  if (!accessKey) throw new Error('Ingresa tu clave de acceso para conectar.');
  const headers = {'X-API-Key': accessKey};
  if (body) headers['Content-Type'] = 'application/json';
  const r = await fetch(path, {method, headers, body: body ? JSON.stringify(body) : undefined});
  const data = await r.json();
  if (r.status === 401) {$('status').textContent='Acceso no autorizado';}
  if (!r.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Revisa los datos ingresados.');
  return data;
}
function message(text, error = false) {$('message').textContent = text; $('message').className = error ? 'error' : '';}
function chart(rows) {
  const w=640,h=245,left=42,right=16,top=16,bottom=28;
  const max=Math.ceil(Math.max(...rows.map(r=>r.ventas))/100)*100;
  const x=i=>left+i*(w-left-right)/(rows.length-1), y=v=>h-bottom-v*(h-top-bottom)/max;
  const points=rows.map((r,i)=>`${x(i)},${y(r.ventas)}`).join(' ');
  const lines=Array.from({length:5},(_,i)=>{const v=max*i/4;return `<line x1="${left}" y1="${y(v)}" x2="${w-right}" y2="${y(v)}" stroke="#e8ede7" stroke-dasharray="3 4"/><text x="${left-10}" y="${y(v)+4}" text-anchor="end" font-size="10" fill="#8a978e">${fmt(v)}</text>`}).join('');
  const labels=rows.map((r,i)=>i===0||i===rows.length-1||i%5===4?`<text x="${x(i)}" y="${h-5}" text-anchor="middle" font-size="10" fill="#8a978e">Día ${r.dia}</text>`:'').join('');
  $('chart').innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Gráfico de ventas históricas por día"><defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#80b796" stop-opacity=".3"/><stop offset="1" stop-color="#80b796" stop-opacity="0"/></linearGradient></defs>${lines}<polygon points="${left},${h-bottom} ${points} ${w-right},${h-bottom}" fill="url(#fill)"/><polyline points="${points}" fill="none" stroke="#297657" stroke-width="2.5" stroke-linejoin="round"/>${rows.map((r,i)=>`<circle cx="${x(i)}" cy="${y(r.ventas)}" r="3" fill="white" stroke="#297657" stroke-width="1.5"><title>Día ${r.dia}: ${r.ventas} unidades</title></circle>`).join('')}${labels}</svg>`;
}
function renderModels() {
  document.querySelectorAll('.model').forEach(b=>b.classList.toggle('selected',b.dataset.color===info.modelo_activo));
  $('active-model').textContent=`${info.modelo_activo} ACTIVO`;
  const m=info.modelos[info.modelo_activo];
  $('model-metrics').textContent=`Evaluación temporal · MAE: ${fmt(m.mae)} unidades · RMSE: ${fmt(m.rmse)} unidades. Días de prueba: ${info.dias_evaluacion.join(', ')}. Modelo final ajustado con ${info.registros} registros.`;
}
async function audit() {
  const data=await api('/audit');
  $('audit-body').replaceChildren();
  for(const e of data.eventos){
    const tr=document.createElement('tr');
    const date=document.createElement('td');date.textContent=new Date(e.fecha).toLocaleString('es-CO');
    const action=document.createElement('td'), badge=document.createElement('span');badge.className='event-tag';badge.textContent=e.accion;action.append(badge);
    const detail=document.createElement('td');detail.textContent=typeof e.detalle==='string'?e.detalle:JSON.stringify(e.detalle);
    tr.append(date,action,detail);$('audit-body').append(tr);
  }
}
async function refresh() {
  const [data,avg,max,metrics,model] = await Promise.all([api('/datos'),api('/promedio-ventas'),api('/max-ventas'),api('/metrics'),api('/modelo-info')]);
  info=model;renderModels();chart(data.registros);
  $('total').textContent=fmt(data.registros.reduce((s,r)=>s+r.ventas,0));$('average').textContent=fmt(avg.promedio);$('maximum').textContent=fmt(max.ventas);$('maxday').textContent=`Día ${max.dia} · unidades registradas`;
  $('requests').textContent=metrics.total_predicciones;$('latency').textContent=`Latencia media: ${fmt(metrics.latencia_promedio_ms)} ms`;
  $('range').textContent=`${data.registros.length} días registrados`;$('status').textContent='● Servicio activo';await audit();
}
async function perform(button, fn) {
  button.disabled=true;
  try{message('');await fn();}catch(e){message(e.message,true);}finally{button.disabled=false;}
}
$('predict-form').addEventListener('submit',e=>{e.preventDefault();perform(e.submitter,async()=>{
  const r=await api('/predict','POST',{dia:Number($('prediction-day').value)});
  const strong=$('prediction-result').querySelector('strong');strong.replaceChildren(document.createTextNode(fmt(r.prediccion)+' '));const units=document.createElement('small');units.textContent='unidades';strong.append(units);
  $('prediction-result').querySelector('p').textContent=`Día ${r.dia} · Modelo ${r.modelo} · ${fmt(r.latencia*1000)} ms`;
  await refresh();message('Predicción generada y registrada en auditoría.');
});});
$('query-form').addEventListener('submit',e=>{e.preventDefault();perform(e.submitter,async()=>{$('query-result').textContent=(await api('/consulta/'+Number($('query-day').value))).respuesta;await audit();});});
document.querySelectorAll('.model').forEach(b=>b.addEventListener('click',()=>perform(b,async()=>{const r=await api('/switch/'+b.dataset.color,'PUT');await refresh();message(r.mensaje);} )));
$('refresh').addEventListener('click',()=>perform($('refresh'),refresh));
$('reload').addEventListener('click',()=>perform($('reload'),async()=>{const r=await api('/reload-model','PUT');await refresh();message(r.mensaje);}));
$('reset').addEventListener('click',()=>perform($('reset'),async()=>{const r=await api('/reset','DELETE');await refresh();message(r.mensaje);}));
$('access-form').addEventListener('submit',e=>{e.preventDefault();perform(e.submitter,async()=>{
  accessKey=$('access-key').value.trim();
  try {await refresh();$('access-key').value='';message('Acceso autorizado. La clave se conserva sólo en memoria durante esta página.');}
  catch(err) {accessKey='';throw err;}
});});
$('disconnect').addEventListener('click',()=>{accessKey='';location.reload();});
$('governance').addEventListener('click',()=>perform($('governance'),async()=>{
  const controls=await api('/governance');$('controls-content').textContent=JSON.stringify(controls,null,2);$('controls-dialog').showModal();
}));
$('status').textContent='Acceso protegido';
message('Ingresa tu clave de acceso para cargar los datos. Puedes consultarla con ver_clave.bat.');
