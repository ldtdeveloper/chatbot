
(async function () {
  console.info("[Widget Loader] Starting...");

  const BACKEND_URL = "http://127.0.0.1:8000";

  async function loadWidget() {
    try {
      console.info("[Widget Loader] Fetching widget files...");
      
      const response = await fetch(`${BACKEND_URL}/get-widget`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch widget. Status: ${response.status}`);
      }

      const data = await response.json();

      // Validate response
      if (!data.html || !data.css || !data.js) {
        throw new Error("Invalid widget data received");
      }

      // Inject CSS
      if (data.css) {
        const styleTag = document.createElement("style");
        styleTag.textContent = data.css;
        styleTag.id = "voice-bot-styles";
        document.head.appendChild(styleTag);
        console.info("[Widget Loader] CSS injected");
      }

      // Inject HTML
      if (data.html) {
        const container = document.createElement("div");
        container.id = "voice-bot-container";
        container.innerHTML = data.html;
        document.body.appendChild(container);
        console.info("[Widget Loader] HTML injected");
      }

      // Inject JavaScript
      if (data.js) {
        const scriptTag = document.createElement("script");
        scriptTag.type = "module";
        scriptTag.textContent = data.js;
        scriptTag.id = "voice-bot-script";
        document.body.appendChild(scriptTag);
        console.info("[Widget Loader] JavaScript injected");
      }

      console.info("[Widget Loader]  Widget loaded successfully!");

    } catch (error) {
      console.error("[Widget Loader]  Error loading widget:", error);
      
      // Display error to user
      const errorDiv = document.createElement("div");
      errorDiv.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #ff4444;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        font-family: Arial, sans-serif;
        z-index: 10000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
      `;
      errorDiv.textContent = `Voice Bot Error: ${error.message}`;
      document.body.appendChild(errorDiv);

      // Auto-remove error after 5 seconds
      setTimeout(() => errorDiv.remove(), 5000);
    }
  }

  // Load widget when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadWidget);
  } else {
    await loadWidget();
  }

  // Expose reload function for debugging
  window.reloadVoiceBot = async function() {
    console.info("[Widget Loader] Reloading widget...");
    
    // Remove existing widget elements
    const container = document.getElementById("voice-bot-container");
    const styles = document.getElementById("voice-bot-styles");
    const script = document.getElementById("voice-bot-script");
    
    if (container) container.remove();
    if (styles) styles.remove();
    if (script) script.remove();
    
    // Reload
    await loadWidget();
  };

})();