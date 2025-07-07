document.addEventListener('DOMContentLoaded', function() {
            const serviceCards = document.querySelectorAll('.service-card');
            
            // Initialize first service on desktop
            if (window.innerWidth >= 992) {
                const firstDetail = document.querySelector('.service-detail');
                if (firstDetail) firstDetail.classList.add('active');
                if (serviceCards[0]) serviceCards[0].classList.add('active');
            }

            // Add click handlers
            serviceCards.forEach(card => {
                card.addEventListener('click', function() {
                    const serviceId = this.getAttribute('data-service');
                    
                    if (window.innerWidth >= 992) {
                        // Desktop behavior
                        document.querySelectorAll('.service-detail').forEach(d => d.classList.remove('active'));
                        document.querySelectorAll('.service-card').forEach(c => c.classList.remove('active'));
                        
                        this.classList.add('active');
                        document.getElementById(`${serviceId}-detail`).classList.add('active');
                    } else {
                        // Mobile behavior - toggle this card
                        const isActive = this.classList.contains('active');
                        
                        // Close all other cards
                        document.querySelectorAll('.service-card').forEach(c => {
                            if (c !== this) c.classList.remove('active');
                        });
                        
                        // Toggle this card
                        this.classList.toggle('active');
                        
                        // Smooth scroll to show content if opening
                        if (!isActive) {
                            setTimeout(() => {
                                this.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            }, 300);
                        }
                    }
                });
            });

            // Handle window resize
            window.addEventListener('resize', function() {
                if (window.innerWidth >= 992) {
                    // Switching to desktop - close all mobile details
                    document.querySelectorAll('.service-card').forEach(card => {
                        card.classList.remove('active');
                    });
                    
                    // Activate first if none active
                    if (!document.querySelector('.service-card.active')) {
                        const firstCard = document.querySelector('.service-card');
                        if (firstCard) firstCard.classList.add('active');
                        const firstDetail = document.querySelector('.service-detail');
                        if (firstDetail) firstDetail.classList.add('active');
                    }
                }
            });
        });