(function () {
  'use strict';

  /* -----------------------------------------------------------------------
     Internationalization (EN / ID)
     ----------------------------------------------------------------------- */
  const I18N = {
    en: {
      tagline: "local media utility",
      navApp: "App",
      navAbout: "About",
      promiseHeadline: "Paste a link. Get the file.",
      promiseSubtext: "Download videos from YouTube, TikTok, Instagram, Twitter/X, and Facebook — quickly and locally.",
      fieldLabelUrl: "Video URL",
      urlPlaceholder: "Paste a YouTube, TikTok, Instagram, Twitter/X, or Facebook link",
      btnInspect: "Inspect link",
      btnInspecting: "Inspecting…",
      labelQuality: "Quality",
      optBestQuality: "Best available",
      labelOutput: "Output",
      optOriginal: "Original",
      optWhatsApp: "WhatsApp Status",
      optMp3: "MP3 Audio",
      btnAdvanced: "Advanced",
      drawerDurationTitle: "Duration (WhatsApp Status)",
      dur15: "15 sec",
      dur30: "30 sec",
      dur60: "60 sec",
      btnDownload: "Download video",
      btnPreparingDownload: "Preparing download…",
      btnDownloading: "Downloading…",
      successTitle: "Downloaded successfully",
      btnDownloadAnother: "Download another",
      statusFfmpegReady: "Ready · ffmpeg available",
      statusFfmpegLimited: "Limited · ffmpeg not installed",
      statusStandalone: "Ready · standalone utility",
      footerPlatforms: "Supports YouTube, TikTok, Instagram, Twitter/X, Facebook",
      errEmptyUrl: "Paste a YouTube, TikTok, Instagram, Twitter/X, or Facebook link to inspect.",
      errUnsupportedUrl: "That link is not supported yet. Try YouTube, TikTok, Instagram, Twitter/X, or Facebook.",
      errTiktokRetry: "TikTok is taking a moment. Retrying the link… Check URL and try again.",
      errInspectFailed: "We couldn't read this link. Check the URL and try again.",
      errFfmpegMissing: "This format needs ffmpeg. Install it, then check again.",
      errDownloadFailed: "Download failed. Try again or choose Original output.",
      aboutTitle: "About SnatchVid",
      aboutLead: "SnatchVid is a high-speed, local-first media utility engineered by <strong>Rafly (<a href=\"https://github.com/Apewww\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"credit-link\">Stellochron / Apewww</a>)</strong> to inspect, extract, and convert online media from YouTube, TikTok, Instagram, Twitter/X, and Facebook cleanly and locally without third-party advertisements, tracking, or cloud lock-in.",
      aboutPortfolioType: "Personal Portfolio",
      aboutGithubType: "Open Source GitHub",
      aboutWhyTitle: "Why Use SnatchVid?",
      pillar1Title: "100% Free Forever",
      pillar1Desc: "Enjoy unlimited video downloads without subscriptions, token fees, or hidden paywalls.",
      pillar2Title: "Local & Fast Processing",
      pillar2Desc: "Powered by yt-dlp & ffmpeg. Media files are merged and converted directly on your machine without third-party proxies.",
      pillar3Title: "No Account or Sign-Up",
      pillar3Desc: "No logins, cookies, or email registration required. Simply paste the link and download directly.",
      pillar4Title: "Flexible Formats",
      pillar4Desc: "Get original source quality (up to 1080p DASH), extracted MP3 audio, or 9:16 portrait video ready for WhatsApp Status.",
      pillar5Title: "Multi-Platform Engine",
      pillar5Desc: "Seamlessly inspect and download content from YouTube, TikTok, Instagram Reels, Twitter/X, and Facebook.",
      pillar6Title: "Ad-Free & Safe",
      pillar6Desc: "Zero intrusive pop-unders, telemetry trackers, or deceptive buttons. Purely fast and transparent.",
      aboutHowTitle: "How to Download Videos",
      step1Title: "Copy Video URL",
      step1Desc: "Browse to YouTube, TikTok, Instagram, Twitter/X, or Facebook and copy the video URL from your browser address bar or share sheet.",
      step2Title: "Paste & Inspect",
      step2Desc: "Paste the link into the SnatchVid input bar and click \"Inspect link\" to retrieve verified video metadata.",
      step3Title: "Select Quality & Save",
      step3Desc: "Choose your desired resolution or output format (Original, WhatsApp Status, or MP3) and click \"Download video\".",
      metricsTriggerSuffix: "downloads",
      metricsModalTitle: "Usage Metrics",
      metricsModalSubtitle: "Real-time local processing & download statistics",
      metricTotalDownloads: "Total Downloads",
      metricSuccessRate: "Success Rate",
      metricTotalDuration: "Total Duration",
      metricMediaProcessed: "Media processed",
      metricsPlatformBreakdown: "Platform Breakdown",
      metricsFormatBreakdown: "Formats Distributed",
      btnRefresh: "Refresh",
      inspectedLabel: "inspected",
      failedLabel: "failed",
      updatedJustNow: "Updated: just now"
    },
    id: {
      tagline: "utilitas media lokal",
      navApp: "Aplikasi",
      navAbout: "Tentang",
      promiseHeadline: "Tempel link. Dapatkan file.",
      promiseSubtext: "Download video dari YouTube, TikTok, Instagram, Twitter/X, dan Facebook — cepat dan lokal.",
      fieldLabelUrl: "URL Video",
      urlPlaceholder: "Tempel link YouTube, TikTok, Instagram, Twitter/X, atau Facebook",
      btnInspect: "Periksa link",
      btnInspecting: "Memeriksa…",
      labelQuality: "Kualitas",
      optBestQuality: "Terbaik tersedia",
      labelOutput: "Format output",
      optOriginal: "Original",
      optWhatsApp: "Status WhatsApp",
      optMp3: "Audio MP3",
      btnAdvanced: "Lanjutan",
      drawerDurationTitle: "Durasi (Status WhatsApp)",
      dur15: "15 dtk",
      dur30: "30 dtk",
      dur60: "60 dtk",
      btnDownload: "Download video",
      btnPreparingDownload: "Menyiapkan download…",
      btnDownloading: "Mengunduh…",
      successTitle: "Berhasil diunduh",
      btnDownloadAnother: "Download link lain",
      statusFfmpegReady: "Siap · ffmpeg tersedia",
      statusFfmpegLimited: "Terbatas · ffmpeg belum terpasang",
      statusStandalone: "Siap · utilitas lokal",
      footerPlatforms: "Mendukung YouTube, TikTok, Instagram, Twitter/X, Facebook",
      errEmptyUrl: "Tempel link YouTube, TikTok, Instagram, Twitter/X, atau Facebook untuk diperiksa.",
      errUnsupportedUrl: "Link tersebut belum didukung. Coba link YouTube, TikTok, Instagram, Twitter/X, atau Facebook.",
      errTiktokRetry: "TikTok sedang memproses lambat. Mencoba kembali… Periksa URL dan coba lagi.",
      errInspectFailed: "Gagal membaca link ini. Periksa kembali URL dan coba lagi.",
      errFfmpegMissing: "Format ini memerlukan ffmpeg. Pasang ffmpeg terlebih dahulu, lalu coba lagi.",
      errDownloadFailed: "Download gagal. Coba lagi atau pilih output Original.",
      aboutTitle: "Tentang SnatchVid",
      aboutLead: "SnatchVid adalah utilitas media lokal berkecepatan tinggi yang dirancang oleh <strong>Rafly (<a href=\"https://github.com/Apewww\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"credit-link\">Stellochron / Apewww</a>)</strong> untuk memeriksa, mengekstrak, dan mengonversi media dari YouTube, TikTok, Instagram, Twitter/X, dan Facebook secara bersih dan lokal tanpa iklan, pelacakan data, atau server pihak ketiga.",
      aboutPortfolioType: "Portofolio Pribadi",
      aboutGithubType: "GitHub Open Source",
      aboutWhyTitle: "Mengapa Menggunakan SnatchVid?",
      pillar1Title: "100% Gratis Selamanya",
      pillar1Desc: "Nikmati unduhan video tanpa batas tanpa langganan, biaya token, atau batasan tersembunyi.",
      pillar2Title: "Proses Lokal & Cepat",
      pillar2Desc: "Didukung yt-dlp & ffmpeg. Berkas video digabung dan dikonversi langsung di komputer Anda tanpa server perantara.",
      pillar3Title: "Tanpa Akun atau Pendaftaran",
      pillar3Desc: "Tidak perlu login, cookie, atau email. Cukup tempel link dan simpan berkas langsung.",
      pillar4Title: "Pilihan Format Fleksibel",
      pillar4Desc: "Dapatkan kualitas sumber asli (hingga 1080p DASH), audio MP3 murni, atau video portrait 9:16 siap Status WhatsApp.",
      pillar5Title: "Mesin Multi-Platform",
      pillar5Desc: "Mendukung YouTube, TikTok, Instagram Reels, Twitter/X, dan Facebook secara andal.",
      pillar6Title: "Bebas Iklan & Aman",
      pillar6Desc: "Tanpa pop-under yang mengganggu, pelacak data, atau tombol palsu. Murni cepat dan aman.",
      aboutHowTitle: "Cara Download Video",
      step1Title: "Salin Link Video",
      step1Desc: "Buka YouTube, TikTok, Instagram, Twitter/X, atau Facebook dan salin link video dari bilah alamat browser atau tombol bagikan.",
      step2Title: "Tempel & Periksa",
      step2Desc: "Tempel link ke kolom SnatchVid lalu klik \"Periksa link\" untuk mengambil metadata video terverifikasi.",
      step3Title: "Pilih Kualitas & Simpan",
      step3Desc: "Pilih resolusi atau format output yang diinginkan (Original, Status WhatsApp, atau MP3) lalu klik \"Download video\".",
      metricsTriggerSuffix: "unduhan",
      metricsModalTitle: "Statistik Penggunaan",
      metricsModalSubtitle: "Statistik pengunduhan & pemrosesan media lokal",
      metricTotalDownloads: "Total Unduhan",
      metricSuccessRate: "Tingkat Keberhasilan",
      metricTotalDuration: "Total Durasi Media",
      metricMediaProcessed: "Media diproses",
      metricsPlatformBreakdown: "Perincian Platform",
      metricsFormatBreakdown: "Format Output",
      btnRefresh: "Segarkan",
      inspectedLabel: "diperiksa",
      failedLabel: "gagal",
      updatedJustNow: "Diperbarui: baru saja"
    }
  };

  let currentLang = localStorage.getItem('snatchvid_lang') || 'en';
  if (!I18N[currentLang]) currentLang = 'en';

  // DOM Elements - Navigation & Brand
  const navTabApp = document.getElementById('navTabApp');
  const navTabAbout = document.getElementById('navTabAbout');
  const viewApp = document.getElementById('viewApp');
  const viewAbout = document.getElementById('viewAbout');
  const brandHomeLink = document.getElementById('brandHomeLink');
  const langBtnEn = document.getElementById('langBtnEn');
  const langBtnId = document.getElementById('langBtnId');

  // DOM Elements - Workbench
  const urlInput = document.getElementById('videoUrl');
  const btnClear = document.getElementById('btnClear');
  const pillDesktop = document.getElementById('platformPillDesktop');
  const pillMobile = document.getElementById('platformPillMobile');
  const btnInspect = document.getElementById('btnInspect');
  const errorBanner = document.getElementById('errorBanner');
  const previewCard = document.getElementById('previewCard');
  const previewThumb = document.getElementById('previewThumb');
  const previewDurationTag = document.getElementById('previewDurationTag');
  const platformDisplayTag = document.getElementById('platformDisplayTag');
  const platformDisplayIcon = document.getElementById('platformDisplayIcon');
  const platformDisplayText = document.getElementById('platformDisplayText');
  const previewTitle = document.getElementById('previewTitle');
  const previewUploader = document.getElementById('previewUploader');
  const previewDuration = document.getElementById('previewDuration');
  const controlsGrid = document.getElementById('controlsGrid');
  const selectQuality = document.getElementById('selectQuality');
  const selectOutput = document.getElementById('selectOutput');
  const btnAdvanced = document.getElementById('btnAdvanced');
  const conditionalDrawer = document.getElementById('conditionalDrawer');
  const downloadSection = document.getElementById('downloadSection');
  const btnDownload = document.getElementById('btnDownload');
  const downloadProgressBar = document.getElementById('downloadProgressBar');
  const successCard = document.getElementById('successCard');
  const btnDownloadAnother = document.getElementById('btnDownloadAnother');

  // DOM Elements - Metrics
  const btnMetricsTrigger = document.getElementById('btnMetricsTrigger');
  const metricsHeaderBadge = document.getElementById('metricsHeaderBadge');
  const metricsModal = document.getElementById('metricsModal');
  const btnMetricsClose = document.getElementById('btnMetricsClose');
  const btnMetricsRefresh = document.getElementById('btnMetricsRefresh');
  const metricsLastUpdated = document.getElementById('metricsLastUpdated');
  
  const metricValDownloads = document.getElementById('metricValDownloads');
  const metricSubInspections = document.getElementById('metricSubInspections');
  const metricValSuccessRate = document.getElementById('metricValSuccessRate');
  const metricSubFailures = document.getElementById('metricSubFailures');
  const metricValDuration = document.getElementById('metricValDuration');

  const metricYTCount = document.getElementById('metricYTCount');
  const metricYTDur = document.getElementById('metricYTDur');
  const metricYTPct = document.getElementById('metricYTPct');
  const metricYTBar = document.getElementById('metricYTBar');

  const metricTTCount = document.getElementById('metricTTCount');
  const metricTTDur = document.getElementById('metricTTDur');
  const metricTTPct = document.getElementById('metricTTPct');
  const metricTTBar = document.getElementById('metricTTBar');

  const metricIGCount = document.getElementById('metricIGCount');
  const metricIGDur = document.getElementById('metricIGDur');
  const metricIGPct = document.getElementById('metricIGPct');
  const metricIGBar = document.getElementById('metricIGBar');

  const metricTWCount = document.getElementById('metricTWCount');
  const metricTWDur = document.getElementById('metricTWDur');
  const metricTWPct = document.getElementById('metricTWPct');
  const metricTWBar = document.getElementById('metricTWBar');

  const metricFBCount = document.getElementById('metricFBCount');
  const metricFBDur = document.getElementById('metricFBDur');
  const metricFBPct = document.getElementById('metricFBPct');
  const metricFBBar = document.getElementById('metricFBBar');

  const metricFmtOriginal = document.getElementById('metricFmtOriginal');
  const metricFmtWA = document.getElementById('metricFmtWA');
  const metricFmtMP3 = document.getElementById('metricFmtMP3');

  let cachedMetrics = null;

  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('snatchvid_lang', lang);

    document.documentElement.lang = lang;
    const dict = I18N[lang];

    // Update static text elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.innerHTML = dict[key];
      }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key]) {
        el.placeholder = dict[key];
      }
    });

    // Update active classes on switcher
    if (langBtnEn) langBtnEn.classList.toggle('active', lang === 'en');
    if (langBtnId) langBtnId.classList.toggle('active', lang === 'id');

    if (cachedMetrics) {
      renderMetrics(cachedMetrics);
    }
  }

  /* -----------------------------------------------------------------------
     Platforms & State Configuration
     ----------------------------------------------------------------------- */
  const BRAND_ICONS = {
    youtube: `<svg class="brand-icon yt-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>`,
    tiktok: `<svg class="brand-icon tt-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64c.298-.002.595.042.88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 3 15.68a6.34 6.34 0 0 0 10.86 4.47 6.27 6.27 0 0 0 1.88-4.47V8.84a8.16 8.16 0 0 0 4.74 1.49V6.89a4.86 4.86 0 0 1-.89-.2z"/></svg>`,
    instagram: `<svg class="brand-icon ig-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
    twitter: `<svg class="brand-icon tw-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
    facebook: `<svg class="brand-icon fb-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`
  };

  const PLATFORMS = {
    youtube: {
      name: 'YouTube',
      cls: 'youtube',
      icon: BRAND_ICONS.youtube,
      detectedLabel: 'YouTube detected'
    },
    tiktok: {
      name: 'TikTok',
      cls: 'tiktok',
      icon: BRAND_ICONS.tiktok,
      detectedLabel: 'TikTok detected'
    },
    instagram: {
      name: 'Instagram',
      cls: 'instagram',
      icon: BRAND_ICONS.instagram,
      detectedLabel: 'Instagram detected'
    },
    twitter: {
      name: 'Twitter / X',
      cls: 'twitter',
      icon: BRAND_ICONS.twitter,
      detectedLabel: 'Twitter / X detected'
    },
    facebook: {
      name: 'Facebook',
      cls: 'facebook',
      icon: BRAND_ICONS.facebook,
      detectedLabel: 'Facebook detected'
    }
  };

  // State machine
  let currentPlatform = null;
  let currentMetadata = null;
  let currentWADuration = 30;
  let ffmpegAvailable = true;
  let isInspecting = false;
  let isDownloading = false;

  /* -----------------------------------------------------------------------
     Navigation Tab Switching (App / About)
     ----------------------------------------------------------------------- */
  function switchView(viewName) {
    if (viewName === 'about') {
      if (navTabApp) navTabApp.classList.remove('active');
      if (navTabAbout) navTabAbout.classList.add('active');
      if (viewApp) viewApp.classList.remove('active');
      if (viewAbout) viewAbout.classList.add('active');
      window.location.hash = 'about';
    } else {
      if (navTabAbout) navTabAbout.classList.remove('active');
      if (navTabApp) navTabApp.classList.add('active');
      if (viewAbout) viewAbout.classList.remove('active');
      if (viewApp) viewApp.classList.add('active');
      window.location.hash = 'app';
    }
  }

  if (navTabApp) navTabApp.addEventListener('click', () => switchView('app'));
  if (navTabAbout) navTabAbout.addEventListener('click', () => switchView('about'));
  if (brandHomeLink) {
    brandHomeLink.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('app');
    });
  }

  // Handle direct hash navigation
  if (window.location.hash === '#about') {
    switchView('about');
  }

  // Language Switcher Events
  if (langBtnEn) langBtnEn.addEventListener('click', () => applyLanguage('en'));
  if (langBtnId) langBtnId.addEventListener('click', () => applyLanguage('id'));

  /* -----------------------------------------------------------------------
     Helper Functions
     ----------------------------------------------------------------------- */
  function detectPlatform(url) {
    if (!url) return null;
    if (/youtube\.com|youtu\.be/i.test(url)) return 'youtube';
    if (/tiktok\.com/i.test(url)) return 'tiktok';
    if (/instagram\.com/i.test(url)) return 'instagram';
    if (/twitter\.com|x\.com/i.test(url)) return 'twitter';
    if (/facebook\.com|fb\.watch/i.test(url)) return 'facebook';
    return null;
  }

  function showError(msg) {
    if (!errorBanner) return;
    errorBanner.textContent = msg;
    errorBanner.classList.add('show');
  }

  function clearError() {
    if (!errorBanner) return;
    errorBanner.textContent = '';
    errorBanner.classList.remove('show');
  }

  function setPlatformStatus(platform) {
    currentPlatform = platform;
    if (platform && PLATFORMS[platform]) {
      const p = PLATFORMS[platform];
      const pillHTML = `<span class="pill-icon-wrap">${p.icon}</span> <span>${p.detectedLabel}</span>`;
      
      if (pillDesktop) {
        pillDesktop.className = `platform-pill platform-pill-desktop show ${p.cls}`;
        pillDesktop.innerHTML = pillHTML;
      }

      if (pillMobile) {
        pillMobile.className = `platform-pill platform-pill-mobile show ${p.cls}`;
        pillMobile.innerHTML = pillHTML;
      }

      if (btnInspect) btnInspect.disabled = false;
    } else {
      if (pillDesktop) {
        pillDesktop.className = 'platform-pill platform-pill-desktop';
        pillDesktop.innerHTML = '';
      }

      if (pillMobile) {
        pillMobile.className = 'platform-pill platform-pill-mobile';
        pillMobile.innerHTML = '';
      }

      if (btnInspect) btnInspect.disabled = true;
    }
  }

  function resetToEmptyState() {
    currentMetadata = null;
    if (previewCard) previewCard.classList.remove('show');
    if (controlsGrid) controlsGrid.classList.remove('show');
    if (conditionalDrawer) conditionalDrawer.classList.remove('open');
    if (downloadSection) downloadSection.classList.remove('show');
    if (successCard) successCard.classList.remove('show');
    clearError();
  }

  /* -----------------------------------------------------------------------
     Backend Health Initialization (GET /api/health)
     ----------------------------------------------------------------------- */
  async function initBackendHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        ffmpegAvailable = !!data.ffmpeg;
      }
    } catch (e) {
      ffmpegAvailable = true;
    }
    updateOutputOptionsAvailability();
  }

  function updateOutputOptionsAvailability() {
    if (!selectOutput) return;
    const waOpt = selectOutput.querySelector('option[value="wa_status"]');
    const mp3Opt = selectOutput.querySelector('option[value="mp3"]');
    if (!ffmpegAvailable) {
      if (waOpt) {
        waOpt.disabled = true;
        waOpt.textContent = `${I18N[currentLang].optWhatsApp} (needs ffmpeg)`;
      }
      if (mp3Opt) {
        mp3Opt.disabled = true;
        mp3Opt.textContent = `${I18N[currentLang].optMp3} (needs ffmpeg)`;
      }
    }
  }

  /* -----------------------------------------------------------------------
     URL Input Events
     ----------------------------------------------------------------------- */
  if (urlInput) {
    urlInput.addEventListener('input', function () {
      const val = urlInput.value.trim();
      if (btnClear) btnClear.classList.toggle('show', val.length > 0);
      clearError();
      if (successCard) successCard.classList.remove('show');

      const p = detectPlatform(val);
      setPlatformStatus(p);
    });

    urlInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (btnInspect && !btnInspect.disabled) {
          btnInspect.click();
        }
      }
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', function () {
      if (urlInput) {
        urlInput.value = '';
        urlInput.focus();
      }
      btnClear.classList.remove('show');
      setPlatformStatus(null);
      resetToEmptyState();
    });
  }

  /* -----------------------------------------------------------------------
     Controls & Drawer Interactions
     ----------------------------------------------------------------------- */
  if (btnAdvanced && conditionalDrawer) {
    btnAdvanced.addEventListener('click', function () {
      conditionalDrawer.classList.toggle('open');
    });
  }

  if (selectOutput && conditionalDrawer) {
    selectOutput.addEventListener('change', function () {
      if (selectOutput.value === 'wa_status') {
        conditionalDrawer.classList.add('open');
      }
    });
  }

  document.querySelectorAll('.dur-pill-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.dur-pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentWADuration = parseInt(btn.dataset.sec, 10) || 30;
    });
  });

  if (btnDownloadAnother) {
    btnDownloadAnother.addEventListener('click', function () {
      if (urlInput) {
        urlInput.value = '';
        urlInput.focus();
      }
      if (btnClear) btnClear.classList.remove('show');
      setPlatformStatus(null);
      resetToEmptyState();
    });
  }

  /* -----------------------------------------------------------------------
     Demo Fallback for sketch1.png Mock
     ----------------------------------------------------------------------- */
  function loadDemoMock() {
    const demoData = {
      platform: 'youtube',
      platform_display: 'YouTube',
      title: 'How a tiny downloader works',
      uploader: 'RaflyLabs',
      duration: '04:32',
      duration_sec: 272,
      thumbnail: 'data:image/svg+xml;base64,' + btoa(`
        <svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
          <rect width="640" height="360" fill="#171714"/>
          <path d="M0,240 Q160,180 320,240 T640,240" fill="none" stroke="#2b2b27" stroke-width="2"/>
          <path d="M0,210 Q200,280 400,210 T640,210" fill="none" stroke="#2b2b27" stroke-width="2"/>
          <path d="M0,270 Q220,190 440,270 T640,270" fill="none" stroke="#2b2b27" stroke-width="2"/>
        </svg>
      `),
      formats: [
        { height: 1080 },
        { height: 720 },
        { height: 480 },
        { height: 360 }
      ]
    };
    currentMetadata = demoData;
    renderMediaPreview(demoData);
  }

  /* -----------------------------------------------------------------------
     Inspect Link Flow
     ----------------------------------------------------------------------- */
  async function fetchWithRetry(url, maxRetries = 3) {
    let lastError;
    for (let i = 0; i < maxRetries; i++) {
      try {
        const res = await fetch(url);
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.detail || `Server returned HTTP ${res.status}`);
        }
        return data;
      } catch (err) {
        lastError = err;
        if (i < maxRetries - 1) {
          await new Promise(r => setTimeout(r, 1500));
        }
      }
    }
    throw lastError;
  }

  if (btnInspect) {
    btnInspect.addEventListener('click', async function () {
      const url = urlInput ? urlInput.value.trim() : '';
      const dict = I18N[currentLang];
      if (!url) {
        showError(dict.errEmptyUrl);
        if (urlInput) urlInput.focus();
        return;
      }

      const platform = detectPlatform(url);
      if (!platform) {
        showError(dict.errUnsupportedUrl);
        return;
      }

      if (isInspecting) return;
      isInspecting = true;
      btnInspect.disabled = true;
      btnInspect.innerHTML = `<span class="spinner-inline"></span> ${dict.btnInspecting}`;
      clearError();
      if (successCard) successCard.classList.remove('show');

      // Built-in support for demo URLs
      if (url.includes('demo123') || url.includes('sketch-demo')) {
        setTimeout(() => {
          loadDemoMock();
          isInspecting = false;
          btnInspect.disabled = false;
          btnInspect.textContent = dict.btnInspect;
        }, 300);
        return;
      }

      try {
        const infoUrl = `/api/info?url=${encodeURIComponent(url)}`;
        const data = await fetchWithRetry(infoUrl, platform === 'tiktok' ? 3 : 1);
        currentMetadata = data;
        renderMediaPreview(data);
      } catch (err) {
        if (err.message && err.message.toLowerCase().includes('tiktok')) {
          showError(dict.errTiktokRetry);
        } else {
          showError(dict.errInspectFailed);
        }
        if (previewCard) previewCard.classList.remove('show');
        if (controlsGrid) controlsGrid.classList.remove('show');
        if (downloadSection) downloadSection.classList.remove('show');
      } finally {
        isInspecting = false;
        btnInspect.disabled = false;
        btnInspect.textContent = dict.btnInspect;
      }
    });
  }

  /* -----------------------------------------------------------------------
     Render Media Preview
     ----------------------------------------------------------------------- */
  function renderMediaPreview(meta) {
    const p = PLATFORMS[meta.platform] || {
      name: meta.platform_display || 'Video',
      cls: 'youtube',
      icon: '▶'
    };

    // Platform Tag
    if (platformDisplayTag) platformDisplayTag.className = `platform-display-tag ${p.cls}`;
    if (platformDisplayIcon) platformDisplayIcon.innerHTML = p.icon;
    if (platformDisplayText) platformDisplayText.textContent = p.name;

    // Title & Metadata
    if (previewTitle) {
      previewTitle.textContent = meta.title || 'Untitled video';
      previewTitle.title = meta.title || '';
    }
    if (previewUploader) previewUploader.textContent = meta.uploader || 'Creator';
    if (previewDuration) previewDuration.textContent = meta.duration || '0:00';
    if (previewDurationTag) previewDurationTag.textContent = meta.duration || '00:00';

    // Thumbnail with fallback
    if (previewThumb) {
      if (meta.thumbnail) {
        previewThumb.src = meta.thumbnail;
      } else {
        previewThumb.src = 'data:image/svg+xml;base64,' + btoa(`
          <svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
            <rect width="640" height="360" fill="#171714"/>
            <text x="320" y="190" fill="#8B867D" font-size="22" text-anchor="middle" font-family="sans-serif">No thumbnail</text>
          </svg>
        `);
      }
      previewThumb.alt = meta.title ? `Thumbnail of ${meta.title}` : 'Video thumbnail';
    }

    // Quality Select Population
    if (selectQuality) {
      selectQuality.innerHTML = '';
      const formats = Array.isArray(meta.formats) ? meta.formats : [];
      const heights = formats.map(f => f.height).filter(Boolean);

      const options = [{ value: 'best', label: I18N[currentLang].optBestQuality }];
      heights.forEach(h => {
        options.push({ value: h.toString(), label: `${h}p` });
      });

      options.forEach(opt => {
        const el = document.createElement('option');
        el.value = opt.value;
        el.textContent = opt.label;
        selectQuality.appendChild(el);
      });
    }

    // Activate UI sections
    if (previewCard) previewCard.classList.add('show');
    if (controlsGrid) controlsGrid.classList.add('show');
    if (downloadSection) downloadSection.classList.add('show');

    if (window.innerWidth <= 720 && previewCard) {
      previewCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  /* -----------------------------------------------------------------------
     Download Execution Flow
     ----------------------------------------------------------------------- */
  if (btnDownload) {
    btnDownload.addEventListener('click', async function () {
      const url = urlInput ? urlInput.value.trim() : '';
      const dict = I18N[currentLang];
      if (!url || !currentMetadata) return;

      // Demo simulation
      if (url.includes('demo123')) {
        isDownloading = true;
        btnDownload.disabled = true;
        btnDownload.innerHTML = `<span class="spinner-inline"></span> ${dict.btnPreparingDownload}`;
        if (downloadProgressBar) downloadProgressBar.classList.add('active');

        setTimeout(() => {
          btnDownload.innerHTML = `<span class="spinner-inline"></span> ${dict.btnDownloading}`;
        }, 400);

        setTimeout(() => {
          isDownloading = false;
          btnDownload.disabled = false;
          btnDownload.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>${dict.btnDownload}</span>
          `;
          if (downloadProgressBar) downloadProgressBar.classList.remove('active');
          if (successFilename) successFilename.textContent = 'How a tiny downloader works.mp4';
          if (successSize) successSize.textContent = '12.4 MB saved';
          if (successCard) successCard.classList.add('show');
        }, 1200);
        return;
      }

      if (isDownloading) return;
      isDownloading = true;
      btnDownload.disabled = true;
      btnDownload.innerHTML = `<span class="spinner-inline"></span> ${dict.btnPreparingDownload}`;
      if (downloadProgressBar) downloadProgressBar.classList.add('active');
      clearError();
      if (successCard) successCard.classList.remove('show');

      if (selectQuality) selectQuality.disabled = true;
      if (selectOutput) selectOutput.disabled = true;

      const quality = selectQuality ? selectQuality.value : 'best';
      const output = selectOutput ? selectOutput.value : 'original';
      const waDur = currentWADuration;

      try {
        const endpoint = `/api/download?url=${encodeURIComponent(url)}&quality=${encodeURIComponent(quality)}&output=${encodeURIComponent(output)}&wa_duration=${encodeURIComponent(waDur)}`;
        
        btnDownload.innerHTML = `<span class="spinner-inline"></span> ${dict.btnDownloading}`;

        const res = await fetch(endpoint);
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}));
          throw new Error(errBody.detail || `Server HTTP ${res.status}`);
        }

        const cd = res.headers.get('Content-Disposition') || '';
        let fname = 'video.mp4';
        const starMatch = cd.match(/filename\*=(?:UTF-8''|utf-8'')([^;]+)/i);
        if (starMatch) {
          try {
            fname = decodeURIComponent(starMatch[1].trim().replace(/^["']|["']$/g, ''));
          } catch (e) {
            fname = starMatch[1].trim().replace(/^["']|["']$/g, '');
          }
        } else {
          const match = cd.match(/filename="?([^";]+)"?/);
          if (match) fname = match[1];
        }

        const blob = await res.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = fname;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);

        const sizeMB = (blob.size / 1048576).toFixed(1);
        if (successFilename) successFilename.textContent = fname;
        if (successSize) successSize.textContent = `${sizeMB} MB saved`;
        if (successCard) successCard.classList.add('show');
      } catch (err) {
        if (err.message && err.message.includes('ffmpeg')) {
          showError(dict.errFfmpegMissing);
        } else {
          showError(dict.errDownloadFailed);
        }
      } finally {
        isDownloading = false;
        btnDownload.disabled = false;
        if (selectQuality) selectQuality.disabled = false;
        if (selectOutput) selectOutput.disabled = false;
        if (downloadProgressBar) downloadProgressBar.classList.remove('active');
        btnDownload.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <span>${dict.btnDownload}</span>
        `;
        fetchAndRenderMetrics();
      }
    });
  }

  /* -----------------------------------------------------------------------
     Usage Metrics & Modal Handlers
     ----------------------------------------------------------------------- */
  async function fetchAndRenderMetrics() {
    try {
      const res = await fetch('/api/metrics');
      if (res.ok) {
        cachedMetrics = await res.json();
        renderMetrics(cachedMetrics);
      }
    } catch (err) {
      console.warn('Could not fetch metrics:', err);
    }
  }

  function renderMetrics(data) {
    if (!data) return;
    const dict = I18N[currentLang];

    // Header badge
    if (metricsHeaderBadge) {
      metricsHeaderBadge.textContent = `${data.total_downloads} ${dict.metricsTriggerSuffix}`;
    }

    // Bento summary
    if (metricValDownloads) metricValDownloads.textContent = data.total_downloads;
    if (metricSubInspections) metricSubInspections.textContent = `${data.total_inspections} ${dict.inspectedLabel}`;
    if (metricValSuccessRate) metricValSuccessRate.textContent = `${data.success_rate}%`;
    if (metricSubFailures) metricSubFailures.textContent = `${data.failed_downloads} ${dict.failedLabel}`;
    if (metricValDuration) {
      const durObj = data.total_duration_formatted || {};
      metricValDuration.textContent = durObj[currentLang] || durObj.en || '0 sec';
    }

    // Platform Breakdown
    const p = data.platforms || {};

    // YouTube
    const yt = p.youtube || { downloaded: 0, share_percentage: 0, duration_formatted: {} };
    if (metricYTCount) metricYTCount.textContent = `${yt.downloaded} ${dict.metricsTriggerSuffix}`;
    if (metricYTDur) metricYTDur.textContent = yt.duration_formatted ? (yt.duration_formatted[currentLang] || yt.duration_formatted.en) : '0 sec';
    if (metricYTPct) metricYTPct.textContent = `${yt.share_percentage}%`;
    if (metricYTBar) metricYTBar.style.width = `${Math.min(100, yt.share_percentage)}%`;

    // TikTok
    const tt = p.tiktok || { downloaded: 0, share_percentage: 0, duration_formatted: {} };
    if (metricTTCount) metricTTCount.textContent = `${tt.downloaded} ${dict.metricsTriggerSuffix}`;
    if (metricTTDur) metricTTDur.textContent = tt.duration_formatted ? (tt.duration_formatted[currentLang] || tt.duration_formatted.en) : '0 sec';
    if (metricTTPct) metricTTPct.textContent = `${tt.share_percentage}%`;
    if (metricTTBar) metricTTBar.style.width = `${Math.min(100, tt.share_percentage)}%`;

    // Instagram
    const ig = p.instagram || { downloaded: 0, share_percentage: 0, duration_formatted: {} };
    if (metricIGCount) metricIGCount.textContent = `${ig.downloaded} ${dict.metricsTriggerSuffix}`;
    if (metricIGDur) metricIGDur.textContent = ig.duration_formatted ? (ig.duration_formatted[currentLang] || ig.duration_formatted.en) : '0 sec';
    if (metricIGPct) metricIGPct.textContent = `${ig.share_percentage}%`;
    if (metricIGBar) metricIGBar.style.width = `${Math.min(100, ig.share_percentage)}%`;

    // Twitter / X
    const tw = p.twitter || { downloaded: 0, share_percentage: 0, duration_formatted: {} };
    if (metricTWCount) metricTWCount.textContent = `${tw.downloaded} ${dict.metricsTriggerSuffix}`;
    if (metricTWDur) metricTWDur.textContent = tw.duration_formatted ? (tw.duration_formatted[currentLang] || tw.duration_formatted.en) : '0 sec';
    if (metricTWPct) metricTWPct.textContent = `${tw.share_percentage}%`;
    if (metricTWBar) metricTWBar.style.width = `${Math.min(100, tw.share_percentage)}%`;

    // Facebook
    const fb = p.facebook || { downloaded: 0, share_percentage: 0, duration_formatted: {} };
    if (metricFBCount) metricFBCount.textContent = `${fb.downloaded} ${dict.metricsTriggerSuffix}`;
    if (metricFBDur) metricFBDur.textContent = fb.duration_formatted ? (fb.duration_formatted[currentLang] || fb.duration_formatted.en) : '0 sec';
    if (metricFBPct) metricFBPct.textContent = `${fb.share_percentage}%`;
    if (metricFBBar) metricFBBar.style.width = `${Math.min(100, fb.share_percentage)}%`;

    // Formats
    const fmts = data.formats || {};
    if (metricFmtOriginal) metricFmtOriginal.textContent = fmts.original || 0;
    if (metricFmtWA) metricFmtWA.textContent = fmts.wa_status || 0;
    if (metricFmtMP3) metricFmtMP3.textContent = fmts.mp3 || 0;

    if (metricsLastUpdated) {
      metricsLastUpdated.textContent = dict.updatedJustNow;
    }
  }

  function openMetricsModal() {
    if (!metricsModal) return;
    metricsModal.hidden = false;
    void metricsModal.offsetWidth; // Force reflow
    metricsModal.classList.add('open');
    fetchAndRenderMetrics();
  }

  function closeMetricsModal() {
    if (!metricsModal) return;
    metricsModal.classList.remove('open');
    setTimeout(() => {
      if (!metricsModal.classList.contains('open')) {
        metricsModal.hidden = true;
      }
    }, 240);
  }

  if (btnMetricsTrigger) btnMetricsTrigger.addEventListener('click', openMetricsModal);
  if (btnMetricsClose) btnMetricsClose.addEventListener('click', closeMetricsModal);
  if (btnMetricsRefresh) btnMetricsRefresh.addEventListener('click', fetchAndRenderMetrics);

  if (metricsModal) {
    metricsModal.addEventListener('click', function (e) {
      if (e.target === metricsModal) {
        closeMetricsModal();
      }
    });
  }

  window.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && metricsModal && !metricsModal.hidden) {
      closeMetricsModal();
    }
  });

  // Initialize language, backend health & usage metrics
  applyLanguage(currentLang);
  initBackendHealth();
  fetchAndRenderMetrics();

})();
