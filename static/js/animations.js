/**
 * animations.js - Premium animations using GSAP and ScrollTrigger
 * Mimicking Aceternity UI / Inspira UI glowing, floating, and revealing effects.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Register ScrollTrigger if available
    if (typeof gsap !== 'undefined') {
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
        }
        
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
    }
});

/**
 * Global animations like floating background blobs and magnetic buttons
 */
function initGlobalAnimations() {
    // Smooth floating background blobs (Inspira UI style)
    const blobs = document.querySelectorAll('.blob');
    blobs.forEach((blob, index) => {
        const randomX = () => gsap.utils.random(-80, 80);
        const randomY = () => gsap.utils.random(-80, 80);
        const randomDuration = () => gsap.utils.random(15, 25);
        const randomScale = () => gsap.utils.random(0.9, 1.25);

        // Infinite drifting animation
        gsap.to(blob, {
            x: randomX,
            y: randomY,
            scale: randomScale,
            duration: randomDuration(),
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
 * Premium landing page animations (staggers, ScrollTrigger, text reveals)
 */
function initLandingPageAnimations() {
    // Reveal hero panel
    gsap.fromTo('.glass-panel', 
        { opacity: 0, y: 50, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 1.2, ease: "power4.out" }
    );

    // Hero title text reveal (Split-like animation)
    gsap.from('.hero h1', {
        opacity: 0,
        y: 20,
        duration: 1,
        delay: 0.2,
        ease: "power3.out"
    });

    gsap.from('.hero p', {
        opacity: 0,
        y: 15,
        duration: 1,
        delay: 0.4,
        ease: "power3.out"
    });

    gsap.from('.hero-actions button', {
        opacity: 0,
        y: 20,
        stagger: 0.15,
        duration: 0.8,
        delay: 0.6,
        ease: "back.out(1.7)"
    });

    // Reveal feature cards on scroll
    if (typeof ScrollTrigger !== 'undefined') {
        // Initial setup for cards to prevent flash
        gsap.set('.feature-card', { opacity: 0, y: 40, rotationX: -10 });
        
        ScrollTrigger.batch('.feature-card', {
            onEnter: batch => gsap.to(batch, {
                opacity: 1,
                y: 0,
                rotationX: 0,
                stagger: 0.15,
                duration: 0.8,
                ease: "power3.out",
                overwrite: "auto"
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
                overwrite: "auto"
            }),
            once: true,
            start: "top 80%"
        });
    }
}

/**
 * Authentication pages entry staggers
 */
function initAuthPageAnimations() {
    gsap.fromTo('.auth-box',
        { opacity: 0, scale: 0.9, y: 30 },
        { opacity: 1, scale: 1, y: 0, duration: 1, ease: "power4.out" }
    );

    gsap.from('.auth-box .form-group', {
        opacity: 0,
        y: 15,
        stagger: 0.1,
        duration: 0.6,
        delay: 0.3,
        ease: "power2.out"
    });

    gsap.from('.auth-box button, .auth-links', {
        opacity: 0,
        y: 10,
        stagger: 0.1,
        duration: 0.6,
        delay: 0.6,
        ease: "power2.out"
    });
}

/**
 * App panel (Dashboard / Create) entrance animations
 */
function initDashboardAnimations() {
    // Sidebar items cascade
    gsap.from('.sidebar .nav-item', {
        opacity: 0,
        x: -20,
        stagger: 0.08,
        duration: 0.6,
        ease: "power2.out"
    });

    // Content cards layout fade-in
    gsap.from('.dashboard-container .action-card, .dashboard-container .doc-item', {
        opacity: 0,
        y: 20,
        stagger: 0.08,
        duration: 0.8,
        ease: "power3.out"
    });

    // Document creation form fields reveal
    gsap.from('.form-section h3, .form-section .form-group', {
        opacity: 0,
        y: 15,
        stagger: 0.05,
        duration: 0.6,
        ease: "power2.out"
    });
}
