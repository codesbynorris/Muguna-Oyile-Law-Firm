document.addEventListener('DOMContentLoaded', function() {
  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const navMenu = document.getElementById('navMenu');
  
  mobileMenuBtn.addEventListener('click', () => {
  navMenu.classList.toggle('active');
  mobileMenuBtn.innerHTML = navMenu.classList.contains('active') 
    ? '<i class="fas fa-times"></i>' 
    : '<i class="fas fa-bars"></i>';
});

  // Close mobile menu when clicking a link
document.querySelectorAll('#navMenu a').forEach(link => {
  link.addEventListener('click', () => {
    navMenu.classList.remove('active');
    mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
  });
});

  // Smooth Scrolling for all links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const target = document.querySelector(targetId);
      
      if (target) {
        const headerHeight = document.getElementById('header').offsetHeight;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
        
        // Update URL without adding to history
        history.replaceState(null, null, targetId);
      }
    });
  });

  // Sticky Header
  window.addEventListener('scroll', () => {
  const header = document.getElementById('header');
  header.classList.toggle('sticky', window.scrollY > 50);
});

  // Back to Top Button
  const backToTopBtn = document.getElementById('backToTop');
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopBtn.classList.add('active');
    } else {
      backToTopBtn.classList.remove('active');
    }
  });
  
  backToTopBtn.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // Animate Stats Counter
  const statNumbers = document.querySelectorAll('.stat-number');
  if (statNumbers.length > 0) {
    const animateStats = () => {
      statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-count'));
        const duration = 2000; // Animation duration in ms
        const step = target / (duration / 16); // 16ms per frame
        
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
    
    // Intersection Observer to trigger animation when section is in view
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateStats();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    
    observer.observe(document.querySelector('.about'));
  }

  // Contact Form Handling
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      // Form validation
      const name = document.getElementById('name');
      const email = document.getElementById('email');
      const message = document.getElementById('message');
      let isValid = true;
      
      // Clear previous errors
      document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
      
      // Validate name
      if (!name.value.trim()) {
        document.getElementById('name_error').textContent = 'Please enter your name';
        isValid = false;
      }
      
      // Validate email
      if (!email.value.trim()) {
        document.getElementById('email_error').textContent = 'Please enter your email';
        isValid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
        document.getElementById('email_error').textContent = 'Please enter a valid email';
        isValid = false;
      }
      
      // Validate message
      if (!message.value.trim()) {
        document.getElementById('message_error').textContent = 'Please enter your message';
        isValid = false;
      }
      
      if (!isValid) return;
      
      // Form submission
      const formData = new FormData(contactForm);
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      
      try {
        // Change button state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        // Simulate form submission (replace with actual fetch request)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Show thank you message
        showThankYouMessage();
        
        // Reset form
        contactForm.reset();
        
      } catch (error) {
        console.error('Form submission error:', error);
        alert('There was an error sending your message. Please try again.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Message';
      }
    });
  }
  
  // Show thank you message
  function showThankYouMessage() {
    const thankYouMessage = document.createElement('div');
    thankYouMessage.className = 'thank-you-message active';
    thankYouMessage.innerHTML = `
      <i class="fas fa-check-circle"></i> 
      Thank you for your message! We'll get back to you soon.
    `;
    document.body.appendChild(thankYouMessage);
    
    // Remove message after 5 seconds
    setTimeout(() => {
      thankYouMessage.classList.remove('active');
      setTimeout(() => {
        thankYouMessage.remove();
      }, 500);
    }, 5000);
  }
  
  // Modal functionality
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const modals = document.querySelectorAll('.modal');
  const closeButtons = document.querySelectorAll('.close-modal');
  
  // Open modal
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const modalId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });
  });
  
  // Close modal
  function closeModal(modal) {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
  }
  
  closeButtons.forEach(button => {
    button.addEventListener('click', () => {
      const modal = button.closest('.modal');
      closeModal(modal);
    });
  });
  
  // Close when clicking outside modal
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
      closeModal(e.target);
    }
  });
  
  // Close with ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modals.forEach(modal => {
        if (modal.classList.contains('active')) {
          closeModal(modal);
        }
      });
    }
  });
});