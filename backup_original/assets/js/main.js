/**
 * ============================================================
 * AgIL Lab — Main JavaScript
 * Lý do: gộp logic carousel, hamburger menu, path normalization
 * Rollback: xoá file này, khôi phục script cũ trong HTML
 * ============================================================
 */

/* ===== HAMBURGER MENU ===== */
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('open');
        });

        // Đóng menu khi click link (mobile)
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks.classList.remove('open');
            });
        });
    }
});

/* ===== IMAGE CAROUSEL ===== */
class Carousel {
    /**
     * @param {string} selector — CSS selector cho container .carousel
     * @param {object} options — { autoPlay: true, interval: 4000, pauseOnHover: true }
     */
    constructor(selector, options = {}) {
        this.el = document.querySelector(selector);
        if (!this.el) return;

        this.track = this.el.querySelector('.carousel-track');
        this.slides = this.el.querySelectorAll('.carousel-slide');
        this.prevBtn = this.el.querySelector('.carousel-prev');
        this.nextBtn = this.el.querySelector('.carousel-next');
        this.dotsContainer = this.el.parentElement.querySelector('.carousel-dots');

        this.current = 0;
        this.total = this.slides.length;
        this.autoPlay = options.autoPlay !== false;
        this.interval = options.interval || 4000;
        this.pauseOnHover = options.pauseOnHover !== false;
        this.timer = null;

        if (this.total === 0) return;

        this._buildDots();
        this._bind();
        this._goTo(0);

        if (this.autoPlay) this._startAutoPlay();
    }

    _buildDots() {
        if (!this.dotsContainer) return;
        this.dotsContainer.innerHTML = '';
        for (let i = 0; i < this.total; i++) {
            const dot = document.createElement('button');
            dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
            dot.addEventListener('click', () => this._goTo(i));
            this.dotsContainer.appendChild(dot);
        }
        this.dots = this.dotsContainer.querySelectorAll('.carousel-dot');
    }

    _bind() {
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prev());
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.next());

        // Pause on hover
        if (this.pauseOnHover) {
            this.el.addEventListener('mouseenter', () => this._stopAutoPlay());
            this.el.addEventListener('mouseleave', () => {
                if (this.autoPlay) this._startAutoPlay();
            });
        }

        // Swipe support (touch)
        let startX = 0;
        this.el.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
        this.el.addEventListener('touchend', e => {
            const diff = startX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 50) {
                diff > 0 ? this.next() : this.prev();
            }
        }, { passive: true });
    }

    _goTo(index) {
        this.current = ((index % this.total) + this.total) % this.total;
        this.track.style.transform = `translateX(-${this.current * 100}%)`;
        if (this.dots) {
            this.dots.forEach((d, i) => d.classList.toggle('active', i === this.current));
        }
    }

    next() { this._goTo(this.current + 1); }
    prev() { this._goTo(this.current - 1); }

    _startAutoPlay() {
        this._stopAutoPlay();
        this.timer = setInterval(() => this.next(), this.interval);
    }

    _stopAutoPlay() {
        if (this.timer) { clearInterval(this.timer); this.timer = null; }
    }
}

/* ===== IMAGE PATH NORMALIZATION ===== */
/**
 * Normalize image path: lowercase extension, encode spaces
 * Lý do: một số member dùng .JPG/.PNG thay vì .jpg/.png
 */
function normalizeImagePath(path) {
    if (!path) return '';
    // Lowercase file extension
    const lastDot = path.lastIndexOf('.');
    if (lastDot > 0) {
        path = path.substring(0, lastDot) + path.substring(lastDot).toLowerCase();
    }
    // Encode spaces
    return path.replace(/ /g, '%20');
}
