// ==========================================
// F1 2026 PREDICTIONS — Interactive Script
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initParticles();
    initRaceCalendar();
    initScrollAnimations();
    initCounterAnimations();
    initActiveNavHighlight();
});

// ==========================================
// Navigation
// ==========================================
function initNavigation() {
    const nav = document.getElementById('main-nav');
    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('nav-links');

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // Mobile toggle
    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
        toggle.classList.toggle('active');
    });

    // Close mobile menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            links.classList.remove('open');
            toggle.classList.remove('active');
        });
    });
}

// ==========================================
// Active Nav Highlight on Scroll
// ==========================================
function initActiveNavHighlight() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, { 
        rootMargin: '-30% 0px -70% 0px' 
    });

    sections.forEach(section => observer.observe(section));
}

// ==========================================
// Floating Particles
// ==========================================
function initParticles() {
    const container = document.getElementById('hero-particles');
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'hero-particle';
        
        const x = Math.random() * 100;
        const duration = 8 + Math.random() * 12;
        const delay = Math.random() * duration;
        const size = 1 + Math.random() * 3;
        const opacity = 0.2 + Math.random() * 0.5;

        particle.style.cssText = `
            left: ${x}%;
            width: ${size}px;
            height: ${size}px;
            animation-duration: ${duration}s;
            animation-delay: -${delay}s;
            opacity: ${opacity};
            background: ${Math.random() > 0.5 ? 'rgba(232, 0, 45, 0.6)' : 'rgba(255, 107, 53, 0.4)'};
        `;

        container.appendChild(particle);
    }
}

// ==========================================
// Race Calendar Data & Rendering
// ==========================================
function initRaceCalendar() {
    const races = [
        { round: 1, flag: '🇦🇺', name: 'Australian Grand Prix', circuit: 'Albert Park, Melbourne', date: 'Mar 14-16', prediction: '🏆 Hamilton wins on Ferrari debut' },
        { round: 2, flag: '🇨🇳', name: 'Chinese Grand Prix', circuit: 'Shanghai International', date: 'Mar 28-30', prediction: '🏆 Norris dominates from pole' },
        { round: 3, flag: '🇯🇵', name: 'Japanese Grand Prix', circuit: 'Suzuka', date: 'Apr 4-6', prediction: '🏆 Verstappen shows Aston\'s pace' },
        { round: 4, flag: '🇧🇭', name: 'Bahrain Grand Prix', circuit: 'Sakhir', date: 'Apr 11-13', prediction: '🏆 Leclerc Ferrari 1-2' },
        { round: 5, flag: '🇸🇦', name: 'Saudi Arabian Grand Prix', circuit: 'Jeddah Corniche', date: 'Apr 18-20', prediction: '🏆 Hamilton under the lights' },
        { round: 6, flag: '🇺🇸', name: 'Miami Grand Prix', circuit: 'Miami International', date: 'May 2-4', prediction: '🏆 Norris takes the fight to Ferrari' },
        { round: 7, flag: '🇪🇸', name: 'Spanish Grand Prix', circuit: 'Barcelona-Catalunya', date: 'May 16-18', prediction: '🏆 Russell\'s Mercedes breakthrough' },
        { round: 8, flag: '🇲🇨', name: 'Monaco Grand Prix', circuit: 'Circuit de Monaco', date: 'May 23-25', prediction: '🏆 Leclerc wins at home again' },
        { round: 9, flag: '🇨🇦', name: 'Canadian Grand Prix', circuit: 'Circuit Gilles-Villeneuve', date: 'Jun 13-15', prediction: '🏆 Verstappen masters the rain' },
        { round: 10, flag: '🇦🇹', name: 'Austrian Grand Prix', circuit: 'Red Bull Ring', date: 'Jun 27-29', prediction: '🏆 Emotional RB return for Max' },
        { round: 11, flag: '🇬🇧', name: 'British Grand Prix', circuit: 'Silverstone', date: 'Jul 4-6', prediction: '🏆 Hamilton wins for the crowds' },
        { round: 12, flag: '🇧🇪', name: 'Belgian Grand Prix', circuit: 'Spa-Francorchamps', date: 'Jul 25-27', prediction: '🏆 Piastri\'s breakout drive' },
        { round: 13, flag: '🇭🇺', name: 'Hungarian Grand Prix', circuit: 'Hungaroring', date: 'Aug 1-3', prediction: '🏆 Norris dominates tight track' },
        { round: 14, flag: '🇳🇱', name: 'Dutch Grand Prix', circuit: 'Zandvoort', date: 'Aug 29-31', prediction: '🏆 Verstappen delights home fans' },
        { round: 15, flag: '🇮🇹', name: 'Italian Grand Prix', circuit: 'Monza', date: 'Sep 5-7', prediction: '🏆 Ferrari Tifosi dream — Hamilton wins' },
        { round: 16, flag: '🇦🇿', name: 'Azerbaijan Grand Prix', circuit: 'Baku City Circuit', date: 'Sep 19-21', prediction: '🏆 Chaos race — Antonelli podium!' },
        { round: 17, flag: '🇸🇬', name: 'Singapore Grand Prix', circuit: 'Marina Bay', date: 'Oct 3-5', prediction: '🏆 Leclerc under the lights' },
        { round: 18, flag: '🇺🇸', name: 'United States Grand Prix', circuit: 'COTA, Austin', date: 'Oct 17-19', prediction: '🏆 Hamilton seals the title deal' },
        { round: 19, flag: '🇲🇽', name: 'Mexican Grand Prix', circuit: 'Autodromo Hermanos Rodriguez', date: 'Oct 24-26', prediction: '🏆 Verstappen altitude advantage' },
        { round: 20, flag: '🇧🇷', name: 'Brazilian Grand Prix', circuit: 'Interlagos, São Paulo', date: 'Nov 7-9', prediction: '🏆 Classic Interlagos rain drama' },
        { round: 21, flag: '🇺🇸', name: 'Las Vegas Grand Prix', circuit: 'Las Vegas Strip', date: 'Nov 20-22', prediction: '🏆 Norris shines under neon' },
        { round: 22, flag: '🇶🇦', name: 'Qatar Grand Prix', circuit: 'Lusail International', date: 'Nov 28-30', prediction: '🏆 Hamilton extends the lead' },
        { round: 23, flag: '🇸🇦', name: 'Saudi Arabian Grand Prix', circuit: 'Jeddah (if double-header)', date: 'TBD', prediction: '🏆 Leclerc keeping it close' },
        { round: 24, flag: '🇦🇪', name: 'Abu Dhabi Grand Prix', circuit: 'Yas Marina', date: 'Dec 5-7', prediction: '🏆 CHAMPION CROWNED — Hamilton 8x WDC' },
    ];

    const grid = document.getElementById('calendar-grid');
    const today = new Date(2026, 2, 13); // March 13, 2026

    races.forEach((race, index) => {
        const card = document.createElement('div');
        card.className = 'race-card fade-in';

        // Determine if first race is "next race" since season hasn't started
        const isNextRace = index === 0; // Australian GP is next
        if (isNextRace) card.classList.add('next-race');

        card.style.transitionDelay = `${index * 50}ms`;

        card.innerHTML = `
            <div class="race-round">ROUND ${String(race.round).padStart(2, '0')}</div>
            <span class="race-flag">${race.flag}</span>
            <h3 class="race-name">${race.name}</h3>
            <p class="race-circuit">${race.circuit}</p>
            <p class="race-date">📅 ${race.date}</p>
            <div class="race-prediction">${race.prediction}</div>
        `;

        grid.appendChild(card);
    });
}

// ==========================================
// Scroll Animations (Intersection Observer)
// ==========================================
function initScrollAnimations() {
    // Add fade-in class to animatable elements
    const animatableSelectors = [
        '.podium-card',
        '.standings-row',
        '.constructor-card',
        '.reg-card',
        '.take-card',
        '.section-header'
    ];

    animatableSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach((el, index) => {
            el.classList.add('fade-in');
            el.style.transitionDelay = `${index * 80}ms`;
        });
    });

    // Observe all fade-in elements
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { 
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}

// ==========================================
// Counter Animations for Hero Stats
// ==========================================
function initCounterAnimations() {
    const statValues = document.querySelectorAll('.hero-stat-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalValue = parseInt(target.textContent);
                animateCounter(target, 0, finalValue, 1500);
                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(stat => observer.observe(stat));
}

function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (end - start) * eased);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ==========================================
// Smooth Scroll for Anchor Links
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navHeight = document.getElementById('main-nav').offsetHeight;
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});
