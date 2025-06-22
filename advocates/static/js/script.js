document.addEventListener("DOMContentLoaded", function () {
  // =====================
  // MOBILE MENU TOGGLE
  // =====================
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navMenu = document.getElementById("navMenu");

  // Toggle menu on button click
  mobileMenuBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    navMenu.classList.toggle("active");
    mobileMenuBtn.innerHTML = navMenu.classList.contains("active")
      ? '<i class="fas fa-times"></i>'
      : '<i class="fas fa-bars"></i>';
  });

  // Close menu when clicking outside
  document.addEventListener("click", function (e) {
    if (!navMenu.contains(e.target) && e.target !== mobileMenuBtn) {
      navMenu.classList.remove("active");
      mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    }
  });

  // =====================
  // SMOOTH SCROLLING
  // =====================
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      // Skip if it's a URL anchor (like mailto: or tel:)
      if (
        this.getAttribute("href").startsWith("#") &&
        this.getAttribute("href").length > 1
      ) {
        e.preventDefault();
        const targetId = this.getAttribute("href");
        const target = document.querySelector(targetId);

        if (target) {
          const headerHeight = document.getElementById("header").offsetHeight;
          const targetPosition =
            target.getBoundingClientRect().top +
            window.pageYOffset -
            headerHeight;

          window.scrollTo({
            top: targetPosition,
            behavior: "smooth",
          });

          // Close mobile menu if open
          navMenu.classList.remove("active");
          mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';

          // Update URL without adding to history
          history.replaceState(null, null, targetId);
        }
      }
    });
  });

  // =====================
  // STICKY HEADER
  // =====================
  const header = document.getElementById("header");
  window.addEventListener("scroll", () => {
    header.classList.toggle("sticky", window.scrollY > 50);
  });

  // =====================
  // BACK TO TOP BUTTON
  // =====================
  const backToTopBtn = document.getElementById("backToTop");
  window.addEventListener("scroll", function () {
    backToTopBtn.classList.toggle("active", window.pageYOffset > 300);
  });

  backToTopBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // =====================
  // STATS COUNTER ANIMATION
  // =====================
  const statNumbers = document.querySelectorAll(".stat-number");
  if (statNumbers.length > 0) {
    const animateStats = () => {
      statNumbers.forEach((stat) => {
        const target = parseInt(stat.getAttribute("data-count"));
        const duration = 2000;
        const step = target / (duration / 16);

        let current = 0;
        const increment = () => {
          current += step;
          if (current < target) {
            stat.textContent = Math.floor(current);
            requestAnimationFrame(increment);
          } else {
            stat.textContent = target;
          }
        };
        increment();
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

    observer.observe(document.querySelector(".about"));
  }

  // =====================
  // NEWSLETTER FORM
  // =====================
  const newsletterForm = document.querySelector(".newsletter-form");
  if (newsletterForm) {
    newsletterForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const emailInput = this.querySelector('input[type="email"]');

      // Simple validation
      if (emailInput.value && emailInput.value.includes("@")) {
        // Here you would typically make an AJAX call to your backend
        alert("Thank you for subscribing to our newsletter!");
        this.reset();
      } else {
        alert("Please enter a valid email address.");
      }
    });
  }
});


// 101
 function toggleService(card, serviceId) {
   // For desktop view
   if (window.innerWidth > 992) {
     document.querySelectorAll(".service-detail").forEach((detail) => {
       detail.classList.remove("active");
     });

     document.querySelectorAll(".service-card").forEach((card) => {
       card.classList.remove("active");
     });

     document.getElementById(serviceId + "-detail").classList.add("active");
     card.classList.add("active");
   }
   // For mobile view
   else {
     // Close all other mobile details
     document.querySelectorAll(".mobile-service-detail").forEach((detail) => {
       if (detail.id !== "mobile-" + serviceId + "-detail") {
         detail.classList.remove("active");
       }
     });

     // Toggle clicked card's mobile detail
     const mobileDetail = document.getElementById(
       "mobile-" + serviceId + "-detail"
     );
     mobileDetail.classList.toggle("active");

     // Toggle active state for styling
     document.querySelectorAll(".service-card").forEach((card) => {
       card.classList.remove("active");
     });
     card.classList.toggle("active");
   }
 }

 // Initialize first card as active on mobile
 document.addEventListener("DOMContentLoaded", function () {
   if (window.innerWidth <= 992) {
     document.getElementById("mobile-tax-detail").classList.add("active");
   }
 });

 // Handle window resize to maintain proper state
 window.addEventListener("resize", function () {
   if (window.innerWidth > 992) {
     // Reset mobile details when switching back to desktop
     document.querySelectorAll(".mobile-service-detail").forEach((detail) => {
       detail.classList.remove("active");
     });
   } else {
     // Ensure the first card is active when switching to mobile
     if (!document.querySelector(".mobile-service-detail.active")) {
       document.getElementById("mobile-tax-detail").classList.add("active");
       document.querySelector(".service-card").classList.add("active");
     }
   }
 });