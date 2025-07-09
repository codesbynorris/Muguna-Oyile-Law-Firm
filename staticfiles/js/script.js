document.addEventListener("DOMContentLoaded", function () {
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navMenu = document.getElementById("navMenu");
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  const header = document.getElementById("header");
  const backToTopBtn = document.getElementById("backToTop");
  const serviceCards = document.querySelectorAll('.service-card');
  const newsletterForm = document.querySelector(".newsletter-form");

  let isMobileMenuOpen = false;
  let isMobile = window.innerWidth <= 767;

  // =====================
  // DROPDOWN SETUP LOGIC
  // =====================
  function setupDropdowns() {
    dropdownToggles.forEach(toggle => {
      const dropdown = toggle.parentElement;
      const menu = dropdown.querySelector('.dropdown-menu');

      dropdown.replaceWith(dropdown.cloneNode(true)); // reset events
    });

    document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
      const dropdown = toggle.parentElement;
      const menu = dropdown.querySelector('.dropdown-menu');

      if (!menu) return;

      if (!isMobile) {
        // Desktop - hover
        dropdown.addEventListener('mouseenter', () => {
          toggleDropdown(dropdown, true);
        });

        dropdown.addEventListener('mouseleave', () => {
          toggleDropdown(dropdown, false);
        });

        toggle.addEventListener('focus', () => {
          toggleDropdown(dropdown, true);
        });

        dropdown.addEventListener('blur', (e) => {
          if (!dropdown.contains(e.relatedTarget)) {
            toggleDropdown(dropdown, false);
          }
        });
      } else {
        // Mobile - click
        toggle.addEventListener('click', function (e) {
          e.preventDefault();
          const wasActive = dropdown.classList.contains('active');

          document.querySelectorAll('.dropdown').forEach(d => {
            if (d !== dropdown) toggleDropdown(d, false);
          });

          toggleDropdown(dropdown, !wasActive);
        });
      }
    });
  }

  function toggleDropdown(dropdown, open) {
    const menu = dropdown.querySelector('.dropdown-menu');
    if (!menu) return;

    if (open) {
      dropdown.classList.add('active');
      menu.style.display = 'block';
      setTimeout(() => {
        menu.style.maxHeight = menu.scrollHeight + 'px';
        menu.style.opacity = '1';
        menu.style.visibility = 'visible';
      }, 10);
    } else {
      menu.style.maxHeight = '0';
      menu.style.opacity = '0';
      menu.style.visibility = 'hidden';
      setTimeout(() => {
        menu.style.display = 'none';
        dropdown.classList.remove('active');
      }, 300);
    }
  }

  function closeAllDropdowns() {
    document.querySelectorAll('.dropdown').forEach(dropdown => {
      toggleDropdown(dropdown, false);
    });
  }

  // =====================
  // MOBILE MENU TOGGLE
  // =====================
  function toggleMobileMenu() {
    isMobileMenuOpen = !isMobileMenuOpen;
    mobileMenuBtn.setAttribute("aria-expanded", isMobileMenuOpen);
    navMenu.classList.toggle("active", isMobileMenuOpen);
    document.body.classList.toggle("menu-open", isMobileMenuOpen);
    if (isMobileMenuOpen) closeAllDropdowns();
  }

  function closeMobileMenu() {
    isMobileMenuOpen = false;
    mobileMenuBtn.setAttribute("aria-expanded", "false");
    navMenu.classList.remove("active");
    document.body.classList.remove("menu-open");
    closeAllDropdowns();
  }

  if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      toggleMobileMenu();
    });
  }

  // =====================
  // CLICK OUTSIDE TO CLOSE
  // =====================
  document.addEventListener('click', function(e) {
    if (isMobileMenuOpen && !navMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
      closeMobileMenu();
    }

    if (!e.target.closest('.dropdown')) {
      closeAllDropdowns();
    }
  });

  // =====================
  // CLOSE ON NAV LINK CLICK
  // =====================
  document.querySelectorAll('#navMenu a:not(.dropdown-toggle)').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 767) closeMobileMenu();
    });
  });

  // =====================
  // SERVICE CARDS TOGGLE
  // =====================
  if (serviceCards.length > 0) {
    serviceCards.forEach(card => {
      card.addEventListener('click', function() {
        if (window.innerWidth <= 992) {
          const serviceId = this.getAttribute('data-service-id');
          const detail = document.getElementById(`mobile-${serviceId}-detail`);

          document.querySelectorAll('.mobile-service-detail').forEach(d => {
            if (d !== detail) d.classList.remove('active');
          });

          if (detail) {
            detail.classList.toggle('active');
            document.querySelectorAll('.service-card').forEach(c => c.classList.remove('active'));
            this.classList.toggle('active', detail.classList.contains('active'));
          }
        }
      });
    });
  }

  // =====================
  // SMOOTH SCROLLING
  // =====================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      if (this.getAttribute("href").startsWith("#") && this.getAttribute("href").length > 1) {
        e.preventDefault();
        const targetId = this.getAttribute("href");
        const target = document.querySelector(targetId);

        if (target) {
          const headerHeight = header?.offsetHeight || 0;
          const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

          window.scrollTo({
            top: targetPosition,
            behavior: "smooth"
          });

          if (window.innerWidth <= 767) closeMobileMenu();
          history.pushState?.(null, null, targetId);
        }
      }
    });
  });

  // =====================
  // STICKY HEADER
  // =====================
  if (header) {
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
      const currentScroll = window.pageYOffset;

      if (currentScroll <= 0) {
        header.classList.remove("sticky");
        return;
      }

      if (currentScroll > lastScroll && currentScroll > header.offsetHeight) {
        header.classList.remove("sticky");
      } else {
        header.classList.add("sticky");
      }
      lastScroll = currentScroll;
    });
  }

  // =====================
  // BACK TO TOP BUTTON
  // =====================
  if (backToTopBtn) {
    window.addEventListener('scroll', function() {
      backToTopBtn.classList.toggle("active", window.pageYOffset > 300);
    });

    backToTopBtn.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // =====================
  // STATS COUNTER ANIMATION
  // =====================
  const statNumbers = document.querySelectorAll(".stat-number");
  if (statNumbers.length > 0) {
    const animateStats = () => {
      statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute("data-count")) || 0;
        const duration = 2000;
        const startTime = performance.now();

        const updateCounter = (timestamp) => {
          const progress = Math.min((timestamp - startTime) / duration, 1);
          stat.textContent = Math.floor(progress * target);
          if (progress < 1) requestAnimationFrame(updateCounter);
        };

        requestAnimationFrame(updateCounter);
      });
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateStats();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    const aboutSection = document.querySelector(".about");
    if (aboutSection) observer.observe(aboutSection);
  }

  // =====================
  // NEWSLETTER FORM
  // =====================
  if (newsletterForm) {
    newsletterForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();

      if (validateEmail(email)) {
        showNotification("Thank you for subscribing to our newsletter!", "success");
        this.reset();
      } else {
        showNotification("Please enter a valid email address.", "error");
      }
    });
  }

  // =====================
  // WINDOW RESIZE HANDLER
  // =====================
  function handleResize() {
    const newIsMobile = window.innerWidth <= 767;
    if (newIsMobile !== isMobile) {
      isMobile = newIsMobile;
      closeAllDropdowns();
      setupDropdowns();
    }

    if (window.innerWidth > 767 && isMobileMenuOpen) {
      closeMobileMenu();
    }

    if (window.innerWidth > 992) {
      document.querySelectorAll('.mobile-service-detail, .service-card').forEach(el => {
        el.classList.remove('active');
      });
    }
  }

  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(handleResize, 250);
  });

  // =====================
  // HELPER FUNCTIONS
  // =====================
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function showNotification(message, type) {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add("show"), 10);
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
  }

  // Initialize dropdowns
  setupDropdowns();
});

document.getElementById('learnMoreBtn').addEventListener('click', function(e) {
  const target = document.getElementById('services');
  if (target) {
    e.preventDefault();
    window.scrollTo({
      top: target.offsetTop,
      behavior: 'smooth'
    });
  }
});