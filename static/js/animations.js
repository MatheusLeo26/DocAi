/**
 * animations.js - Premium animations using GSAP and ScrollTrigger
 * All animations use fromTo with explicit start/end states to prevent
 * race conditions with CSS animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof gsap === 'undefined') return;

    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }

    // Initialize Lenis for Smooth Scrolling
    let lenis;
    if (typeof Lenis !== 'undefined') {
        lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            direction: 'vertical',
            gestureDirection: 'vertical',
            smooth: true,
        });

        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);

        if (typeof ScrollTrigger !== 'undefined') {
            lenis.on('scroll', ScrollTrigger.update);
            gsap.ticker.add((time)=>{
              lenis.raf(time * 1000);
            });
            gsap.ticker.lagSmoothing(0);
        }
    }

    // Kill any conflicting CSS animations on GSAP-managed elements
    document.querySelectorAll('.glass-panel, .feature-card').forEach(el => {
        el.style.animation = 'none';
    });

    initGlobalAnimations();

    // Detect current page and init specific animations
    const isLandingPage = document.querySelector('.hero') !== null;
    if (isLandingPage) {
        initLandingPageAnimations();
    }

    const isAuthPage = document.querySelector('.auth-container') !== null;
    if (isAuthPage) {
        initAuthPageAnimations();
    }

    const isDashboard = document.querySelector('.dashboard-container') !== null || document.querySelector('.create-container') !== null;
    if (isDashboard) {
        initDashboardAnimations();
    }
});

/**
 * Global animations like floating background blobs and magnetic buttons
 */
function initGlobalAnimations() {
    // Smooth floating background blobs (Inspira UI style)
    const blobs = document.querySelectorAll('.blob');
    blobs.forEach((blob, index) => {
        gsap.to(blob, {
            x: () => gsap.utils.random(-80, 80),
            y: () => gsap.utils.random(-80, 80),
            scale: () => gsap.utils.random(0.9, 1.25),
            duration: gsap.utils.random(15, 25),
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut",
            delay: index * 2
        });
    });

    // Magnetic buttons effect (hover pull)
    const primaryButtons = document.querySelectorAll('.btn-primary, .generate-btn');
    primaryButtons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            gsap.to(btn, {
                x: x * 0.25,
                y: y * 0.25,
                duration: 0.3,
                ease: "power2.out"
            });
        });

        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, {
                x: 0,
                y: 0,
                duration: 0.5,
                ease: "elastic.out(1, 0.3)"
            });
        });
    });
}

/**
 * Premium landing page animations using a timeline for sequencing
 */
function initLandingPageAnimations() {
    // Main hero timeline — fromTo everywhere for predictable results
    const tl = gsap.timeline({ defaults: { ease: "power4.out", overwrite: true } });

    tl.fromTo('.glass-panel',
        { opacity: 0, y: 50, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 1.2 }
    )
    .fromTo('.hero h1',
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 1 },
        "-=0.9"
    )
    .fromTo('.hero p',
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, duration: 0.8 },
        "-=0.7"
    )
    .fromTo('.hero-actions button',
        { opacity: 0, y: 20, scale: 0.9 },
        { opacity: 1, y: 0, scale: 1, stagger: 0.15, duration: 0.8, ease: "back.out(1.7)" },
        "-=0.5"
    );

    // Reveal feature cards on scroll
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.set('.feature-card', { opacity: 0, y: 40 });

        ScrollTrigger.batch('.feature-card', {
            onEnter: batch => gsap.to(batch, {
                opacity: 1,
                y: 0,
                stagger: 0.15,
                duration: 0.8,
                ease: "power3.out",
                overwrite: true
            }),
            once: true,
            start: "top 85%"
        });

        // Steps reveal
        gsap.set('.step', { opacity: 0, x: -30 });

        ScrollTrigger.batch('.step', {
            onEnter: batch => gsap.to(batch, {
                opacity: 1,
                x: 0,
                stagger: 0.2,
                duration: 0.8,
                ease: "power2.out",
                overwrite: true
            }),
            once: true,
            start: "top 80%"
        });
    } else {
        // Fallback: just show everything if ScrollTrigger not loaded
        gsap.set('.feature-card, .step', { opacity: 1, y: 0, x: 0 });
    }
}

/**
 * Authentication pages entry animations with explicit fromTo
 */
function initAuthPageAnimations() {
    const tl = gsap.timeline({ defaults: { ease: "power4.out", overwrite: true } });

    tl.fromTo('.auth-box',
        { opacity: 0, scale: 0.9, y: 30 },
        { opacity: 1, scale: 1, y: 0, duration: 1 }
    )
    .fromTo('.auth-box .form-group',
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, stagger: 0.1, duration: 0.6 },
        "-=0.5"
    )
    .fromTo('.auth-box button',
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.6 },
        "-=0.3"
    )
    .fromTo('.auth-links',
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.6 },
        "-=0.4"
    );
}

/**
 * App panel (Dashboard / Create) entrance animations
 */
function initDashboardAnimations() {
    // Sidebar items cascade
    gsap.fromTo('.sidebar .nav-item',
        { opacity: 0, x: -20 },
        { opacity: 1, x: 0, stagger: 0.08, duration: 0.6, ease: "power2.out", delay: 0.2 }
    );

    // Bento cards layout fade-in
    gsap.fromTo('.bento-card',
        { opacity: 0, y: 30, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, stagger: 0.1, duration: 0.8, ease: "back.out(1.5)", delay: 0.3 }
    );

    // Document lists reveal on scroll
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.set('.doc-item', { opacity: 0, y: 20 });
        
        ScrollTrigger.batch('.doc-item', {
            onEnter: batch => gsap.to(batch, {
                opacity: 1,
                y: 0,
                stagger: 0.05,
                duration: 0.6,
                ease: "power2.out",
                overwrite: true
            }),
            once: true,
            start: "top 90%"
        });
    }

    // Document creation form fields reveal
    gsap.fromTo('.form-section h3, .form-section .form-group',
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, stagger: 0.05, duration: 0.6, ease: "power2.out", delay: 0.3 }
    );
}
