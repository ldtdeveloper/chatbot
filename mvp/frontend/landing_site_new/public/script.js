// Tailwind CSS Configuration (only when using Tailwind CDN - skipped in Next.js)
if (typeof tailwind !== 'undefined') {
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
    };
}

// API Base URL
const API_BASE = 'https://api.voicequik.com';
const APP_BASE_URL = 'https://app.voicequik.com'
// Selected plan tracking - stores the full plan object
let selectedPlan = null;
// Store all plans globally for lookup
let allPlans = [];

// Plan selection - accepts full plan object
function selectPlan(planObject) {
    console.log("Selected plan:", planObject);
    selectedPlan = planObject;
    openRegisterModal();
}

// Plan selection by ID - looks up plan from allPlans
function selectPlanById(planId) {
    const plan = allPlans.find(p => p.id === planId);
    if (plan) {
        selectPlan(plan);
    } else {
        console.error('Plan not found with ID:', planId);
    }
}

// Fetch plans from API
async function fetchPlans() {
    try {
        const response = await fetch(`${API_BASE}/api/plans/public`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch plans');
        }
        const plans = await response.json();
        const activePlans = plans.filter(plan => plan.is_active);
        // Store plans globally for lookup
        allPlans = plans;
        renderPlans(activePlans);
    } catch (error) {
        console.error('Error fetching plans:', error);
        const plansContainer = document.getElementById('plans');
        const loadingElement = document.getElementById('plansLoading');
        if (loadingElement) {
            loadingElement.innerHTML = `
                <p class="text-red-600">Failed to load plans. Please refresh the page.</p>
            `;
        } else {
            plansContainer.innerHTML = `
                <div class="w-full text-center py-12">
                    <p class="text-red-600">Failed to load plans. Please refresh the page.</p>
                </div>
            `;
        }
    }
}

// Render plans dynamically
function renderPlans(plans) {
    const plansContainer = document.getElementById('plans');
    const loadingElement = document.getElementById('plansLoading');
    
    // Remove loading element
    if (loadingElement) {
        loadingElement.remove();
    }

    // Clear container
    plansContainer.innerHTML = '';

    // Filter active plans
    const activePlans = plans && plans.length > 0 ? plans.filter(plan => plan.is_active) : [];
    
    // Count total cards (API plans + 1 static Custom Plan)
    const totalCards = activePlans.length + 1;

    // Set container classes based on total card count
    if (totalCards <= 4) {
        // All cards inline - use grid with exact column count
        let gridClasses = 'grid gap-6 md:gap-8 max-w-7xl mx-auto px-4';
        
        // Set responsive grid columns
        if (totalCards === 1) {
            gridClasses += ' grid-cols-1';
        } else if (totalCards === 2) {
            gridClasses += ' grid-cols-1 sm:grid-cols-2';
        } else if (totalCards === 3) {
            gridClasses += ' grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
        } else if (totalCards === 4) {
            gridClasses += ' grid-cols-1 sm:grid-cols-2 lg:grid-cols-4';
        }
        
        plansContainer.className = gridClasses;
    } else {
        // More than 4 cards - allow wrapping with flexbox
        plansContainer.className = 'flex flex-wrap justify-center items-start gap-6 md:gap-8 max-w-7xl mx-auto px-4';
    }

    // Render each plan from API
    activePlans.forEach((plan, index) => {
        const isPopular = index === 1; // Mark first plan as popular
        const isCustomPrice = !plan.price || plan.price === 0;
        const isTrial = plan.is_trial
        const planCard = document.createElement('div');
        planCard.className = `
            ${isTrial 
                ? 'rounded-2xl border border-gray-200 bg-white/70 p-5 md:p-6 flex flex-col' 
                : 'glass-card rounded-2xl p-6 md:p-8 card-hover flex flex-col'}
            ${isPopular && !isTrial ? ' border-2 border-purple-300 relative popular-glow' : ''}
        `.trim();
        
        // Set width based on layout
        if (totalCards <= 4) {
            // Grid layout - cards fill grid cells
            planCard.style.width = '100%';
            planCard.style.maxWidth = '100%';
        } else {
            // Flex layout - cards have fixed max width
            planCard.style.width = '100%';
            planCard.style.maxWidth = '320px';
            planCard.style.flexShrink = '0';
        }
        
        planCard.innerHTML = `
            ${isPopular ? `
                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span class="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-semibold px-4 py-1.5 rounded-full shadow-lg">
                        Most Popular
                    </span>
                </div>
            ` : ''}
            
            <div class="text-center mb-6 ${isPopular ? 'mt-2' : ''}">
                <h3 class="text-2xl font-bold mb-2 text-gray-800">${plan.name}</h3>
                <p class="text-gray-500 mb-4">${plan.description || 'Choose this plan'}</p>
                <div class="${isTrial ? 'text-base font-semibold text-gray-800 mb-1' : 'text-5xl font-extrabold gradient-text'}">
                    ${isTrial ? 'Free Trial' : `$${plan.price}`}
                    ${!isCustomPrice && !isTrial ? '<span class="text-lg font-normal text-gray-400">/month</span>' : ''}
                </div>
                ${plan.wallet_credits ? `
                    <div class="mt-2 inline-flex items-center px-3 py-1 rounded-full bg-purple-50 text-xs font-medium text-purple-700">
                        ${isTrial ? `Free $${plan.wallet_credits} Credits/14 days` : `Free $${plan.wallet_credits} Credits`}
                    </div>
                ` : ''}
            </div>

            <ul class="space-y-4 mb-8 flex-grow">
                ${plan.features && plan.features.length > 0 ? plan.features.map(feature => `
                    <li class="flex items-center space-x-3">
                        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        <span class="text-gray-600">${feature}</span>
                    </li>
                `).join('') : '<li class="text-gray-500">No features listed</li>'}
            </ul>
            ${plan.is_trial ? 
            `<div class="mt-auto">
            <button onclick="selectPlanById(${plan.id})" class="w-full btn-gradient py-3.5 rounded-full text-white font-semibold" data-plan-id="${plan.id}">
                Start 14 day free trial
            </button>
            </div> `: 
            `<div class="mt-auto">
            <button onclick="selectPlanById(${plan.id})" class="w-full btn-gradient py-3.5 rounded-full text-white font-semibold" data-plan-id="${plan.id}">
                Get Started 
            </button>
            </div>`

            }
        `;
        
        plansContainer.appendChild(planCard);
    });

    // Add static Custom Plan card
    const customPlanCard = document.createElement('div');
    customPlanCard.className = 'glass-card rounded-2xl p-6 md:p-8 card-hover flex flex-col';
    
    // Set width based on layout
    if (totalCards <= 4) {
        // Grid layout - cards fill grid cells
        customPlanCard.style.width = '100%';
        customPlanCard.style.maxWidth = '100%';
    } else {
        // Flex layout - cards have fixed max width
        customPlanCard.style.width = '100%';
        customPlanCard.style.maxWidth = '320px';
        customPlanCard.style.flexShrink = '0';
    }
    
    customPlanCard.innerHTML = `
        <div class="text-center mb-8">
            <h3 class="text-2xl font-bold mb-2 text-gray-800">Custom Plan</h3>
            <p class="text-gray-500 mb-4">Customize plan according to business needs</p>
            <div class="text-5xl font-extrabold gradient-text">
                Custom
            </div>
        </div>

        <ul class="space-y-4 mb-8 flex-grow">
            <li class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-gray-600">Unlimited agents</span>
            </li>
            <li class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-gray-600">Custom integrations</span>
            </li>
            <li class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-gray-600">Dedicated support</span>
            </li>
            <li class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="text-gray-600">SLA guarantee</span>
            </li>
        </ul>

        <div class="mt-auto">
            <button class="w-full py-3.5 rounded-full border-2 border-purple-200 text-purple-600 font-semibold hover:bg-purple-50 transition-colors">
                Contact Sales
            </button>
        </div>
    `;
    
    plansContainer.appendChild(customPlanCard);
}

// Registration modal functions
function openRegisterModal() {
    document.getElementById('registerModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Update plan info display
    if (selectedPlan && selectedPlan.id) {
        const selectedPlanInfo = document.getElementById('selectedPlanInfo');
        if (selectedPlan.is_trial) {
            // For trial plans, show a simple "Free 14-Day Trial" label instead of price/month
            selectedPlanInfo.innerHTML = `
                <span class="text-sm font-medium text-purple-700">
                    Selected Plan: ${selectedPlan.name || 'Plan'} - Free 14 Days Trial
                </span>
            `;
        } else {
            document.getElementById('planName').textContent = selectedPlan.name || 'Plan';
            document.getElementById('planPrice').textContent = selectedPlan.price || 0;
        }
        selectedPlanInfo.classList.remove('hidden');
    } else {
        document.getElementById('selectedPlanInfo').classList.add('hidden');
    }
}

// Scroll down for get started
function scrollDownPlans(duration = 1000) {
    console.log("Scroll down plans logged.........")
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
    // If no plan selected, select the first available plan
    if (!selectedPlan && allPlans.length > 0) {
        const firstActivePlan = allPlans.find(p => p.is_active);
        if (firstActivePlan) {
            selectedPlan = firstActivePlan;
        }
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
    if (!selectedPlan || !selectedPlan.id) {
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
                plan_id: selectedPlan.id
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
                text: `Registration successful! Please check your email`,
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
                plan_id: selectedPlan.id,
                amount: selectedPlan.price, // Amount in USD
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
            description: `${selectedPlan.name || 'Plan'} Subscription`,
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
            localStorage.setItem('subscription_plan', selectedPlan.code || selectedPlan.name);
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
            body: JSON.stringify({ email, plan_id: selectedPlan ? selectedPlan.id : null })
        });
        const data = await res.json();
        console.log(`${data} --------------`)
        if (!res.ok) {
            throw new Error(data.detail || 'Prefetch failed');
        }
        if (data.next_action=='LOGIN') {
            passwordContainer.classList.remove('hidden');
            document.getElementById('forgotPasswordContainer').classList.remove('hidden');
            loadingOverlay.classList.add('hidden');
            loginBtn.disabled = false;
            passwordInput.focus();
            return;
        }
        else if (data.next_action=='COMPLETE_PAYMENT') {
            Toastify({
                text: 'Payment link sent to your registered email',
                duration: 2000,
                gravity: 'top',
                position: 'right',
                style: { borderRadius: '15px',background: '#16a34a' }
            }).showToast();
            loadingOverlay.classList.add('hidden');
            closeLoginModal();
            return;
        }
        else if(data.next_action=='CHOOSE_PLAN'){
            loadingOverlay.classList.add('hidden');
            Toastify({
                text: 'Choose a plan',
                duration: 2000,
                gravity: 'top',
                position: 'right',
                style: {borderRadius: '15px',background:' #dc2626' }
            }).showToast();
            closeLoginModal();
            scrollDownPlans();
        }
        else if (data.next_action === 'SET_PASSWORD') {
            loadingOverlay.classList.add('hidden');
            Toastify({
                text: 'Setup Password link sent to your registered email',
                duration: 2000,
                gravity: 'top',
                position: 'right',
                style: {borderRadius: '15px', background:' #16a34a'}
            }).showToast();
                closeLoginModal();
                return;
            }
        }
     catch (err) {
        console.error(err);
        showError(`${err.message}`);
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

// Load plans when page loads (support both initial load and late script load)
function loadPlans() {
    if (document.getElementById('plans')) fetchPlans();
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadPlans);
} else {
    loadPlans();
}

