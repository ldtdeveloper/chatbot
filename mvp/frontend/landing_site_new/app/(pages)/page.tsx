"use client";
/* eslint-disable @next/next/no-img-element */
import { HomePageScripts } from "./HomePageScripts";
import { PricingPlans } from "./PricingPlans";

// Images served from public folder (e.g. public/logo.png → /logo.png)
const IMG = "";

export default function HomePage() {
  return (
    <div className="gradient-mesh min-h-screen text-white overflow-x-hidden">
      {/* Floating Background Shapes */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="floating-shape w-96 h-96 bg-purple-900 shape-blob top-20 -left-48 animate-float" />
        <div className="floating-shape w-80 h-80 bg-indigo-900 shape-blob-2 top-40 right-0 animate-float-slow" />
        <div
          className="floating-shape w-72 h-72 bg-violet-900 shape-blob bottom-20 left-1/4 animate-float"
          style={{ animationDelay: "2s" }}
        />
        <div
          className="floating-shape w-64 h-64 bg-pink-900 shape-blob-2 bottom-40 right-1/4 animate-float-slow"
          style={{ animationDelay: "1s" }}
        />
      </div>

      {/* Navigation - Pill Navbar Style (Exact Match to Provided HTML) */}
      <nav className="main-navbar fixed top-0 left-0 right-0 z-50 px-6 py-4">
        <div className="nav-inner flex items-center justify-between py-2.5 px-7 rounded-full bg-white backdrop-blur-xl border border-purple-500/30 shadow-2xl max-w-5xl mx-auto gap-4">
          {/* Logo */}
          <div className="nav-logo flex-shrink-0">
            <img 
              src={`${IMG}/logo.png`} 
              alt="Voice Quick" 
              className="w-28 h-auto block sm:w-32" 
            />
          </div>

          {/* Center Links - Hidden on mobile/tablet, shown on md+ */}
          <div className="nav-center hidden md:flex items-center gap-8 flex-1 justify-center">
            <a href="#features" className="nav-link text-sm font-medium text-black hover:text-purple-600 transition">
              Features
            </a>
            <a href="#how-it-works" className="nav-link text-sm font-medium text-black hover:text-purple-600 transition">
              How it Works
            </a>
            <a href="#pricing" className="nav-link text-sm font-medium text-black hover:text-purple-600 transition">
              Pricing
            </a>
          </div>

          {/* Right Side */}
          <div className="nav-right flex items-center gap-4 flex-shrink-0">
            {/* Login - Hidden on very small screens */}
            <a 
              href="#" 
              className="login-link text-sm font-medium text-black hover:text-purple-600 transition hidden sm:inline-block"
              onClick={(e) => { 
                e.preventDefault(); 
                if (typeof window !== "undefined" && (window as any).openLoginModal) {
                  (window as any).openLoginModal();
                }
              }}
            >
              Login
            </a>

            {/* Get Started Button */}
            <a 
              href="#pricing" 
              className="cta-btn bg-gradient-to-br from-purple-600 to-pink-600 text-white font-semibold text-sm px-6 py-2.5 rounded-full hover:opacity-90 transition"
            >
              Get Started
            </a>
          </div>
        </div>

        {/* Tablet Adjustments */}
        <style jsx>{`
          @media (max-width: 900px) {
            .nav-inner {
              padding: 8px 20px !important;
              gap: 12px !important;
            }
            .nav-center {
              gap: 20px !important;
            }
            .nav-link {
              font-size: 13px !important;
            }
            .nav-right {
              gap: 12px !important;
            }
          }

          /* Mobile - Hide center & login, smaller elements */
          @media (max-width: 640px) {
            .nav-center {
              display: none !important;
            }
            .nav-inner {
              padding: 8px 18px !important;
              gap: 0 !important;
            }
            .login-link {
              display: none !important;
            }
            .nav-logo img {
              width: 90px !important;
            }
            .cta-btn {
              font-size: 13px !important;
              padding: 8px 16px !important;
            }
          }
        `}</style>
      </nav>

      {/* Hero Section */}
      <section className="mt-24 min-h-screen flex items-center pt-16 md:pt-0 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            <div className="space-y-6 md:space-y-8 text-center lg:text-left order-2 lg:order-1">
              <div className="inline-flex items-center space-x-2 bg-purple-900/50 backdrop-blur px-4 py-2 rounded-full shadow-md border border-purple-700 animate-fade-in">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-sm text-gray-300 font-medium">Enterprise-Grade AI Voice Assistant</span>
              </div>
              <h1 className="hero-title text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold leading-tight animate-slide-up text-white">
                Build <span className="gradient-text">Intelligent</span>
                <br className="hidden sm:block" />
                Voice Assistant
              </h1>
              <p className="text-lg md:text-xl text-gray-300 max-w-lg mx-auto lg:mx-0 animate-slide-up delay-100" style={{ opacity: 0 }}>
                Design a human-like AI Voice Bot that answers calls, resolves queries, and automates conversations on-scale. Integrate seamlessly with your existing platforms.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-slide-up delay-200" style={{ opacity: 0 }}>
                <button
                  type="button"
                  onClick={() => typeof window !== "undefined" && (window as any).openLoginModal?.()}
                  className="btn-gradient px-6 sm:px-8 py-3 sm:py-4 rounded-full text-white font-semibold text-base sm:text-lg flex items-center justify-center space-x-2"
                >
                  <span>Start Building Free</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
                <a
                  href="#how-it-works"
                  className="relative inline-flex items-center justify-center p-[2px] rounded-full bg-gradient-to-r from-purple-600 via-pink-500 to-indigo-500"
                >
                  <span className="bg-white text-purple-700 px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold text-base sm:text-lg flex items-center space-x-2 hover:bg-gray-100 transition">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Watch Demo</span>
                  </span>
                </a>
              </div>
              <div className="flex items-center justify-center lg:justify-start space-x-6 md:space-x-8 pt-6 md:pt-8 animate-slide-up delay-300" style={{ opacity: 0 }}>
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold gradient-text">10K+</div>
                  <div className="text-gray-400 text-sm">Voice Calls</div>
                </div>
                <div className="w-px h-12 bg-purple-800" />
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold gradient-text">99.9%</div>
                  <div className="text-gray-400 text-sm">Uptime</div>
                </div>
                <div className="w-px h-12 bg-purple-800" />
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold gradient-text">&lt;500ms</div>
                  <div className="text-gray-400 text-sm">Latency</div>
                </div>
              </div>
            </div>
            <div className="relative animate-float order-1 lg:order-2">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-full blur-3xl" />
              <div className="relative flex items-center justify-center" style={{ height: 350 }}>
                <div className="relative">
                  <div className="absolute inset-0 w-64 h-64 md:w-80 md:h-80 rounded-full border-4 border-purple-700 animate-spin-slow" />
                  <div className="absolute inset-4 w-56 h-56 md:w-72 md:h-72 rounded-full border-4 border-pink-700 animate-spin-slow" style={{ animationDirection: "reverse" }} />
                  <div className="relative w-64 h-64 md:w-80 md:h-80 rounded-full bg-gradient-to-br from-purple-800 via-pink-800 to-indigo-800 flex items-center justify-center shadow-2xl">
                    <div className="w-48 h-48 md:w-60 md:h-60 rounded-full bg-black/20 backdrop-blur flex items-center justify-center">
                      <svg className="w-24 h-24 md:w-32 md:h-32 text-white animate-pulse-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                  </div>
                  <div className="absolute -top-4 -right-4 w-8 h-8 rounded-full bg-gradient-to-br from-yellow-600 to-orange-600 animate-bounce-soft shadow-lg" />
                  <div className="absolute -bottom-2 -left-6 w-6 h-6 rounded-full bg-gradient-to-br from-cyan-600 to-blue-600 animate-bounce-soft shadow-lg" style={{ animationDelay: "0.5s" }} />
                  <div className="absolute top-1/2 -right-8 w-4 h-4 rounded-full bg-gradient-to-br from-green-600 to-emerald-600 animate-bounce-soft shadow-lg" style={{ animationDelay: "1s" }} />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce-soft hidden md:block">
          <div className="w-8 h-12 rounded-full border-2 border-purple-700 flex items-start justify-center p-2">
            <div className="w-1.5 h-3 bg-purple-500 rounded-full animate-bounce" />
          </div>
        </div>
      </section>

      {/* Channel Section - Mobile Responsive Fix */}
      <section className="channel-section py-12 sm:py-16 md:py-20 lg:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-extrabold mb-4 px-4">
            <span className="channel-gradient-text">One AI Voice Assistant for Every Channel</span>
          </h2>
          <p className="text-sm sm:text-base md:text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed px-4 mb-8 sm:mb-12">
            Design and manage an AI Voice Bot that operates seamlessly across voice, chat, SMS, and digital channels. Voicequik delivers unified conversations with built-in compliance, reliability, and real-time insights.
          </p>

          {/* Mobile Version: Simple vertical/grid cards - clean & easy to tap */}
          <div className="block lg:hidden">
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-6 sm:gap-8 max-w-3xl mx-auto">
              {/* EMAIL */}
              <div className="flex flex-col items-center">
                <div className="channel-icon-box w-12 h-12 sm:w-16 sm:h-16">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="M2 7l10 7 10-7" />
                  </svg>
                </div>
                <span className="channel-label mt-3 text-sm sm:text-base">EMAIL</span>
              </div>

              {/* CHAT */}
              <div className="flex flex-col items-center">
                <div className="channel-icon-box w-12 h-12 sm:w-16 sm:h-16">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    <circle cx="9" cy="10" r="1" fill="currentColor" />
                    <circle cx="12" cy="10" r="1" fill="currentColor" />
                    <circle cx="15" cy="10" r="1" fill="currentColor" />
                  </svg>
                </div>
                <span className="channel-label mt-3 text-sm sm:text-base">CHAT</span>
              </div>

              {/* WHATSAPP */}
              <div className="flex flex-col items-center">
                <div className="channel-icon-box w-12 h-12 sm:w-16 sm:h-16">
                  <svg viewBox="0 0 24 24" fill="currentColor" style={{ color: "#7c3aed" }}>
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
                </div>
                <span className="channel-label mt-3 text-sm sm:text-base">WHATSAPP</span>
              </div>

              {/* SMS */}
              <div className="flex flex-col items-center">
                <div className="channel-icon-box w-12 h-12 sm:w-16 sm:h-16">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#7c3aed" }}>
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    <line x1="8" y1="10" x2="8.01" y2="10" strokeWidth="3" />
                    <line x1="12" y1="10" x2="12.01" y2="10" strokeWidth="3" />
                    <line x1="16" y1="10" x2="16.01" y2="10" strokeWidth="3" />
                  </svg>
                </div>
                <span className="channel-label mt-3 text-sm sm:text-base">SMS</span>
              </div>

              {/* VOICE - larger icon in center */}
              <div className="flex flex-col items-center col-span-3 sm:col-span-1 order-first sm:order-none mb-6 sm:mb-0">
                <div className="channel-icon-box channel-voice-icon w-16 h-16 sm:w-20 sm:h-20">
                  <svg viewBox="0 0 40 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="0" y="10" width="4" height="8" rx="2" fill="white" />
                    <rect x="6" y="6" width="4" height="16" rx="2" fill="white" />
                    <rect x="12" y="2" width="4" height="24" rx="2" fill="white" />
                    <rect x="18" y="0" width="4" height="28" rx="2" fill="white" />
                    <rect x="24" y="2" width="4" height="24" rx="2" fill="white" />
                    <rect x="30" y="6" width="4" height="16" rx="2" fill="white" />
                    <rect x="36" y="10" width="4" height="8" rx="2" fill="white" />
                  </svg>
                </div>
                <span className="channel-label channel-voice-label mt-3 text-base sm:text-lg font-semibold">VOICE</span>
              </div>
            </div>
          </div>

          {/* Desktop Version: Exact original arc layout (unchanged) */}
          <div className="hidden lg:block channel-arc-wrapper relative mt-12 max-w-5xl mx-auto">
            <div className="channel-rings-container relative w-full" aria-hidden>
              <svg className="channel-rings-svg w-full h-auto" viewBox="0 0 900 520" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                <path d="M 60 460 A 390 390 0 0 1 840 460" stroke="rgba(140,80,255,0.28)" strokeWidth="1.5" fill="none" />
                <path d="M 120 460 A 330 330 0 0 1 780 460" stroke="rgba(140,80,255,0.22)" strokeWidth="1.5" fill="none" />
                <path d="M 190 460 A 260 260 0 0 1 710 460" stroke="rgba(140,80,255,0.18)" strokeWidth="1.5" fill="none" />
                <path d="M 265 460 A 185 185 0 0 1 635 460" stroke="rgba(140,80,255,0.14)" strokeWidth="1.5" fill="none" />
                <path d="M 190 460 A 260 260 0 0 1 710 460 Z" fill="rgba(80,20,160,0.22)" />
              </svg>
            </div>
            <div className="channel-card channel-email">
              <div className="channel-card-inner">
                <div className="channel-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="M2 7l10 7 10-7" />
                  </svg>
                </div>
                <span className="channel-label">EMAIL</span>
              </div>
            </div>
            <div className="channel-card channel-chat">
              <div className="channel-card-inner">
                <div className="channel-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    <circle cx="9" cy="10" r="1" fill="currentColor" />
                    <circle cx="12" cy="10" r="1" fill="currentColor" />
                    <circle cx="15" cy="10" r="1" fill="currentColor" />
                  </svg>
                </div>
                <span className="channel-label">CHAT</span>
              </div>
            </div>
            <div className="channel-card channel-whatsapp">
              <div className="channel-card-inner">
                <div className="channel-icon-box">
                  <svg viewBox="0 0 24 24" fill="currentColor" style={{ color: "#7c3aed" }}>
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
                </div>
                <span className="channel-label">WHATSAPP</span>
              </div>
            </div>
            <div className="channel-card channel-sms">
              <div className="channel-card-inner">
                <div className="channel-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#7c3aed" }}>
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    <line x1="8" y1="10" x2="8.01" y2="10" strokeWidth="3" />
                    <line x1="12" y1="10" x2="12.01" y2="10" strokeWidth="3" />
                    <line x1="16" y1="10" x2="16.01" y2="10" strokeWidth="3" />
                  </svg>
                </div>
                <span className="channel-label">SMS</span>
              </div>
            </div>
            <div className="channel-card channel-voice">
              <div className="channel-card-inner channel-voice-inner">
                <div className="channel-icon-box channel-voice-icon">
                  <svg viewBox="0 0 40 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="0" y="10" width="4" height="8" rx="2" fill="white" />
                    <rect x="6" y="6" width="4" height="16" rx="2" fill="white" />
                    <rect x="12" y="2" width="4" height="24" rx="2" fill="white" />
                    <rect x="18" y="0" width="4" height="28" rx="2" fill="white" />
                    <rect x="24" y="2" width="4" height="24" rx="2" fill="white" />
                    <rect x="30" y="6" width="4" height="16" rx="2" fill="white" />
                    <rect x="36" y="10" width="4" height="8" rx="2" fill="white" />
                  </svg>
                </div>
                <span className="channel-label channel-voice-label">VOICE</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Launch AI Voice Bot Section - Mobile Responsive Fix */}
      <section className="w-full launch-section flex flex-col lg:flex-row items-stretch justify-center py-12 md:py-16 lg:py-24 px-4 sm:px-6">
        <div className="launch-features w-full lg:w-[10%] flex flex-row lg:flex-col items-center lg:items-start justify-center gap-4 lg:gap-6 mb-8 lg:mb-0 flex-wrap">
          <div className="feature-card w-36 sm:w-40 lg:w-auto">
            <img className="w-12 sm:w-16 mx-auto" src={`${IMG}/online.png`} alt="Online Shopping Support" />
            <span className="text-black text-xs sm:text-sm text-center">Online Shopping Support</span>
          </div>
          <div className="feature-card w-36 sm:w-40 lg:w-auto">
            <img className="w-12 sm:w-16 mx-auto" src={`${IMG}/order.png`} alt="Order Management" />
            <span className="text-black text-xs sm:text-sm text-center">Order Management</span>
          </div>
          <div className="feature-card w-36 sm:w-40 lg:w-auto">
            <img className="w-12 sm:w-16 mx-auto" src={`${IMG}/appointment.png`} alt="Appointment Scheduling" />
            <span className="text-black text-xs sm:text-sm text-center">Appointment Scheduling</span>
          </div>
          <div className="feature-card w-36 sm:w-40 lg:w-auto">
            <img className="w-12 sm:w-16 mx-auto" src={`${IMG}/bank.png`} alt="Banking Assistance" />
            <span className="text-black text-xs sm:text-sm text-center">Banking Assistance</span>
          </div>
        </div>
        <div className="main w-full lg:w-3/5 flex flex-col sm:flex-row ml-0 lg:ml-10 relative rounded-2xl overflow-hidden bg-gradient-to-br from-purple-900/50 to-pink-900/50 backdrop-blur-lg border border-purple-700 shadow-2xl">
          <div className="left w-full sm:w-1/2">
            <img className="w-full h-48 sm:h-full object-cover" src={`${IMG}/aiwomen.png`} alt="AI Assistant" />
          </div>
          <div className="launch-content w-full sm:w-1/2 text-white flex flex-col justify-between p-4 sm:p-6">
            <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl ml-0 sm:ml-2 mt-2 sm:mt-6">
              Launch an AI Voice<br />Bot in Minutes
            </h2>
            <p className="ml-0 sm:ml-2 text-xs sm:text-sm mt-2 sm:mt-3">
              Create an intelligent AI Voice Assistant that operates reliably across channels with built-in compliance and analytics.
            </p>
            <button type="button" className="launch-btn w-full sm:w-auto px-4 py-2 sm:px-6 sm:py-3 text-sm sm:text-base mt-4 sm:mt-0">Try Live Demo</button>
            <div className="mt-4 sm:mt-0">
              <img className="h-20 sm:h-24 md:h-36 w-full wave-img" src={`${IMG}/wave.png`} alt="Waveform" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 md:py-24 relative bg-gradient-to-b from-[#0f0f1a] to-[#140f24]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-4">
              Powerful <span className="text-purple-400">Features</span>
            </h2>
            <p className="text-gray-300 text-lg max-w-2xl mx-auto">Everything you need to create exceptional voice experiences</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { img: "voice.png", title: "Real-time Voice AI", desc: "Enable natural, low-latency voice conversations with AI-powered responses that feel human, fast, and context-aware." },
              { img: "widget.png", title: "Easy Widget Embed", desc: "Deploy your AI voice assistant on any website using a single line of code with no complex setup required." },
              { img: "secure.png", title: "Secure API Management", desc: "Protect sensitive API keys with encrypted storage and ensure they are never exposed to frontend environments." },
              { img: "analytics.png", title: "Real-Time Analytics", desc: "Track conversations, monitor usage, analyze costs, and gain actionable insights through detailed dashboards." },
              { img: "agent.png", title: "Custom AI Agents", desc: "Create multiple voice agents with unique personalities, voices, and instructions tailored to specific use cases." },
              { img: "report.png", title: "Automated Weekly Reports", desc: "Get scheduled reports with AI Voice Bot usage, performance, and cost summaries — delivered automatically." },
            ].map((f) => (
              <div key={f.title} className="bg-[#1a1a1f] rounded-2xl p-8 text-center border border-purple-500 hover:border-pink-500 transition duration-300 shadow-lg hover:shadow-purple-500/30">
                <div className="flex justify-center mb-6">
                  <img src={`${IMG}/${f.img}`} alt={f.title} className="w-20 h-20 object-contain" />
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{f.title}</h3>
                <p className="text-gray-300 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Seamless Integrations */}
      <section className="py-16 md:py-24 bg-gradient-to-b from-[#0f0f1a] to-[#140f24] relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12 bg-[#0b0b18] border border-purple-600/40 rounded-3xl p-8 md:p-12 shadow-[0_0_40px_rgba(168,85,247,0.2)]">
            <div className="lg:w-1/2 text-left">
              <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-6 leading-tight">
                Seamless Integrations <br />Across Your Tech Stack
              </h2>
              <p className="text-gray-300 text-lg mb-8 max-w-xl">
                VoiceQuik integrates seamlessly with the tools your teams already rely on — CRMs, CCaaS platforms, calendars, and internal systems. AI Voice Assistant operates within your workflows, updating records, routing calls, and triggering actions in real time.
              </p>
              <button type="button" className="px-6 py-3 rounded-full bg-gradient-to-r from-purple-600 to-pink-500 hover:opacity-90 transition text-white font-semibold">
                Explore Integrations
              </button>
            </div>
            <div className="lg:w-1/2 flex justify-center">
              <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-3xl shadow-2xl">
                <img src={`${IMG}/techstack.png`} alt="Tech Stack Integrations" className="w-full max-w-md mx-auto object-contain" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-16 md:py-20 bg-gradient-to-b from-[#0f0f1a] to-[#140f24] relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-4">
              How It <span className="text-purple-400">Works</span>
            </h2>
            <p className="text-gray-300 text-lg">Get started in just 4 simple steps</p>
          </div>
          <div className="grid md:grid-cols-4 gap-6 items-stretch">
            {[
              { num: "01", color: "from-purple-600 to-indigo-700", img: "phone.png", title: "Register", desc: "Create your VoiceQuik account and access your dashboard in minutes." },
              { num: "02", color: "from-pink-600 to-rose-700", img: "robot.png", title: "Create Your Agent", desc: "Define your AI agent's personality, voice, tone, and behavior with custom instructions." },
              { num: "03", color: "from-indigo-600 to-purple-700", img: "book.png", title: "Add Your Knowledge Base", desc: "Upload documents or connect data sources to train your agent with relevant business information." },
              { num: "04", color: "from-violet-600 to-pink-700", img: "rocket.png", title: "Embed & Launch", desc: "Copy the integration code or connect via API to deploy your AI voice assistant instantly." },
            ].map((s) => (
              <div key={s.num} className="relative text-center flex flex-col">
                <div className={`w-20 aspect-square shrink-0 mx-auto mb-8 rounded-full bg-gradient-to-br ${s.color} flex items-center justify-center text-2xl font-bold text-white shadow-lg border-4 border-[#1a1a1f]`}>
                  {s.num}
                </div>
                <div className="bg-[#1a1a1f] border border-purple-500 rounded-2xl p-8 shadow-lg h-full flex flex-col">
                  <div className="flex justify-center mb-6">
                    <img src={`${IMG}/${s.img}`} alt={s.title} className="w-20 h-20 object-contain" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-3">{s.title}</h3>
                  <p className="text-gray-300 text-sm leading-relaxed flex-grow">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Language Support */}
      <section className="py-16 md:py-24 relative bg-gradient-to-b from-[#0f0f1a] to-[#140f24]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          <div className="space-y-4 md:space-y-6">
            <h3 className="text-lg font-semibold text-gray-300">Language Support</h3>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white leading-tight">
              Speak Every Language<br />Reach Every Customer.
            </h2>
            <p className="text-base md:text-lg text-gray-300 max-w-md">
              Voicequik supports text-to-speech and speech-to-text in 15+ languages, with localization and accent support.
            </p>
            <button type="button" className="btn-gradient px-8 py-3 rounded-full text-white font-semibold" onClick={() => typeof window !== "undefined" && (window as any).openLoginModal?.()}>
              Start Building Free
            </button>
          </div>
          <div>
            <img src={`${IMG}/languages.png`} alt="Language Support List" className="rounded-2xl shadow-lg w-full" />
          </div>
        </div>
      </section>

      {/* Pricing Section - container for script.js to inject plans */}
      <section id="pricing" className="py-20 md:py-28 bg-gradient-to-b from-[#0f0f1a] to-[#140f24] relative">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 max-w-7xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-4">
              Simple <span className="bg-gradient-to-r from-indigo-400 to-pink-500 bg-clip-text text-transparent">Pricing</span>
            </h2>
            <p className="text-gray-300 text-lg max-w-2xl mx-auto">Choose the plan that fits your needs. All plans include core features.</p>
          </div>
          <PricingPlans />
        </div>
      </section>

      {/* Use Cases */}
      <section id="use-cases" className="py-20 md:py-28 bg-gradient-to-b from-[#0b0615] via-[#140a25] to-[#0b0615]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-extrabold text-center mb-16 bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
            Use Cases
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { img: "bpo.png", title: "BPO & Call Centres" },
              { img: "retail.jpg", title: "Retail & eCommerce" },
              { img: "financial.png", title: "Financial Services & Insurance" },
              { img: "realestate.png", title: "Real Estate" },
              { img: "healthcare.png", title: "Healthcare" },
              { img: "travel.png", title: "Travel & Hospitality" },
              { img: "telecomm.png", title: "Telecom & Utilities" },
              { img: "education.png", title: "Education & Training" },
            ].map((u) => (
              <div key={u.title} className="relative group rounded-2xl overflow-hidden border border-purple-500/40 hover:border-purple-500 transition duration-300">
                <img src={`${IMG}/${u.img}`} className="w-full h-60 object-cover group-hover:scale-105 transition duration-500" alt={u.title} />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
                <div className="absolute bottom-4 left-4">
                  <h3 className="text-white font-semibold text-lg">
                    {u.title.includes(" & ") ? (
                      <>{(u.title.split(" & ")[0])} & <br />{u.title.split(" & ").slice(1).join(" & ")}</>
                    ) : (
                      u.title
                    )}
                  </h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 md:py-28 bg-[#0b0615]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative rounded-3xl overflow-hidden border-2 border-purple-500">
            <div className="absolute inset-0">
              <img src={`${IMG}/bgimage.png`} alt="AI Voice Assistant Background" className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/70 to-black/90" />
            </div>
            <div className="relative z-10 text-center py-16 md:py-24 px-6">
              <div className="w-16 h-16 mx-auto mb-8 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-xl">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white leading-tight mb-10">
                Ready to Scale with an AI <br className="hidden sm:block" /> Voice Assistant?
              </h2>
              <button
                type="button"
                onClick={() => typeof window !== "undefined" && (window as any).openLoginModal?.()}
                className="px-10 py-4 rounded-full text-white font-semibold text-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:opacity-90 transition duration-300 shadow-lg"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 md:py-28 bg-gradient-to-b from-[#0b0615] via-[#140a25] to-[#0b0615] relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-center mb-12 sm:mb-16 bg-gradient-to-r from-indigo-400 to-pink-500 bg-clip-text text-transparent">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4 sm:space-y-6">
            {[
              { q: "What is VoiceQuik?", a: "VoiceQuik is an AI-powered voice automation platform that enables businesses to deploy intelligent voice assistants for sales, support, and operations." },
              { q: "How fast can I deploy an AI Voice Bot with VoiceQuik?", a: "Deployment can typically be completed within days depending on your workflow complexity and integration requirements." },
              { q: "Can VoiceQuik's AI Voice Bot integrate with my existing systems?", a: "Yes. VoiceQuik integrates seamlessly with CRMs, CCaaS platforms, calendars, and internal tools. Your AI Voice Assistant can update records, route calls, trigger actions, and operate directly within your existing workflows." },
              { q: "Is VoiceQuik secure and compliant for enterprise use?", a: "Yes. VoiceQuik follows enterprise-grade security standards, encryption protocols, and compliance requirements." },
              { q: "Which industries can benefit from VoiceQuik's AI Voice Assistant?", a: "Industries including healthcare, finance, real estate, e-commerce, logistics, and customer support teams can benefit from VoiceQuik." },
            ].map((faq) => (
              <div key={faq.q} className="faq-item bg-[#1b1b22] rounded-2xl overflow-hidden shadow-lg">
                <button 
                  type="button" 
                  className="faq-btn w-full flex justify-between items-center px-4 sm:px-6 md:px-8 py-4 sm:py-5 md:py-6 text-left transition-all duration-300 hover:bg-[#222228]"
                >
                  <span className="text-white text-base sm:text-lg font-medium pr-4">
                    {faq.q}
                  </span>
                  <span className="faq-icon w-10 h-10 sm:w-11 sm:h-11 md:w-12 md:h-12 flex-shrink-0 flex items-center justify-center rounded-full bg-white text-black transition-all duration-300">
                    <svg className="w-5 h-5 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </button>
                <div className="faq-content max-h-0 overflow-hidden transition-all duration-500">
                  <p className="px-4 sm:px-6 md:px-8 pb-5 sm:pb-6 text-gray-300 text-sm sm:text-base leading-relaxed">
                    {faq.a}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative bg-gradient-to-b from-[#0b0615] via-[#140a25] to-[#0b0615] text-gray-300">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="grid md:grid-cols-5 gap-12">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 mb-8">
                <img src={`${IMG}/logo.png`} alt="VoiceQuik Logo" className="w-12 h-12" />
                <span className="text-2xl font-bold text-white">VoiceQuik</span>
              </div>
              <div className="space-y-5 text-sm text-gray-400">
                <div className="flex items-start gap-3">
                  <i className="fa-solid fa-location-dot text-purple-400 mt-1" />
                  <p>UAE Meydan Grandstand, 6th floor,<br />Meydan Road, Nad Al Sheba, Dubai.</p>
                </div>
                <div className="flex items-start gap-3">
                  <i className="fa-solid fa-location-dot text-purple-400 mt-1" />
                  <p>India Office 24A, 3rd Floor Motiaz Royal Business Park,<br />Zirakpur, Punjab 140603.</p>
                </div>
                <div className="flex items-center gap-3">
                  <i className="fa-solid fa-envelope text-purple-400" />
                  <p>sales@ldttechnology.com</p>
                </div>
                <div className="flex items-start gap-3">
                  <i className="fa-solid fa-phone text-purple-400 mt-1" />
                  <p>Sales: +971 55 248 0485, +91-77194 28662<br />HR : +91-76968 84332</p>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-6">About Us</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">VoiceQuik</a></li>
                <li><a href="#" className="hover:text-white transition">Use Cases</a></li>
                <li><a href="#" className="hover:text-white transition">Careers</a></li>
                <li><a href="#" className="hover:text-white transition">Contact Us</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-6">Terms and Conditions</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition">FAQ</a></li>
                <li><a href="#" className="hover:text-white transition">Service Availability</a></li>
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-6">Refund Policy</h4>
              <ul className="space-y-3 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">Billing & Payments</a></li>
                <li><a href="#" className="hover:text-white transition">Refund Eligibility</a></li>
                <li><a href="#" className="hover:text-white transition">Cancellation Policy</a></li>
              </ul>
              <div className="mt-8">
                <h4 className="text-white font-semibold mb-4">Our Social media</h4>
                <div className="flex space-x-5 text-gray-400 text-lg">
                  <a href="https://www.facebook.com/ldttechnologypvtltd/" className="hover:text-white transition" target="_blank" rel="noopener noreferrer"><i className="fa-brands fa-facebook-f" /></a>
                  <a href="https://cd.linkedin.com/company/ldt-technology-ldttechnology" className="hover:text-white transition" target="_blank" rel="noopener noreferrer"><i className="fa-brands fa-linkedin-in" /></a>
                  <a href="https://x.com/LDTTechPvtLtd" className="hover:text-white transition" target="_blank" rel="noopener noreferrer"><i className="fa-brands fa-x-twitter" /></a>
                  <a href="https://www.instagram.com/ldttechnologypvtltd/" className="hover:text-white transition" target="_blank" rel="noopener noreferrer"><i className="fa-brands fa-instagram" /></a>
                  <a href="https://in.pinterest.com/ldttechnology/" className="hover:text-white transition" target="_blank" rel="noopener noreferrer"><i className="fa-brands fa-pinterest-p" /></a>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="h-[1px] w-full bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500" />
        <div className="py-6 text-center text-sm text-gray-400">© 2026 VoiceQuik by LDT Technology Pvt. Ltd. All rights reserved.</div>
      </footer>

      {/* Modals and overlay - same structure as home.html for script.js */}
      <RegisterModal />
      <LoginModal />
      <LoadingOverlay />

      <HomePageScripts />
    </div>
  );
}

function RegisterModal() {
  return (
    <div id="registerModal" className="fixed inset-0 z-50 hidden">
      <div className="modal-backdrop absolute inset-0" onClick={() => typeof window !== "undefined" && (window as any).closeRegisterModal?.()} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && (window as any).closeRegisterModal?.()} />
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="bg-white rounded-3xl p-6 md:p-8 w-full max-w-md relative z-10 shadow-2xl animate-scale-in max-h-[90vh] overflow-y-auto">
          <button type="button" onClick={() => (window as any).closeRegisterModal?.()} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-800">Create Account</h3>
            <p className="text-gray-500 mt-2">Sign up to get started</p>
            <div id="selectedPlanInfo" className="mt-3 px-4 py-2 bg-purple-50 rounded-lg border border-purple-200 hidden">
              <span className="text-sm font-medium text-purple-700">Selected Plan: <span id="planName" /> - $<span id="planPrice" />/month</span>
            </div>
          </div>
          <form id="registerForm" onSubmit={(e) => { e.preventDefault(); (window as any).handleRegister?.(e); }} className="space-y-5">
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
              <button type="button" onClick={() => (window as any).switchToLogin?.()} className="text-purple-600 hover:text-purple-700 font-medium">Sign in</button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoginModal() {
  return (
    <div id="loginModal" className="fixed inset-0 z-50 hidden">
      <div className="modal-backdrop absolute inset-0" onClick={() => (window as any).closeLoginModal?.()} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && (window as any).closeLoginModal?.()} />
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="bg-white rounded-3xl p-6 md:p-8 w-full max-w-md relative z-10 shadow-2xl animate-scale-in">
          <button type="button" onClick={() => (window as any).closeLoginModal?.()} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-800">Welcome Back</h3>
            <p className="text-gray-500 mt-2">Sign in to your account</p>
          </div>
          <form id="loginForm" onSubmit={(e) => { e.preventDefault(); (window as any).handleLogin?.(e); }} className="space-y-5">
            <div>
              <label htmlFor="loginEmail" className="block text-sm font-medium text-gray-700 mb-2">Email or Username</label>
              <input type="text" id="loginEmail" required className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all" placeholder="Enter your email or username" />
            </div>
            <div id="passwordContainer" className="hidden">
              <label htmlFor="loginPassword" className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <div className="relative">
                <input type="password" id="loginPassword" className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all" placeholder="Enter your password" />
                <button type="button" onClick={() => (window as any).togglePassword?.()} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
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
              <a href="#" onClick={(e) => { e.preventDefault(); (window as any).handleForgotPassword?.(e); }} className="text-sm text-purple-600 hover:text-purple-700 font-medium">Forgot password?</a>
            </div>
            <div id="loginError" className="hidden bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">Invalid email or password</div>
            <button type="submit" id="loginBtn" className="w-full btn-gradient py-3.5 rounded-xl text-white font-semibold flex items-center justify-center space-x-2">
              <span>Sign In</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </button>
            <div className="hidden mt-6 text-center" id="signupcontainer">
              <p className="text-sm text-gray-600">
                Don&apos;t have an account? <button type="button" onClick={() => (window as any).switchToRegister?.()} className="text-purple-600 hover:text-purple-700 font-medium">Sign up</button>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function LoadingOverlay() {
  return (
    <div id="loadingOverlay" className="fixed inset-0 z-[60] hidden bg-white/90 backdrop-blur-sm flex items-center justify-center">
      <div className="text-center">
        <div className="relative w-20 h-20 mx-auto mb-4">
          <div className="absolute inset-0 rounded-full border-4 border-purple-100" />
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-500 animate-spin" />
          <div className="absolute inset-2 rounded-full border-4 border-transparent border-t-pink-500 animate-spin" style={{ animationDuration: "0.8s", animationDirection: "reverse" }} />
        </div>
        <p className="text-gray-600 font-medium">Signing in...</p>
      </div>
    </div>
  );
}