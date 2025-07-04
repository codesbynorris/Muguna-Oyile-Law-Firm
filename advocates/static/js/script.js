document.addEventListener("DOMContentLoaded", function () {
  // =====================
  // MOBILE MENU TOGGLE
  // =====================
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navMenu = document.getElementById("navMenu");
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

  // Toggle mobile menu
  function toggleMobileMenu() {
    const isExpanded = mobileMenuBtn.getAttribute("aria-expanded") === "true";
    mobileMenuBtn.setAttribute("aria-expanded", !isExpanded);
    navMenu.classList.toggle("active");
    document.body.classList.toggle("menu-open");
  }

  // Close mobile menu
  function closeMobileMenu() {
    mobileMenuBtn.setAttribute("aria-expanded", "false");
    navMenu.classList.remove("active");
    document.body.classList.remove("menu-open");
    document.querySelectorAll('.dropdown').forEach(d => {
    d.classList.remove('active');
  });
  }

  if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      toggleMobileMenu();
    });

    // Close menu when clicking outside
    document.addEventListener("click", function(e) {
      if (!navMenu.contains(e.target) && e.target !== mobileMenuBtn) {
        closeMobileMenu();
      }
    });
  }

  // =====================
  // DROPDOWN MENUS
  // =====================
  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      if (window.innerWidth <= 767) {
        e.preventDefault();
        e.stopPropagation();
        
        const dropdown = this.parentElement;
        const wasActive = dropdown.classList.contains('active');
        
        // Close all dropdowns first
        document.querySelectorAll('.dropdown').forEach(d => {
          d.classList.remove('active');
        });
        
        // Reopen current if it wasn't active
        if (!wasActive) {
          dropdown.classList.add('active');
        }
      }
    });
  });

  // Close dropdowns when clicking outside on mobile
  document.addEventListener('click', function(e) {
    if (window.innerWidth <= 767 && !e.target.closest('.dropdown')) {
      document.querySelectorAll('.dropdown').forEach(dropdown => {
        dropdown.classList.remove('active');
      });
    }
  });

  // Close menu when clicking regular nav links (not dropdown toggles)
document.querySelectorAll('#navMenu a:not(.dropdown-toggle)').forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth <= 767) {
      closeMobileMenu();
    }
  });
});

  // =====================
  // SERVICE CARDS TOGGLE
  // =====================
  const serviceCards = document.querySelectorAll('.service-card');
  if (serviceCards.length > 0) {
    // Initialize - no service details open by default
    document.querySelectorAll('.mobile-service-detail').forEach(detail => {
      detail.classList.remove('active');
    });

    serviceCards.forEach(card => {
      card.addEventListener('click', function() {
        if (window.innerWidth <= 992) {
          const serviceId = this.getAttribute('data-service-id');
          const detail = document.getElementById(`mobile-${serviceId}-detail`);
          
          // Close all other details
          document.querySelectorAll('.mobile-service-detail').forEach(d => {
            if (d !== detail) d.classList.remove('active');
          });
          
          // Toggle current detail
          if (detail) {
            detail.classList.toggle('active');
            
            // Toggle active state for styling
            document.querySelectorAll('.service-card').forEach(c => {
              c.classList.remove('active');
            });
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
          const headerHeight = document.getElementById("header").offsetHeight;
          const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

          window.scrollTo({
            top: targetPosition,
            behavior: "smooth"
          });

          // Close mobile menu if open
          if (window.innerWidth <= 767) {
            closeMobileMenu();
          }

          // Update URL without page reload
          if (history.pushState) {
            history.pushState(null, null, targetId);
          } else {
            location.hash = targetId;
          }
        }
      }
    });
  });

  // =====================
  // STICKY HEADER
  // =====================
  const header = document.getElementById("header");
  if (header) {
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
      const currentScroll = window.pageYOffset;
      
      if (currentScroll <= 0) {
        header.classList.remove("sticky");
        return;
      }
      
      if (currentScroll > lastScroll && currentScroll > header.offsetHeight) {
        // Scrolling down
        header.classList.remove("sticky");
      } else {
        // Scrolling up
        header.classList.add("sticky");
      }
      lastScroll = currentScroll;
    });
  }

  // =====================
  // BACK TO TOP BUTTON
  // =====================
  const backToTopBtn = document.getElementById("backToTop");
  if (backToTopBtn) {
    window.addEventListener('scroll', function() {
      if (window.pageYOffset > 300) {
        backToTopBtn.classList.add("active");
      } else {
        backToTopBtn.classList.remove("active");
      }
    });

    backToTopBtn.addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
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
          const value = Math.floor(progress * target);
          stat.textContent = value;
          
          if (progress < 1) {
            requestAnimationFrame(updateCounter);
          }
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
    if (aboutSection) {
      observer.observe(aboutSection);
    }
  }

  // =====================
  // NEWSLETTER FORM
  // =====================
  const newsletterForm = document.querySelector(".newsletter-form");
  if (newsletterForm) {
    newsletterForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();

      if (validateEmail(email)) {
        // Here you would typically make an AJAX call to your backend
        showNotification("Thank you for subscribing to our newsletter!", "success");
        this.reset();
      } else {
        showNotification("Please enter a valid email address.", "error");
      }
    });
  }

  // Email validation helper
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  // Notification helper
  function showNotification(message, type) {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add("show");
    }, 10);
    
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }

  // Handle window resize
  window.addEventListener('resize', function() {
    // Reset service cards on desktop
    if (window.innerWidth > 992) {
      document.querySelectorAll('.mobile-service-detail').forEach(detail => {
        detail.classList.remove('active');
      });
      document.querySelectorAll('.service-card').forEach(card => {
        card.classList.remove('active');
      });
    }
    
    // Close mobile menu if resizing to desktop
    if (window.innerWidth > 767 && navMenu.classList.contains("active")) {
      closeMobileMenu();
    }
  });
});