document.querySelector('#print-book').addEventListener('click',()=>window.print());
const toc=document.querySelector('#toc');if(window.innerWidth<=700)toc.open=false;
const chapters=[...document.querySelectorAll('.chapter')];
document.querySelector('#search').addEventListener('input',e=>{
 const q=e.target.value.trim().toLocaleLowerCase('ru');let count=0;
 for(const section of chapters){const match=!q||section.textContent.toLocaleLowerCase('ru').includes(q);section.hidden=!match;if(match)count++;}
 document.querySelector('#search-status').textContent=q?'Найдено разделов: '+count:'';
});
document.querySelectorAll('nav a').forEach(a=>a.addEventListener('click',()=>{
 document.querySelector('#search').value='';chapters.forEach(c=>c.hidden=false);document.querySelector('#search-status').textContent='';
 if(window.innerWidth<=700)toc.open=false;
}));
if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('current',a.hash==='#'+e.target.id));}}, {rootMargin:'-10% 0px -70% 0px'});chapters.forEach(c=>observer.observe(c));}
