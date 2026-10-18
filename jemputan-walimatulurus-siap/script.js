const weddingDate = new Date('2026-11-01T11:00:00+08:00').getTime();
const countdown = document.querySelector('[data-wedding-countdown]');

function updateCountdown() {
    if (!countdown) return;

    const remaining = weddingDate - Date.now();
    const values = {
        days: Math.max(0, Math.floor(remaining / 86400000)),
        hours: Math.max(0, Math.floor((remaining % 86400000) / 3600000)),
        minutes: Math.max(0, Math.floor((remaining % 3600000) / 60000)),
        seconds: Math.max(0, Math.floor((remaining % 60000) / 1000))
    };

    Object.entries(values).forEach(([unit, value]) => {
        const element = countdown.querySelector(`[data-${unit}]`);
        if (element) element.textContent = String(value).padStart(2, '0');
    });
}

updateCountdown();
if (countdown) window.setInterval(updateCountdown, 1000);

const youtubePlayer = document.querySelector('[data-youtube-player]');
if (youtubePlayer && window.location.protocol === 'file:') {
    youtubePlayer.hidden = true;
    const localPlaybackNote = document.querySelector('[data-local-youtube-note]');
    if (localPlaybackNote) localPlaybackNote.hidden = false;
} else if (youtubePlayer) {
    youtubePlayer.src = youtubePlayer.dataset.src;
}

const musicPlayButton = document.querySelector('[data-music-play]');
musicPlayButton?.addEventListener('click', () => {
    const musicFrame = document.querySelector('[data-music-frame]');
    const musicCard = document.querySelector('[data-music-card]');
    const youtubeLink = document.querySelector('[data-open-youtube]');
    if (!musicFrame || !musicCard) return;

    if (window.location.protocol === 'file:') {
        if (youtubeLink instanceof HTMLAnchorElement) {
            window.open(youtubeLink.href, '_blank', 'noopener,noreferrer');
        }
        return;
    }

    if (!musicFrame.querySelector('iframe')) {
        const player = document.createElement('iframe');
        player.className = 'music-embed';
        player.src = 'https://www.youtube-nocookie.com/embed/e6VBAC1l_MU?autoplay=1&rel=0';
        player.title = 'Lagu pilihan untuk majlis walimatulurus';
        player.allow = 'autoplay; encrypted-media; picture-in-picture';
        player.referrerPolicy = 'strict-origin-when-cross-origin';
        player.allowFullscreen = true;
        musicFrame.append(player);
    }

    musicCard.hidden = true;
    musicFrame.hidden = false;
    musicPlayButton.setAttribute('aria-label', 'Lagu sedang dimainkan');
});

const rsvpForm = document.querySelector('[data-rsvp-form]');
rsvpForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!rsvpForm.reportValidity()) return;

    const formData = new FormData(rsvpForm);
    const message = [
        'Assalamualaikum, saya ingin mengesahkan kehadiran ke majlis walimatulurus.',
        '',
        `Nama: ${formData.get('name')}`,
        `Kehadiran: ${formData.get('attendance')}`,
        `Bilangan tetamu: ${formData.get('guests')}`,
        `Ucapan & doa: ${formData.get('message') || '-'}`
    ].join('\n');

    window.location.href = `https://wa.me/60122719861?text=${encodeURIComponent(message)}`;
});
