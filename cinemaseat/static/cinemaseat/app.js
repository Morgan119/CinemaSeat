const search=document.querySelector('#search'), cards=[...document.querySelectorAll('.movie-card')];function filter(){let q=(search?.value||'').toLowerCase();cards.forEach(c=>c.style.display=c.dataset.title.includes(q)?'block':'none')}search?.addEventListener('input',filter);document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{document.querySelectorAll('.chip').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');let f=b.dataset.filter;cards.forEach(c=>c.style.display=(f==='all'||c.dataset.genre===f)&&c.dataset.title.includes((search?.value||'').toLowerCase())?'block':'none')});
const seats=document.querySelector('#seats');if(seats){let chosen=[];for(let r=0;r<8;r++)for(let c=1;c<=15;c++){let s=document.createElement('button');s.className='seat '+(r<1?'vip ':'')+([3,9,14].includes(c)&&r%3===0?'booked':'');s.dataset.seat=String.fromCharCode(65+r)+c;s.disabled=s.classList.contains('booked');s.onclick=()=>{s.classList.toggle('selected');chosen=s.classList.contains('selected')?[...chosen,s.dataset.seat]:chosen.filter(x=>x!==s.dataset.seat);document.querySelector('#seat-label').textContent=chosen.join(', ')||'None';document.querySelector('#total').textContent='UGX '+(chosen.length*25000).toLocaleString()};seats.appendChild(s)}}document.querySelector('#book')?.addEventListener('click',()=>document.querySelector('#seat-panel').scrollIntoView({behavior:'smooth'}));

document.querySelector('#locationBtn')?.addEventListener('click',()=>alert('Cinema location: Acacia Mall, Kampala'));document.querySelector('#notifyBtn')?.addEventListener('click',()=>alert('You have no new notifications.'));document.querySelector('#reminderBtn')?.addEventListener('click',e=>{e.currentTarget.textContent='Reminder added ✓';e.currentTarget.classList.add('primary')});document.querySelector('#continue')?.addEventListener('click',()=>{let l=document.querySelector('#seat-label');if(l&&l.textContent!=='None'){let movie=resolveMovieTitle();let time=document.querySelector('.times .chosen')?.dataset.time||'6:30 PM';window.location.href='/payment/?movie='+encodeURIComponent(movie)+'&seats='+encodeURIComponent(l.textContent.replaceAll(', ',','))+'&time='+encodeURIComponent(time);}else alert('Please select at least one seat.')});
document.querySelectorAll('.times button').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.times button').forEach(x=>x.classList.remove('chosen'));btn.classList.add('chosen');localStorage.setItem('cinemaseat_time',btn.dataset.time||btn.textContent.trim())}));
if(document.querySelector('.booking-heading')){let saved=localStorage.getItem('cinemaseat_time');let target=[...document.querySelectorAll('.times button')].find(b=>b.dataset.time===saved);if(target){document.querySelectorAll('.times button').forEach(x=>x.classList.remove('chosen'));target.classList.add('chosen')}}

document.querySelector('#printReceipt')?.addEventListener('click',()=>window.print());

const resolveMovieTitle = () => {
  const headingText = document.querySelector('.booking-heading h1')?.textContent?.trim() || '';
  if (headingText && headingText.toLowerCase() !== 'movie') return headingText;
  const pageTitle = document.title || '';
  const cleanTitle = pageTitle.replace(/^Book\s+/, '').replace(/\s+·\s+CinemaSeat$/, '').trim();
  return cleanTitle || 'Selected movie';
};

document.querySelectorAll('nav').forEach(nav => {
  const toggle = nav.querySelector('.nav-toggle');
  const links = nav.querySelector('.navlinks');
  if (!toggle || !links) return;
  toggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(isOpen));
  });
  links.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => nav.classList.remove('nav-open'));
  });
});

document.querySelectorAll('.user-menu').forEach(menu => {
  const button = menu.querySelector('.user-menu-toggle');
  if (!button) return;
  button.addEventListener('click', (event) => {
    event.stopPropagation();
    const open = menu.classList.toggle('open');
    button.setAttribute('aria-expanded', String(open));
  });
  menu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      menu.classList.remove('open');
      button.setAttribute('aria-expanded', 'false');
    });
  });
});

document.addEventListener('click', () => {
  document.querySelectorAll('.user-menu.open').forEach(menu => {
    menu.classList.remove('open');
    const button = menu.querySelector('.user-menu-toggle');
    if (button) button.setAttribute('aria-expanded', 'false');
  });
});

