(function() {
    console.log("WhatsApp Agent Widget - Premium Version Loading...");

    const script = document.currentScript;
    const textAgentId = script.getAttribute('data-text-agent-id');
    const apiBase = script.getAttribute('data-api-base') || 'http://localhost:8081';

    if (!textAgentId) {
        console.error("WhatsApp Widget Error: Missing data-text-agent-id attribute");
        return;
    }

    // Advanced CSS with glassmorphism and animations
    const style = document.createElement('style');
    style.innerHTML = `
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap');
        
        .wa-widget-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 2147483647;
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .wa-tooltip {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 10px 18px;
            border-radius: 14px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            font-weight: 600;
            color: #1e293b;
            font-size: 14px;
            opacity: 0;
            transform: translateX(10px);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255,255,255,0.4);
        }

        .wa-widget-container:hover .wa-tooltip {
            opacity: 1;
            transform: translateX(0);
        }

        .wa-btn {
            width: 60px;
            height: 60px;
            background: #25D366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(37, 211, 102, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        .wa-btn:hover {
            transform: scale(1.08) translateY(-3px) !important;
            box-shadow: 0 15px 35px rgba(37, 211, 102, 0.4);
        }

        .wa-btn svg {
            width: 32px;
            height: 32px;
            fill: white;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }

        .wa-status-dot {
            position: absolute;
            top: 2px;
            right: 2px;
            width: 14px;
            height: 14px;
            background: #25D366;
            border: 2.5px solid white;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.className = 'wa-widget-container';

    const tooltip = document.createElement('div');
    tooltip.className = 'wa-tooltip';
    tooltip.innerText = 'Chat with us';

    const btn = document.createElement('div');
    btn.className = 'wa-btn';
    btn.innerHTML = `
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.445 0 .044 5.401.041 12.006c0 2.112.551 4.171 1.597 5.991L0 24l6.135-1.61a11.793 11.793 0 005.912 1.613h.005c6.604 0 12.001-5.401 12.004-12.006a11.812 11.812 0 00-3.486-8.486"/>
        </svg>
    `;

    btn.onclick = async () => {
        console.log(`Widget clicked - text_agent_id: ${textAgentId}`);

        try {
            const res = await fetch(`${apiBase}/api/whatsapp/status/${textAgentId}`);
            if (!res.ok) throw new Error("Status fetch failed");

            const data = await res.json();
            
            // Prioritize direct WhatsApp redirection if a phone number exists
            if (data.phone_number) {
                const cleanPhone = data.phone_number.replace(/\D/g, '');
                const waLink = `https://wa.me/${cleanPhone}`;
                console.log(`Redirecting to WhatsApp: ${waLink}`);
                window.open(waLink, '_blank');
            } else {
                // Fallback to AI chat only if no phone number is configured
                console.log("No phone number found, opening AI fallback...");
                window.open(`${apiBase}/chat?text_agent_id=${textAgentId}`, 'WhatsAppChat', 'width=420,height=680');
            }
        } catch (err) {
            console.error("Widget error:", err);
            window.open(`${apiBase}/chat?text_agent_id=${textAgentId}`, 'WhatsAppChat', 'width=420,height=680');
        }
    };

    container.appendChild(tooltip);
    container.appendChild(btn);
    document.body.appendChild(container);

    // Fade in animation
    container.style.opacity = '0';
    container.style.transition = 'opacity 0.8s ease';
    setTimeout(() => container.style.opacity = '1', 100);
})();
