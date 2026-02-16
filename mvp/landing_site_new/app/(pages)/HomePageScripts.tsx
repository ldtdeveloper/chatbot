"use client";

import { useEffect } from "react";

export function HomePageScripts() {
  useEffect(() => {
    // FAQ accordion
    const faqItems = document.querySelectorAll(".faq-item");
    faqItems.forEach((item) => {
      const btn = item.querySelector(".faq-btn");
      const content = item.querySelector(".faq-content");
      const icon = item.querySelector(".faq-content")?.parentElement?.querySelector("svg");
      const iconWrapper = item.querySelector(".faq-icon");

      if (!btn || !content) return;

      btn.addEventListener("click", () => {
        const isOpen = (content as HTMLElement).style.maxHeight;

        faqItems.forEach((i) => {
          const c = i.querySelector(".faq-content");
          const svg = i.querySelector(".faq-btn svg");
          const wrap = i.querySelector(".faq-icon");
          if (c) (c as HTMLElement).style.maxHeight = "";
          if (svg) svg.classList.remove("rotate-180");
          if (wrap) {
            wrap.classList.remove("bg-gradient-to-br", "from-indigo-500", "to-purple-600", "text-white");
            wrap.classList.add("bg-white", "text-black");
          }
        });

        if (!isOpen) {
          (content as HTMLElement).style.maxHeight = content.scrollHeight + "px";
          const svg = item.querySelector(".faq-btn svg");
          if (svg) svg.classList.add("rotate-180");
          if (iconWrapper) {
            iconWrapper.classList.remove("bg-white", "text-black");
            iconWrapper.classList.add("bg-gradient-to-br", "from-indigo-500", "to-purple-600", "text-white");
          }
        }
      });
    });

    // Pricing card active state
    const pricingCards = document.querySelectorAll(".pricing-card");
    pricingCards.forEach((card) => {
      card.addEventListener("click", () => {
        pricingCards.forEach((c) => {
          c.classList.remove(
            "bg-gradient-to-br",
            "from-cyan-400",
            "to-purple-500",
            "shadow-[0_0_40px_rgba(168,85,247,0.5)]"
          );
          c.classList.add("bg-white/5");
        });
        card.classList.remove("bg-white/5");
        card.classList.add(
          "bg-gradient-to-br",
          "from-cyan-400",
          "to-purple-500",
          "shadow-[0_0_40px_rgba(168,85,247,0.5)]"
        );
      });
    });
  }, []);

  return null;
}
