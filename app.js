const PHONE="5518997553071";
const ATTR_KEY="bdm_attribution";
const clean=(v,l=120)=>String(v||"").slice(0,l).replace(/[<>]/g,"").trim();
function initAttribution(){
  const p=new URLSearchParams(location.search);
  const keys=["utm_source","utm_medium","utm_campaign","utm_content","utm_term","gclid","gbraid","wbraid","fbclid"];
  let stored={};try{stored=JSON.parse(sessionStorage.getItem(ATTR_KEY)||"{}")}catch{}
  const a={};for(const k of keys)a[k]=clean(p.get(k)||stored[k]||"");
  a.landing_path=clean(stored.landing_path||location.pathname,160);
  try{sessionStorage.setItem(ATTR_KEY,JSON.stringify(a))}catch{}
  document.querySelectorAll("[data-cta-id]").forEach(el=>el.addEventListener("click",()=>{window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:"bdm_partner_cta_click",cta_id:el.dataset.ctaId,...a})}));
}
function readAttribution(){try{return JSON.parse(sessionStorage.getItem(ATTR_KEY)||"{}")}catch{return{}}}
function initForm(){
  const f=document.querySelector("#partner-form"),err=document.querySelector("#form-error");if(!f||!err)return;
  f.addEventListener("submit",e=>{
    e.preventDefault();
    const fields=[...f.querySelectorAll("[required]")],bad=fields.filter(x=>!x.checkValidity());
    if(bad.length){err.textContent="Preencha os campos obrigatórios para continuar.";bad[0].focus();return}
    const d=new FormData(f),a=readAttribution();
    const lead={name:clean(d.get("name"),100),phone:clean(d.get("phone"),20),region:clean(d.get("region"),100),role:clean(d.get("automotive_role"),100),capital:clean(d.get("capital"),100)};
    window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:"generate_lead",lead_type:"authorized_representative",region:lead.region,automotive_role:lead.role,capital_status:lead.capital,...a});
    const origin=[a.utm_source,a.utm_medium,a.utm_campaign].filter(Boolean).join(" / ");
    const msg=["Olá, BDM. Quero saber mais sobre ser um autorizado.","","Nome: "+lead.name,"WhatsApp: "+lead.phone,"Cidade/região: "+lead.region,"Atuação: "+lead.role,"Capital: "+lead.capital,origin?"Origem: "+origin:""].filter(Boolean).join("\n");
    location.assign("https://wa.me/"+PHONE+"?text="+encodeURIComponent(msg));
  });
}
initAttribution();initForm();const y=document.querySelector("#year");if(y)y.textContent=new Date().getFullYear();