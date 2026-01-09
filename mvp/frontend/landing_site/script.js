// Tailwind CSS Configuration
tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                'outfit': ['Outfit', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#fdf4ff',
                    100: '#fae8ff',
                    200: '#f5d0fe',
                    300: '#f0abfc',
                    400: '#e879f9',
                    500: '#d946ef',
                    600: '#c026d3',
                    700: '#a21caf',
                    800: '#86198f',
                    900: '#701a75',
                }
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'float-slow': 'float 8s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'gradient': 'gradient 8s ease infinite',
                'slide-up': 'slideUp 0.6s ease-out forwards',
                'slide-down': 'slideDown 0.3s ease-out',
                'fade-in': 'fadeIn 0.6s ease-out forwards',
                'scale-in': 'scaleIn 0.3s ease-out',
                'bounce-soft': 'bounceSoft 2s ease-in-out infinite',
                'spin-slow': 'spin 20s linear infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-20px)' },
                },
                gradient: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(30px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                slideDown: {
                    '0%': { transform: 'translateY(-10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                scaleIn: {
                    '0%': { transform: 'scale(0.95)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
                bounceSoft: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
            }
        }
    }
}

// API Base URL
const API_BASE = 'http://localhost:8081';
const APP_BASE_URL = 'http://localhost:3000'
// Selected plan tracking
let selectedPlan = null;
let selectedPlanPrice = null;

// Plan selection
function selectPlan(plan, price) {
    console.log("Selected plan price ----> " + plan + "" + price)
    selectedPlan = plan;
    selectedPlanPrice = price;
    openRegisterModal();
}

// Registration modal functions
function openRegisterModal() {
    document.getElementById('registerModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Update plan info display
    if (selectedPlan && selectedPlanPrice) {
        const planNames = {
            'starter': 'Starter',
            'pro': 'Pro',
            'enterprise': 'Enterprise'
        };
        document.getElementById('planName').textContent = planNames[selectedPlan] || selectedPlan;
        document.getElementById('planPrice').textContent = selectedPlanPrice;
        document.getElementById('selectedPlanInfo').classList.remove('hidden');
    } else {
        document.getElementById('selectedPlanInfo').classList.add('hidden');
    }
}

// Scroll down for get started
function scrollDownPlans(duration = 1000) {
    const target = document.getElementById("pricing");
    if (!target) return;

    const start = window.pageYOffset;
    const end = target.getBoundingClientRect().top + start;
    const startTime = performance.now();

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // easeInOut
        const ease = progress < 0.5
            ? 2 * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 2) / 2;

        window.scrollTo(0, start + (end - start) * ease);

        if (progress < 1) requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}


function closeRegisterModal() {
    document.getElementById('registerModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
    document.getElementById('registerError').classList.add('hidden');
    // Reset form
    document.getElementById('registerForm').reset();
}


function switchToLogin() {
    closeRegisterModal();
    openLoginModal();
}

function switchToRegister() {
    closeLoginModal();
    if (!selectedPlan) {
        selectedPlan = 'starter';
        selectedPlanPrice = 100;
    }
    openRegisterModal();
}

// Handle registration
async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const errorDiv = document.getElementById('registerError');
    const registerBtn = document.getElementById('registerBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Validate plan selection
    if (!selectedPlan || !selectedPlanPrice) {
        errorDiv.textContent = 'Please select a plan first';
        errorDiv.classList.remove('hidden');
        return;
    }

    // Show loading
    loadingOverlay.querySelector('p').textContent = 'Creating account...';
    loadingOverlay.classList.remove('hidden');
    registerBtn.disabled = true;
    errorDiv.classList.add('hidden');

    try {
        // Register user (email + username only, no password)
        const registerResponse = await fetch(`${API_BASE}/api/auth/register-with-plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                plan: selectedPlan
            })
        });

        if (!registerResponse.ok) {
            const error = await registerResponse.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const result = await registerResponse.json();

        // Show success message
        loadingOverlay.querySelector('p').textContent = 'Registration successful!';

        // Close modal and show success message
        setTimeout(() => {
            closeRegisterModal();
            loadingOverlay.classList.add('hidden');

            // Show success message
            // alert(`Registration successful! Please check your email (${email}) for the payment link. Click the link in the email to complete payment and set up your password.`);
            Toastify({
                text: `Registration successful! Check your email for the payment link.`,
                duration: 2000,
                gravity: "top",
                position: "right",
                backgroundColor: "#16a34a",
                style: {
                    borderRadius: "15px"
                }
            }).showToast();

        }, 1500);

    } catch (error) {
        console.error('Registration error:', error);
        errorDiv.textContent = error.message || 'Registration failed. Please try again.';
        errorDiv.classList.remove('hidden');
        loadingOverlay.classList.add('hidden');
        registerBtn.disabled = false;
    }
}

// Initiate Razorpay payment
async function initiatePayment(token, userId) {
    try {
        // Create payment order on backend
        const orderResponse = await fetch(`${API_BASE}/api/payments/create-order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                plan: selectedPlan,
                amount: selectedPlanPrice, // Amount in USD
                user_id: userId
            })
        });

        if (!orderResponse.ok) {
            // Get error message from backend
            const errorData = await orderResponse.json().catch(() => ({ detail: 'Failed to create payment order' }));
            throw new Error(errorData.detail || 'Failed to create payment order');
        }

        const orderData = await orderResponse.json();

        // Check if test mode (mock key)
        if (orderData.razorpay_key_id === 'rzp_test_MOCK_KEY') {
            // Test mode - auto-approve payment
            console.log('[Payment] TEST MODE - Auto-approving payment');
            await verifyPayment(token, {
                razorpay_order_id: orderData.razorpay_order_id,
                razorpay_payment_id: 'pay_test_' + orderData.order_id,
                razorpay_signature: 'test_signature'
            }, orderData.order_id);
            return;
        }

        // Initialize Razorpay (production mode)
        const options = {
            key: orderData.razorpay_key_id,
            amount: orderData.amount,
            currency: orderData.currency,
            name: 'VoiceAI Platform',
            description: `${selectedPlan.charAt(0).toUpperCase() + selectedPlan.slice(1)} Plan Subscription`,
            order_id: orderData.razorpay_order_id,
            handler: async function (response) {
                // Verify payment on backend
                await verifyPayment(token, response, orderData.order_id);
            },
            prefill: {
                email: document.getElementById('registerEmail').value,
                name: document.getElementById('registerUsername').value
            },
            theme: {
                color: '#667eea'
            },
            modal: {
                ondismiss: function () {
                    // Payment cancelled - show error and prevent dashboard access
                    document.getElementById('loadingOverlay').classList.add('hidden');
                    document.getElementById('registerError').textContent = 'Payment is required to access the platform. Please complete the payment to continue.';
                    document.getElementById('registerError').classList.remove('hidden');
                    // Remove token so user cannot access dashboard without payment
                    localStorage.removeItem('token');
                }
            }
        };

        const razorpay = new Razorpay(options);
        razorpay.open();

    } catch (error) {
        console.error('Payment initiation error:', error);
        // Show the actual error message from backend
        const errorMessage = error.message || 'Payment initialization failed. Please try again.';
        document.getElementById('registerError').textContent = errorMessage;
        document.getElementById('registerError').classList.remove('hidden');
        document.getElementById('loadingOverlay').classList.add('hidden');
        // Remove token if payment setup fails
        localStorage.removeItem('token');
    }
}

// Verify payment
async function verifyPayment(token, razorpayResponse, orderId) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.querySelector('p').textContent = 'Verifying payment...';

    try {
        const verifyResponse = await fetch(`${API_BASE}/api/payments/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                razorpay_order_id: razorpayResponse.razorpay_order_id,
                razorpay_payment_id: razorpayResponse.razorpay_payment_id,
                razorpay_signature: razorpayResponse.razorpay_signature,
                order_id: orderId
            })
        });

        if (!verifyResponse.ok) {
            throw new Error('Payment verification failed');
        }

        const verifyData = await verifyResponse.json();

        if (verifyData.success) {
            // Payment successful - store subscription status
            localStorage.setItem('subscription_active', 'true');
            localStorage.setItem('subscription_plan', selectedPlan);
            loadingOverlay.querySelector('p').textContent = 'Payment successful! Redirecting to dashboard...';
            const setupResponse = await fetch(`${API_BASE}/openai-keys`, {

                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    razorpay_payment_id: verifyData.razorpay_payment_id
                })
            });


            const setupData = await setupResponse.json();


            if (setupData.success) {
                localStorage.setItem('subscription_active', 'true');
                loadingOverlay.querySelector('p').textContent = 'Account setup complete! Redirecting...';

                setTimeout(() => {
                    window.location.href = window.location.origin + '/dashboard';
                }, 1500);
            } else {
                throw new Error(setupData.message || 'Account setup failed');
            }
        } else {
            // Payment verification failed - remove token
            localStorage.removeItem('token');
            throw new Error(verifyData.message || 'Payment verification failed');
        }

    } catch (error) {
        console.error('Payment verification error:', error);
        // Remove token on payment failure
        localStorage.removeItem('token');
        localStorage.removeItem('subscription_active');
        document.getElementById('registerError').textContent = error.message || 'Payment verification failed. Please contact support or try again.';
        document.getElementById('registerError').classList.remove('hidden');
        loadingOverlay.classList.add('hidden');
    }
}

// Modal functions
function openLoginModal() {
    resetLoginState();
    document.getElementById('loginModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    if(selectedPlan){
        document.getElementById('signupcontainer').classList.remove('hidden');
    }
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
    document.getElementById('loginError').classList.add('hidden');
}

// Toggle password visibility
function togglePassword() {
    const input = document.getElementById('loginPassword');
    const icon = document.getElementById('eyeIcon');

    if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
        `;
    } else {
        input.type = 'password';
        icon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        `;
    }
}

// Handle Forget Password
async function handleForgotPassword(e){
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    if(!email){
        Toastify({
            text: `Please enter your email first`,
            duration: 2000,
            gravity: "top",
            position: "right",
            backgroundColor: "#dc2626",
            style: {
                borderRadius: "15px"
            }
        }).showToast();
        return 
    }
    Toastify({
        text: `If the email exists, a reset link has been sent ! Check your registered email for the link.`,
        duration: 3000,
        gravity: "top",
        position: "right",
        backgroundColor: "#16a34a",
        style: {
            borderRadius: "15px"
        }
    }).showToast();
    try{
        const forgetPasswordResponse = await fetch(`${API_BASE}/api/auth/forget-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email
            })
        });
        if(!forgetPasswordResponse.ok){
            const error = await forgetPasswordResponse.json();
            throw new Error(error.detail || 'User not found');
        }  

    }
    catch (error){
        console.log(error)
    }
}

// Quick login
function quickLogin(username, password) {
    document.getElementById('loginEmail').value = username;
    document.getElementById('loginPassword').value = password;
    handleLogin(new Event('submit'));
}

// Reset Login State 
function resetLoginState() {
    // Inputs
    document.getElementById('loginEmail').value = '';
    document.getElementById('loginPassword').value = '';

    // UI state
    document.getElementById('passwordContainer').classList.add('hidden');
    document.getElementById('forgotPasswordContainer').classList.add('hidden');

    // Errors & loaders
    document.getElementById('loginError').classList.add('hidden');
    document.getElementById('loginBtn').disabled = false;
    document.getElementById('loadingOverlay').classList.add('hidden');
}

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const passwordInput = document.getElementById('loginPassword');
    const passwordContainer = document.getElementById('passwordContainer');
    const errorDiv = document.getElementById('loginError');
    const loginBtn = document.getElementById('loginBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');

    const showError = (msg) => {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
        loadingOverlay.classList.add('hidden');
        loginBtn.disabled = false;
    };

    const startLoading = () => {
        errorDiv.classList.add('hidden');
        loadingOverlay.classList.remove('hidden');
        loginBtn.disabled = true;
    };

    /** LOGIN FLOW **/
    if (!passwordContainer.classList.contains('hidden')) {
        const password = passwordInput.value;

        if (!password) {
            showError('Password is required');
            return;
        }

        startLoading();

        try {
            const res = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            if (!data.access_token) {
                throw new Error('No access token received');
            }

            localStorage.setItem('token', data.access_token);[]
            window.location.href = `${APP_BASE_URL}/?token=${data.access_token}`;
        } catch (err) {
            console.error(err);
            showError(err.message);
            return;
        }
    }

    /** PREFETCH FLOW **/
    startLoading();

    try {
        const res = await fetch(`${API_BASE}/api/auth/prefetch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, plan: selectedPlan })
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || 'Prefetch failed');
        }

        if (data.password_set) {
            passwordContainer.classList.remove('hidden');
            document.getElementById('forgotPasswordContainer').classList.remove('hidden');
            loadingOverlay.classList.add('hidden');
            loginBtn.disabled = false;
            passwordInput.focus();
            return;
        }

        if (!data.subscription.exists ||
            (data.subscription.status === 'PENDING' && !data.subscription.expired)) {

            Toastify({
                text: 'Payment link sent to your registered email',
                duration: 2000,
                gravity: 'top',
                position: 'right',
                backgroundColor: '#16a34a',
                style: { borderRadius: '15px' }
            }).showToast();

            return;
        }

        if (data.subscription.exists && data.next_action === 'SET_PASSWORD') {
            // redirect to setup password
            return;
        }

        Toastify({
            text: 'Subscription expired',
            duration: 2000,
            gravity: 'top',
            position: 'right',
            backgroundColor: '#dc2626',
            style: { borderRadius: '15px' }
        }).showToast();

    } catch (err) {
        console.error(err);
        showError('Connection error. Please try again.');
    }
}


// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeLoginModal();
        closeRegisterModal();
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
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

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.classList.add('animate-slide-up');
        }
    });
}, observerOptions);

// Observe elements with animation classes
document.querySelectorAll('.feature-card, .glass-card').forEach(el => {
    observer.observe(el);
});

// Trigger animations for elements with delay classes
document.querySelectorAll('[class*="delay-"]').forEach(el => {
    setTimeout(() => {
        el.style.opacity = '1';
    }, 100);
});

