// Generate random CAPTCHA code
function generateCaptcha() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let captcha = '';
    for (let i = 0; i < 5; i++) {
        captcha += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return captcha;
}

// Initialize CAPTCHA on page load
let currentCaptcha = generateCaptcha();
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('captchaCode').textContent = currentCaptcha;
});

// Form validation and submission
const contactForm = document.getElementById('contactForm');

contactForm.addEventListener('submit', function(e) {
    e.preventDefault();

    // Validate all required fields
    const formData = new FormData(contactForm);
    let isValid = true;
    let errorMessage = '';

    // Check if all required fields are filled
    const requiredFields = ['offense', 'measurement', 'rating', 'date', 'month', 'day', 'location', 'previous', 'phone', 'email'];

    requiredFields.forEach(field => {
        const value = formData.get(field);
        if (!value || value === '') {
            isValid = false;
            errorMessage += `Kérjük, töltse ki a következő mezőt: ${getFieldLabel(field)}\n`;
        }
    });

    // Check consent checkbox
    if (!document.getElementById('consent').checked) {
        isValid = false;
        errorMessage += 'Kérjük, fogadja el az adatkezelési tájékoztatót!\n';
    }

    // Validate CAPTCHA
    const userCaptcha = formData.get('captcha');
    if (userCaptcha !== currentCaptcha) {
        isValid = false;
        errorMessage += 'Helytelen ellenőrző kód!\n';
    }

    // Validate email format
    const email = formData.get('email');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
        isValid = false;
        errorMessage += 'Helytelen email formátum!\n';
    }

    // Validate phone format
    const phone = formData.get('phone');
    if (phone && !phone.startsWith('06-')) {
        isValid = false;
        errorMessage += 'A telefonszámnak 06- előtaggal kell kezdődnie!\n';
    }

    if (!isValid) {
        alert(errorMessage);
        return false;
    }

    // If validation passes, show success message
    showSuccessMessage();

    // Reset form and generate new CAPTCHA
    contactForm.reset();
    currentCaptcha = generateCaptcha();
    document.getElementById('captchaCode').textContent = currentCaptcha;

    return false;
});

// Helper function to get field labels
function getFieldLabel(fieldName) {
    const labels = {
        'offense': 'Az elkövetés',
        'measurement': 'A mérés',
        'rating': 'Szonda érték',
        'date': 'Időpont',
        'month': 'Hónap',
        'day': 'Nap',
        'location': 'Hol történt',
        'previous': 'Volt már ittas vezetése',
        'phone': 'Mobiltelefon',
        'email': 'Email'
    };
    return labels[fieldName] || fieldName;
}

// Show success message
function showSuccessMessage() {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #4caf50;
        color: white;
        padding: 30px 50px;
        border-radius: 10px;
        font-size: 1.2em;
        text-align: center;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;
    successDiv.innerHTML = `
        <h3 style="margin-bottom: 10px;">Köszönjük!</h3>
        <p>Üzenetét sikeresen elküldtük.</p>
        <p>Hamarosan felvesszük Önnel a kapcsolatot!</p>
    `;

    document.body.appendChild(successDiv);

    // Remove success message after 3 seconds
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Phone number formatting
const phoneInput = document.getElementById('phone');
phoneInput.addEventListener('input', function(e) {
    let value = e.target.value;

    // Ensure it starts with 06-
    if (!value.startsWith('06-')) {
        if (value.startsWith('06')) {
            value = '06-' + value.substring(2);
        } else if (!value.startsWith('0')) {
            value = '06-' + value;
        } else {
            value = '06-' + value.substring(1);
        }
    }

    e.target.value = value;
});

// Dynamic day validation based on month
const monthSelect = document.getElementById('month');
const dayInput = document.getElementById('day');

monthSelect.addEventListener('change', function() {
    const month = this.value;
    const thirtyDayMonths = ['april', 'june', 'september', 'november'];

    if (month === 'february') {
        dayInput.max = 29;
        if (parseInt(dayInput.value) > 29) {
            dayInput.value = 29;
        }
    } else if (thirtyDayMonths.includes(month)) {
        dayInput.max = 30;
        if (parseInt(dayInput.value) > 30) {
            dayInput.value = 30;
        }
    } else {
        dayInput.max = 31;
    }
});

// Add loading animation on form submit
contactForm.addEventListener('submit', function() {
    const submitBtn = contactForm.querySelector('.submit-btn');
    const originalText = submitBtn.textContent;

    submitBtn.disabled = true;
    submitBtn.textContent = 'KÜLDÉS...';

    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }, 2000);
});

// Refresh CAPTCHA button (optional feature)
const captchaBox = document.querySelector('.captcha-box');
const refreshBtn = document.createElement('button');
refreshBtn.type = 'button';
refreshBtn.textContent = '↻';
refreshBtn.style.cssText = `
    margin-left: 10px;
    padding: 5px 15px;
    background: #c00;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1.2em;
`;
refreshBtn.title = 'Új kód generálása';

refreshBtn.addEventListener('click', function() {
    currentCaptcha = generateCaptcha();
    document.getElementById('captchaCode').textContent = currentCaptcha;
    document.getElementById('captcha').value = '';
});

captchaBox.appendChild(refreshBtn);

// Console warning
console.log('%cFigyelem!', 'color: red; font-size: 30px; font-weight: bold;');
console.log('%cEz egy böngésző funkció, amelyet fejlesztők számára terveztek. Ha valaki azt mondta, hogy másoljon/illesszen be valamit ide, hogy "aktiváljon" egy funkciót, az egy átverés, és hozzáférést adhat a fiókjához.', 'font-size: 14px;');
