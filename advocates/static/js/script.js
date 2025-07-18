document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navMenu = document.getElementById("navMenu");
  const dropdownToggles = document.querySelectorAll(".dropdown-toggle");
  const header = document.getElementById("header");
  const backToTopBtn = document.getElementById("backToTop");
  const serviceCards = document.querySelectorAll(".service-card");
  const newsletterForm = document.querySelector(".newsletter-form");

  let isMobileMenuOpen = false;
  let isMobile = window.innerWidth <= 767;

  // Update header height dynamically
  const updateHeaderHeight = () => {
    if (header) {
      document.documentElement.style.setProperty("--header-height", `${header.offsetHeight}px`);
    }
  };
  updateHeaderHeight();

  // Dropdown menu handling
  const setupDropdowns = () => {
    dropdownToggles.forEach((toggle) => {
      const dropdown = toggle.parentElement;
      const menu = dropdown.querySelector(".dropdown-menu");
      if (!menu) return;

      if (!isMobile) {
        // Desktop: Hover and focus
        dropdown.addEventListener("mouseenter", () => toggleDropdown(dropdown, true));
        dropdown.addEventListener("mouseleave", () => toggleDropdown(dropdown, false));
        toggle.addEventListener("focus", () => toggleDropdown(dropdown, true));
        dropdown.addEventListener("focusout", (e) => {
          if (!dropdown.contains(e.relatedTarget)) toggleDropdown(dropdown, false);
        });
      } else {
        // Mobile: Click
        toggle.addEventListener("click", (e) => {
          e.preventDefault();
          const isActive = dropdown.classList.contains("active");
          document.querySelectorAll(".dropdown").forEach((d) => {
            if (d !== dropdown) toggleDropdown(d, false);
          });
          toggleDropdown(dropdown, !isActive);
        });
      }
    });
  };

  const toggleDropdown = (dropdown, open) => {
    const menu = dropdown.querySelector(".dropdown-menu");
    if (!menu) return;

    if (open) {
      dropdown.classList.add("active");
      menu.style.display = "block";
      setTimeout(() => {
        menu.style.maxHeight = `${menu.scrollHeight}px`;
        menu.style.opacity = "1";
        menu.style.visibility = "visible";
      }, 10);
    } else {
      menu.style.maxHeight = "0";
      menu.style.opacity = "0";
      menu.style.visibility = "hidden";
      setTimeout(() => {
        menu.style.display = "none";
        dropdown.classList.remove("active");
      }, 300);
    }
  };

  const closeAllDropdowns = () => {
    document.querySelectorAll(".dropdown").forEach((dropdown) => toggleDropdown(dropdown, false));
  };

  // Mobile menu toggle
  const toggleMobileMenu = () => {
    isMobileMenuOpen = !isMobileMenuOpen;
    mobileMenuBtn.setAttribute("aria-expanded", isMobileMenuOpen);
    navMenu.classList.toggle("active", isMobileMenuOpen);
    document.body.classList.toggle("menu-open", isMobileMenuOpen);
    mobileMenuBtn.classList.toggle("active", isMobileMenuOpen); // Added for icon transition
    if (isMobileMenuOpen) closeAllDropdowns();
  };

  const closeMobileMenu = () => {
    isMobileMenuOpen = false;
    mobileMenuBtn.setAttribute("aria-expanded", "false");
    navMenu.classList.remove("active");
    document.body.classList.remove("menu-open");
    mobileMenuBtn.classList.remove("active");
    closeAllDropdowns();
  };

  if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleMobileMenu();
    });
  }

  // Close menu on outside click
  document.addEventListener("click", (e) => {
    if (isMobileMenuOpen && !navMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
      closeMobileMenu();
    }
    if (!e.target.closest(".dropdown")) closeAllDropdowns();
  });

  // Close menu on nav link click
  document.querySelectorAll("#navMenu a:not(.dropdown-toggle)").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 767) closeMobileMenu();
    });
  });

  // Service cards toggle
  if (serviceCards.length) {
    serviceCards.forEach((card) => {
      card.addEventListener("click", () => {
        if (window.innerWidth <= 992) {
          const serviceId = card.getAttribute("data-service-id");
          const detail = document.getElementById(`mobile-${serviceId}-detail`);
          document.querySelectorAll(".mobile-service-detail").forEach((d) => {
            if (d !== detail) d.classList.remove("active");
          });
          if (detail) {
            detail.classList.toggle("active");
            document.querySelectorAll(".service-card").forEach((c) => c.classList.remove("active"));
            card.classList.toggle("active", detail.classList.contains("active"));
          }
        }
      });
    });
  }

  // Smooth scrolling
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const href = anchor.getAttribute("href");
      if (href.startsWith("#") && href.length > 1) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          const headerHeight = header?.offsetHeight || 0;
          const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
          window.scrollTo({ top: targetPosition, behavior: "smooth" });
          if (window.innerWidth <= 767) closeMobileMenu();
          history.pushState?.(null, null, href);
        }
      }
    });
  });

  // Sticky header
  if (header) {
    window.addEventListener("scroll", () => {
      header.classList.toggle("sticky", window.pageYOffset > 0);
    });
  }

  // Back to top button
  if (backToTopBtn) {
    window.addEventListener("scroll", () => {
      backToTopBtn.classList.toggle("active", window.pageYOffset > 300);
    });
    backToTopBtn.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Stats counter animation
  const statNumbers = document.querySelectorAll(".stat-number");
  if (statNumbers.length) {
    const animateStats = () => {
      statNumbers.forEach((stat) => {
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
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateStats();
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    const aboutSection = document.querySelector(".about");
    if (aboutSection) observer.observe(aboutSection);
  }

  // Newsletter form
  if (newsletterForm) {
    newsletterForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const emailInput = newsletterForm.querySelector('input[type="email"]');
      const email = emailInput.value.trim();
      if (validateEmail(email)) {
        showNotification("Thank you for subscribing to our newsletter!", "success");
        newsletterForm.reset();
      } else {
        showNotification("Please enter a valid email address.", "error");
      }
    });
  }

  // Resize handler
  const handleResize = () => {
    const newIsMobile = window.innerWidth <= 767;
    if (newIsMobile !== isMobile) {
      isMobile = newIsMobile;
      closeAllDropdowns();
      setupDropdowns();
    }
    if (window.innerWidth > 767 && isMobileMenuOpen) closeMobileMenu();
    if (window.innerWidth > 992) {
      document.querySelectorAll(".mobile-service-detail, .service-card").forEach((el) => {
        el.classList.remove("active");
      });
    }
    updateHeaderHeight();
  };

  window.addEventListener("resize", () => {
    clearTimeout(window.resizeTimer);
    window.resizeTimer = setTimeout(handleResize, 250);
  });

  // Helper functions
  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const showNotification = (message, type) => {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add("show"), 10);
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
  };

  // Initialize
  setupDropdowns();
});

// Learn More button
document.getElementById("learnMoreBtn")?.addEventListener("click", (e) => {
  const target = document.getElementById("services");
  if (target) {
    e.preventDefault();
    window.scrollTo({ top: target.offsetTop, behavior: "smooth" });
  }
});