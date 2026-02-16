"use client";

import { useEffect, useState } from "react";

const API_BASE = "https://api.voicequik.com";

type Plan = {
  id: number;
  name: string;
  description?: string;
  price?: number;
  is_active: boolean;
  is_trial?: boolean;
  wallet_credits?: number;
  features?: string[];
  code?: string;
  minutes?: number;
};

export function PricingPlans() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [activePlanId, setActivePlanId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showLoadingOverlay, setShowLoadingOverlay] = useState(false);
  const [showSalesModal, setShowSalesModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);

  useEffect(() => {
    async function fetchPlans() {
      try {
        const res = await fetch(`${API_BASE}/api/plans/public`);
        const data = await res.json();

        if (!res.ok) {
          const errorMsg = data.detail || data.message || "Failed to fetch plans";
          setError(errorMsg);
          if (typeof window !== "undefined" && (window as any).Toastify) {
            (window as any).Toastify({
              text: errorMsg,
              duration: 3000,
              gravity: "top",
              position: "right",
              backgroundColor: "#dc2626",
              style: { borderRadius: "15px" }
            }).showToast();
          }
          throw new Error(errorMsg);
        }

        // ✅ Only show first 3 active plans
        const active = data.filter((p: Plan) => p.is_active).slice(0, 3);

        const customPlan: Plan = {
          id: 999,
          name: "Enterprise",
          description: "Where scale meets reliability",
          price: undefined,
          is_active: true,
          is_trial: false,
          features: [
            "Unlimited Usage & Agents",
            "Custom Integrations",
            "Dedicated Support Team",
            "SLA & Compliance Assurance",
            "On-Premise Deployment Option"
          ],
        };

        setPlans([...active, customPlan]);
        
        // Show success toast for plans loaded
        if (typeof window !== "undefined" && (window as any).Toastify) {
          // (window as any).Toastify({
          //   text: `Loaded ${active.length} plan${active.length !== 1 ? 's' : ''} successfully`,
          //   duration: 2000,
          //   gravity: "top",
          //   position: "right",
          //   backgroundColor: "#16a34a",
          //   style: { borderRadius: "15px" }
          // }).showToast();
        }
      } catch (err: any) {
        const errorMsg = err.message || "Failed to fetch plans";
        setError(errorMsg);
        if (typeof window !== "undefined" && (window as any).Toastify) {
          // (window as any).Toastify({
          //   text: errorMsg,
          //   duration: 3000,
          //   gravity: "top",
          //   position: "right",
          //   backgroundColor: "#dc2626",
          //   style: { borderRadius: "15px" }
          // }).showToast();
        }
      } finally {
        setLoading(false);
      }
    }

    fetchPlans();
  }, []);

const handlePlanAction = (plan: Plan) => {
  // Store the selected plan
  setSelectedPlan(plan);

  // Enterprise → Sales modal
  if (plan.name === "Enterprise") {
    setShowSalesModal(true);
    return;
  }

  // Free Trial → Register modal
  if (plan.is_trial) {
    setShowRegisterModal(true);
    return;
  }

  // Paid plan → Open register modal
  const token = localStorage.getItem("token");

  if (!token) {
    setShowRegisterModal(true);
    return;
  }

  console.log("Proceed with checkout...");
};


  const switchToRegister = () => {
    setShowLoginModal(false);
    // Preserve selected plan when switching to register
    if (!selectedPlan && plans.length > 0) {
      const firstActivePlan = plans.find((p) => p.is_active);
      if (firstActivePlan) {
        setSelectedPlan(firstActivePlan);
      }
    }
    setShowRegisterModal(true);
  };

  const switchToLogin = () => {
    setShowRegisterModal(false);
    setShowLoginModal(true);
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const username = (form.elements.namedItem("registerUsername") as HTMLInputElement).value;
    const email = (form.elements.namedItem("registerEmail") as HTMLInputElement).value;

    setShowLoadingOverlay(true);
    const registerError = document.getElementById("registerError") as HTMLElement;

    // Validate plan selection
    if (!selectedPlan || !selectedPlan.id) {
      const errorMsg = "Please select a plan first";
      registerError.textContent = errorMsg;
      registerError.classList.remove("hidden");
      setShowLoadingOverlay(false);
      if (typeof window !== "undefined" && (window as any).Toastify) {
        (window as any).Toastify({
          text: errorMsg,
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#dc2626",
          style: { borderRadius: "15px" }
        }).showToast();
      }
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/auth/register-with-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          username, 
          email,
          plan_id: selectedPlan.id
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        const errorMsg = data.detail || data.message || "Registration failed";
        registerError.textContent = errorMsg;
        registerError.classList.remove("hidden");
        if (typeof window !== "undefined" && (window as any).Toastify) {
          (window as any).Toastify({
            text: errorMsg,
            duration: 3000,
            gravity: "top",
            position: "right",
            backgroundColor: "#dc2626",
            style: { borderRadius: "15px" }
          }).showToast();
        }
        throw new Error(errorMsg);
      }

      // On success, close modal and show success message
      const successMsg = data.message || `Registration successful! Please check your email (${email}) for the payment link.`;
      setShowRegisterModal(false);
      setShowLoadingOverlay(false);
      if (typeof window !== "undefined" && (window as any).Toastify) {
        (window as any).Toastify({
          text: successMsg,
          duration: 4000,
          gravity: "top",
          position: "right",
          backgroundColor: "#16a34a",
          style: { borderRadius: "15px" }
        }).showToast();
      }
    } catch (err: any) {
      const errorMsg = err.message || "Registration failed. Please try again.";
      registerError.textContent = errorMsg;
      registerError.classList.remove("hidden");
      if (typeof window !== "undefined" && (window as any).Toastify) {
        (window as any).Toastify({
          text: errorMsg,
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#dc2626",
          style: { borderRadius: "15px" }
        }).showToast();
      }
    } finally {
      setShowLoadingOverlay(false);
    }
  };

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const identifier = (form.elements.namedItem("loginEmail") as HTMLInputElement).value;
    
    // Get password value only if the field exists and is visible
    const passwordInput = form.elements.namedItem("loginPassword") as HTMLInputElement;
    const password = passwordInput ? passwordInput.value : "";

    // Check if password container is visible
    const passwordContainer = document.getElementById("passwordContainer");
    const isPasswordVisible = passwordContainer && !passwordContainer.classList.contains("hidden");

    setShowLoadingOverlay(true);
    const loginError = document.getElementById("loginError") as HTMLElement;

    try {
      // If password is visible (user has entered prefetch stage), proceed with login
      if (isPasswordVisible) {
        if (!password) {
          throw new Error("Password is required");
        }

        const res = await fetch(`${API_BASE}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            email: identifier,  // Use email as field name
            password: password 
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          const errorMsg = data.detail || data.message || "Invalid credentials";
          loginError.textContent = errorMsg;
          loginError.classList.remove("hidden");
          if (typeof window !== "undefined" && (window as any).Toastify) {
            (window as any).Toastify({
              text: errorMsg,
              duration: 3000,
              gravity: "top",
              position: "right",
              backgroundColor: "#dc2626",
              style: { borderRadius: "15px" }
            }).showToast();
          }
          throw new Error(errorMsg);
        }

        localStorage.setItem("token", data.access_token || data.token);
        const successMsg = data.message || "Login successful!";
        setShowLoginModal(false);
        if (typeof window !== "undefined" && (window as any).Toastify) {
          (window as any).Toastify({
            text: successMsg,
            duration: 2000,
            gravity: "top",
            position: "right",
            backgroundColor: "#16a34a",
            style: { borderRadius: "15px" }
          }).showToast();
        }
        
        // Redirect to dashboard or reload
        if (data.access_token) {
          window.location.href = `${window.location.origin}/dashboard?token=${data.access_token}`;
        } else {
          window.location.reload();
        }
      } else {
        // First step - check if user exists (prefetch)
        const res = await fetch(`${API_BASE}/api/auth/prefetch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            email: identifier,
            plan_id: selectedPlan ? selectedPlan.id : null 
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || data.message || "User not found");
        }

        // Handle different next actions
        if (data.next_action === 'LOGIN') {
          // Show password field
          passwordContainer?.classList.remove('hidden');
          document.getElementById('forgotPasswordContainer')?.classList.remove('hidden');
          // Clear any existing password value
          if (passwordInput) {
            passwordInput.value = '';
          }
          setShowLoadingOverlay(false);
          // loginBtn.disabled = false;
          passwordInput?.focus();
          return;
        } 
        else if (data.next_action === 'COMPLETE_PAYMENT') {
          if (typeof window !== "undefined" && (window as any).Toastify) {
            (window as any).Toastify({
              text: 'Payment link sent to your registered email',
              duration: 2000,
              gravity: 'top',
              position: 'right',
              style: { borderRadius: '15px', background: '#16a34a' }
            }).showToast();
          }
          setShowLoadingOverlay(false);
          setShowLoginModal(false);
          return;
        }
        else if (data.next_action === 'CHOOSE_PLAN') {
          setShowLoadingOverlay(false);
          if (typeof window !== "undefined" && (window as any).Toastify) {
            (window as any).Toastify({
              text: 'Please choose a plan first',
              duration: 2000,
              gravity: 'top',
              position: 'right',
              style: { borderRadius: '15px', background: '#dc2626' }
            }).showToast();
          }
          setShowLoginModal(false);
          // Scroll to plans section
          const pricingSection = document.getElementById('pricing');
          if (pricingSection) {
            pricingSection.scrollIntoView({ behavior: 'smooth' });
          }
          return;
        }
        else if (data.next_action === 'SET_PASSWORD') {
          setShowLoadingOverlay(false);
          if (typeof window !== "undefined" && (window as any).Toastify) {
            (window as any).Toastify({
              text: 'Password setup link sent to your registered email',
              duration: 2000,
              gravity: 'top',
              position: 'right',
              style: { borderRadius: '15px', background: '#16a34a' }
            }).showToast();
          }
          setShowLoginModal(false);
          return;
        }
      }
    } catch (err: any) {
      const errorMsg = err.message || "Login failed. Please try again.";
      loginError.textContent = errorMsg;
      loginError.classList.remove("hidden");
      if (typeof window !== "undefined" && (window as any).Toastify) {
        (window as any).Toastify({
          text: errorMsg,
          duration: 3000,
          gravity: "top",
          position: "right",
          backgroundColor: "#dc2626",
          style: { borderRadius: "15px" }
        }).showToast();
      }
    } finally {
      setShowLoadingOverlay(false);
    }
  };

  const togglePassword = () => {
    const passwordInput = document.getElementById("loginPassword") as HTMLInputElement;
    const eyeIcon = document.getElementById("eyeIcon") as HTMLElement;
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      eyeIcon.innerHTML = '<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0111.25 19c-2.798 0-5.001-1.201-6.649-3.218M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7m-1.501 1.208A10.05 10.05 0 0012.75 5c-2.798 0-5.001 1.201-6.649 3.218M21 21l-4.35-4.35" />';
    } else {
      passwordInput.type = "password";
      eyeIcon.innerHTML = '<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />';
    }
  };

  const handleForgotPassword = (e: React.MouseEvent) => {
    e.preventDefault();
    // Implement forgot password logic here
    console.log("Forgot password clicked");
  };

  if (loading) return null;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 w-full max-w-7xl mx-auto px-4">
        {plans.map((plan, index) => {
          const isActive = activePlanId === plan.id;
          const isPopular = index === 1;
          const isTrial = !!plan.is_trial;
          const isCustom = plan.name === "Enterprise";

          return (
            <div
              key={plan.id}
              onClick={() => setActivePlanId(plan.id)}
              className={`pricing-card rounded-2xl p-[1px] transition duration-300 cursor-pointer
                ${isActive ? "bg-gradient-to-br from-cyan-400 to-purple-500 shadow-[0_0_40px_rgba(168,85,247,0.5)]" : "bg-white/5"}
              `}
            >
              <div className="bg-[#151527] rounded-2xl p-8 h-full flex flex-col">

                {isPopular && (
                  <div className="mb-4 text-center">
                    <span className="bg-gradient-to-r from-indigo-400 to-pink-500 text-white text-xs px-4 py-1 rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}

                <h3 className="text-2xl font-bold text-white mb-2 capitalize">
                  {plan.name}
                </h3>

                <p className="text-gray-400 text-sm mb-4">
                  {plan.description}
                </p>

                <div className="mb-6">
                  {isTrial ? (
                    <>
                      <span className="text-4xl font-extrabold text-pink-400">$0.00</span>
                      <span className="text-gray-400 text-sm"> /14 Days</span>
                      {plan.minutes && (
                        <span className="text-gray-400 text-sm ml-2">
                          / {plan.minutes} minutes
                        </span>
                      )}
                    </>
                  ) : plan.price ? (
                    <>
                      <span className="text-4xl font-extrabold text-pink-400">
                        ${plan.price}
                      </span>
                      {plan.minutes && (
                        <span className="text-gray-400 text-sm ml-2">
                          / {plan.minutes} minutes
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="text-4xl font-extrabold text-pink-400">
                      Custom
                    </span>
                  )}
                </div>

                <ul className="space-y-3 text-gray-300 text-sm flex-grow">
                  {plan.features?.map((feature, i) => (
                    <li key={i}>✔ {feature}</li>
                  ))}
                </ul>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePlanAction(plan);
                  }}
                  className="mt-8 w-full py-3 rounded-full bg-white/10 hover:bg-white/20 transition font-semibold text-white"
                >
                  {isTrial ? "Start Free Trial" : isCustom ? "Contact Sales" : "Get Started"}
                </button>

              </div>
            </div>
          );
        })}
      </div>

      {/* Register Modal (Exact design from homepage) */}
      {showRegisterModal && (
        <div className="fixed inset-0 z-50">
          <div className="modal-backdrop absolute inset-0" onClick={() => setShowRegisterModal(false)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setShowRegisterModal(false)} />
          <div className="flex items-center justify-center min-h-screen p-4">
            <div className="bg-white rounded-3xl p-6 md:p-8 w-full max-w-md relative z-10 shadow-2xl animate-scale-in max-h-[90vh] overflow-y-auto">
              <button type="button" onClick={() => setShowRegisterModal(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
              <div className="text-center mb-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-800">Create Account</h3>
                <p className="text-gray-500 mt-2">Sign up to get started</p>
                {selectedPlan && (
                  <div className="mt-3 px-4 py-2 bg-purple-50 rounded-lg border border-purple-200">
                    <span className="text-sm font-medium text-purple-700">
                      Selected Plan: {selectedPlan.name}
                      {selectedPlan.is_trial ? (
                        " - Free 14 Days Trial"
                      ) : selectedPlan.price ? (
                        ` - $${selectedPlan.price}/month`
                      ) : (
                        ""
                      )}
                    </span>
                  </div>
                )}
              </div>
              <form onSubmit={handleRegister} className="space-y-5">
                <div>
                  <label htmlFor="registerUsername" className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                  <input type="text" id="registerUsername" required className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all" placeholder="Choose a username" />
                </div>
                <div>
                  <label htmlFor="registerEmail" className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input type="email" id="registerEmail" required className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all" placeholder="Enter your email" />
                </div>
                <div id="registerError" className="hidden bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm" />
                <button type="submit" id="registerBtn" className="w-full btn-gradient py-3.5 rounded-xl text-white font-semibold flex items-center justify-center space-x-2">
                  <span>Create Account</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                </button>
              </form>
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  Already have an account?{" "}
                  <button type="button" onClick={switchToLogin} className="text-purple-600 hover:text-purple-700 font-medium">Sign in</button>
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Login Modal (Exact design from homepage) */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50">
          <div className="modal-backdrop absolute inset-0" onClick={() => setShowLoginModal(false)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setShowLoginModal(false)} />
          <div className="flex items-center justify-center min-h-screen p-4">
            <div className="bg-white rounded-3xl p-6 md:p-8 w-full max-w-md relative z-10 shadow-2xl animate-scale-in">
              <button type="button" onClick={() => setShowLoginModal(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
              <div className="text-center mb-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-800">Welcome Back</h3>
                <p className="text-gray-500 mt-2">Sign in to your account</p>
              </div>
              <form onSubmit={handleLogin} className="space-y-5">
                <div>
                  <label htmlFor="loginEmail" className="block text-sm font-medium text-gray-700 mb-2">Email or Username</label>
                  <input type="text" id="loginEmail" required className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all" placeholder="Enter your email or username" />
                </div>
                <div id="passwordContainer" className="hidden">
                  <label htmlFor="loginPassword" className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <div className="relative">
                    <input type="password" id="loginPassword" className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all" placeholder="Enter your password" />
                    <button type="button" onClick={togglePassword} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      <svg id="eyeIcon" className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div id="forgotPasswordContainer" className="hidden flex items-center justify-between">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                    <span className="text-sm text-gray-600">Remember me</span>
                  </label>
                  <a href="#" onClick={handleForgotPassword} className="text-sm text-purple-600 hover:text-purple-700 font-medium">Forgot password?</a>
                </div>
                <div id="loginError" className="hidden bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">Invalid email or password</div>
                <button type="submit" id="loginBtn" className="w-full btn-gradient py-3.5 rounded-xl text-white font-semibold flex items-center justify-center space-x-2">
                  <span>Sign In</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                </button>
                <div className="hidden mt-6 text-center" id="signupcontainer">
                  <p className="text-sm text-gray-600">
                    Don&apos;t have an account? <button type="button" onClick={switchToRegister} className="text-purple-600 hover:text-purple-700 font-medium">Sign up</button>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Sales Modal (Similar design to homepage modals) */}
      {showSalesModal && (
        <div className="fixed inset-0 z-50">
          <div className="modal-backdrop absolute inset-0" onClick={() => setShowSalesModal(false)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setShowSalesModal(false)} />
          <div className="flex items-center justify-center min-h-screen p-4">
            <div className="bg-white rounded-3xl p-6 md:p-8 w-full max-w-md relative z-10 shadow-2xl animate-scale-in">
              <button type="button" onClick={() => setShowSalesModal(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
              <div className="text-center mb-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-800">Contact Sales</h3>
                <p className="text-gray-500 mt-2">Get in touch with our sales team</p>
              </div>
              <div className="space-y-4 text-center">
                <p className="text-gray-600">sales@ldttechnology.com</p>
                <p className="text-gray-600">Sales: +971 55 248 0485</p>
                <p className="text-gray-600">+91 9056909767</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay (Exact design from homepage) */}
      {showLoadingOverlay && (
        <div className="fixed inset-0 z-[60] bg-white/90 backdrop-blur-sm flex items-center justify-center">
          <div className="text-center">
            <div className="relative w-20 h-20 mx-auto mb-4">
              <div className="absolute inset-0 rounded-full border-4 border-purple-100" />
              <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-500 animate-spin" />
              <div className="absolute inset-2 rounded-full border-4 border-transparent border-t-pink-500 animate-spin" style={{ animationDuration: "0.8s", animationDirection: "reverse" }} />
            </div>
            <p className="text-gray-600 font-medium">Signing in...</p>
          </div>
        </div>
      )}
    </>
  );
}