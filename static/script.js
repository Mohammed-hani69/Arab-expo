// Menu functionality
const menuIcon = document.getElementById('menuIcon');
const dropdownMenu = document.getElementById('dropdownMenu');

menuIcon.addEventListener('click', function(e) {
    e.stopPropagation();
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
});

document.addEventListener('click', function(e) {
    if (dropdownMenu.style.display === 'block' && !dropdownMenu.contains(e.target) && e.target !== menuIcon) {
        dropdownMenu.style.display = 'none';
    }
});

// Fade-in on scroll for sections
function fadeInOnScroll() {
    const fadeEls = document.querySelectorAll('.fade-in-up');
    fadeEls.forEach(el => {
        const rect = el.getBoundingClientRect();
        if(rect.top < window.innerHeight - 60) {
            el.classList.add('visible');
        }
    });
}

window.addEventListener('scroll', fadeInOnScroll);
window.addEventListener('DOMContentLoaded', fadeInOnScroll);

// Learn More button functionality
document.getElementById('learnMoreBtn').onclick = function() {
    document.getElementById('moreHeroText').style.display = 'inline';
    this.style.display = 'none';
};

// Modal functionality
document.getElementById('exhibitorBtn').onclick = function() {
    document.getElementById('exhibitorModal').style.display = 'flex';
};

document.getElementById('visitorBtn').onclick = function() {
    document.getElementById('visitorModal').style.display = 'flex';
};

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal on outside click
window.onclick = function(event) {
    const exhibitorModal = document.getElementById('exhibitorModal');
    const visitorModal = document.getElementById('visitorModal');
    if(event.target === exhibitorModal) exhibitorModal.style.display = 'none';
    if(event.target === visitorModal) visitorModal.style.display = 'none';
};

// Form submission functionality
document.getElementById('exhibitorForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        company_name: document.getElementById('companyName').value,
        contact_person: document.getElementById('contactPerson').value,
        email: document.getElementById('exhibitorEmail').value,
        phone: document.getElementById('exhibitorPhone').value
    };
    
    fetch('/register_exhibitor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            document.getElementById('exhibitorForm').reset();
            closeModal('exhibitorModal');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الإرسال', 'error');
    });
});

document.getElementById('visitorForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        full_name: document.getElementById('fullName').value,
        email: document.getElementById('visitorEmail').value,
        phone: document.getElementById('visitorPhone').value
    };
    
    fetch('/register_visitor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            document.getElementById('visitorForm').reset();
            closeModal('visitorModal');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الإرسال', 'error');
    });
});

// إضافة تحسينات لتجربة المستخدم
document.addEventListener('DOMContentLoaded', function() {
    // إضافة تأثيرات التحميل
    document.body.classList.add('loaded');
    
    // تحسين النماذج
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
});

// دالة للتحقق من صحة البريد الإلكتروني
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// دالة للتحقق من صحة رقم الهاتف
function validatePhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/\s+/g, ''));
}

// تحسين عرض الرسائل
function showBetterNotification(message, type, duration = 5000) {
    // إزالة الإشعارات السابقة
    const existingNotifications = document.querySelectorAll('.better-notification');
    existingNotifications.forEach(notif => notif.remove());
    
    // إنشاء الإشعار الجديد
    const notification = document.createElement('div');
    notification.className = `better-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
            <button class="close-notification" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // إضافة الأنماط
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transform: translateX(400px);
        transition: all 0.3s ease;
        max-width: 350px;
        direction: rtl;
    `;
    
    document.body.appendChild(notification);
    
    // عرض الإشعار
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // إخفاء الإشعار
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification && notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

// Notification system
function showNotification(message, type) {
    showBetterNotification(message, type);
}
