// Frontend Logic for Long Châu Care Guide

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessagesContainer = document.getElementById("chat-messages-container");
    const sendBtn = document.getElementById("send-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");
    
    // Config Elements
    const aiProvider = document.getElementById("ai-provider");
    const apiKeyContainer = document.getElementById("api-key-container");
    const apiKeyInput = document.getElementById("api-key");
    
    // Logger Elements
    const logConsole = document.getElementById("log-console");
    const clearLogsBtn = document.getElementById("clear-logs-btn");
    
    // Demo Preset Buttons
    const presetHappy = document.getElementById("preset-happy");
    const presetLowConf = document.getElementById("preset-low-conf");
    const presetSafety = document.getElementById("preset-safety");
    const presetCorrection = document.getElementById("preset-correction");

    // Load saved API Key and Provider from LocalStorage
    if (localStorage.getItem("longchau_api_provider")) {
        aiProvider.value = localStorage.getItem("longchau_api_provider");
    }
    if (localStorage.getItem("longchau_api_key")) {
        apiKeyInput.value = localStorage.getItem("longchau_api_key");
    }
    
    // Toggle API Key input visibility
    function toggleApiKeyVisibility() {
        if (aiProvider.value === "mock") {
            apiKeyContainer.style.display = "none";
        } else {
            apiKeyContainer.style.display = "block";
            apiKeyInput.placeholder = aiProvider.value === "gemini" ? "Nhập Gemini API Key..." : "Nhập OpenAI API Key...";
        }
        localStorage.setItem("longchau_api_provider", aiProvider.value);
    }
    
    aiProvider.addEventListener("change", toggleApiKeyVisibility);
    apiKeyInput.addEventListener("input", () => {
        localStorage.setItem("longchau_api_key", apiKeyInput.value.trim());
    });
    toggleApiKeyVisibility();

    // Logger helper
    function addLog(type, message) {
        const timestamp = new Date().toLocaleTimeString();
        const logLine = document.createElement("div");
        logLine.className = `log-line ${type}`;
        logLine.innerHTML = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
        logConsole.appendChild(logLine);
        logConsole.scrollTop = logConsole.scrollHeight;
    }

    // Clear logs
    clearLogsBtn.addEventListener("click", () => {
        logConsole.innerHTML = '<div class="log-line system">[System] Logs cleared.</div>';
    });

    // Clear Chat
    clearChatBtn.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p>Lịch sử trò chuyện đã được làm mới. Tôi sẵn sàng hỗ trợ bạn.</p>
                </div>
            </div>
        `;
        addLog("system", "Lịch sử trò chuyện được đặt lại.");
    });

    // Append standard user/bot message bubble
    function appendMessage(sender, content, customClass = "") {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message ${customClass}`;
        
        const avatarDiv = document.createElement("div");
        avatarDiv.className = "avatar";
        avatarDiv.textContent = sender === "user" ? "👤" : "🤖";
        
        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "message-bubble";
        bubbleDiv.innerHTML = content;
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        chatMessagesContainer.appendChild(messageDiv);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        
        return messageDiv;
    }

    // Render diagnostic structure (symptoms, products, recommendations)
    function appendDiagnosticMessage(data) {
        const messageDiv = document.createElement("div");
        messageDiv.className = "message system-message";
        
        const avatarDiv = document.createElement("div");
        avatarDiv.className = "avatar";
        avatarDiv.textContent = "🤖";
        
        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "message-bubble";
        
        let htmlContent = `<p>${data.message}</p>`;
        
        // 1. Emergency Case Render
        if (data.is_emergency) {
            htmlContent = `
                <div class="emergency-alert-card">
                    <div class="emergency-header">
                        <div class="emergency-icon">!</div>
                        <div class="emergency-title">Cảnh Báo Cấp Cứu</div>
                    </div>
                    <div class="emergency-body">
                        <p>${data.message}</p>
                        <div class="result-section-title">Khuyến cáo khẩn cấp:</div>
                        <ul class="warning-list" style="margin-bottom: 16px;">
                            ${data.warnings.map(w => `<li><strong>${w}</strong></li>`).join("")}
                            ${data.recommendations.map(r => `<li>${r}</li>`).join("")}
                        </ul>
                    </div>
                    <div class="emergency-actions">
                        <a href="tel:115" class="emergency-btn call-btn">
                            📞 Gọi Cấp Cứu 115
                        </a>
                        <a href="https://www.google.com/maps/search/bệnh+viện+gần+nhất" target="_blank" class="emergency-btn map-btn">
                            📍 Tìm Bệnh Viện Gần Nhất
                        </a>
                    </div>
                </div>
            `;
            addLog("rule", "HIỂN THỊ CẢNH BÁO CẤP CỨU MÀU ĐỎ (SAFETY GUARDRAIL).");
        } 
        // 2. Low Confidence / Ask for clarification
        else if (data.confidence === "low") {
            htmlContent += `
                <div class="diagnostic-container">
                    <div class="result-section-title">Vui lòng cung cấp thêm thông tin:</div>
                    <div class="hint-chips">
                        ${data.clarifying_questions.map(q => `
                            <button class="hint-chip" onclick="setInputValue('${q.replace('Bạn có ', 'Tôi bị ').replace('không?', '')}')">${q}</button>
                        `).join("")}
                    </div>
                </div>
            `;
            addLog("rule", "Nhận diện độ tin cậy thấp. Hiển thị các câu hỏi gợi ý làm rõ.");
        }
        // 3. Happy Path / Normal OTC Suggestion
        else {
            const symptomTags = data.symptoms.map(s => `<span class="symptom-tag safe-tag">${s}</span>`).join(" ");
            const adviceList = data.recommendations.map(r => `<li>${r}</li>`).join("");
            const warningList = data.warnings.map(w => `<li>${w}</li>`).join("");
            
            // Build products grid
            let productsGridHtml = "";
            if (data.products && data.products.length > 0) {
                productsGridHtml = `
                    <div class="result-section-title">Sản phẩm gợi ý tại nhà thuốc Long Châu:</div>
                    <div class="product-suggestions-grid">
                        ${data.products.map(p => `
                            <div class="product-card">
                                <div class="product-image-placeholder" style="background: ${p.image_gradient || 'var(--primary-gradient)'}">
                                    ${p.name}
                                </div>
                                <div class="product-details">
                                    <h4>${p.name}</h4>
                                    <div class="price">${p.price}</div>
                                    <div class="desc">${p.description}</div>
                                    <div class="usage">HDSD: ${p.usage}</div>
                                </div>
                                <button class="product-action-btn" onclick="alert('Đã thêm sản phẩm vào giỏ hàng tư vấn Long Châu!')">Chọn sản phẩm</button>
                            </div>
                        `).join("")}
                    </div>
                `;
            } else {
                productsGridHtml = `<p style="font-size: 0.85rem; color: var(--text-light); font-style: italic;">Không có sản phẩm OTC tự dùng trực tiếp cho triệu chứng này.</p>`;
            }

            htmlContent += `
                <div class="diagnostic-container">
                    <div class="result-section-title">Triệu chứng nhận diện:</div>
                    <div class="symptoms-tags">${symptomTags}</div>
                    
                    ${productsGridHtml}
                    
                    <div class="result-section-title">Lời khuyên chăm sóc ban đầu:</div>
                    <ul class="advice-list">
                        ${adviceList}
                    </ul>
                    
                    <div class="result-section-title">Cảnh báo an toàn:</div>
                    <ul class="warning-list">
                        ${warningList}
                    </ul>
                </div>
            `;
            addLog("database", `Đã trích xuất ${data.symptoms.length} triệu chứng và gợi ý ${data.products.length} sản phẩm.`);
        }
        
        bubbleDiv.innerHTML = htmlContent;
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        chatMessagesContainer.appendChild(messageDiv);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    // Append Typing Indicator
    function showTypingIndicator() {
        const indicatorDiv = document.createElement("div");
        indicatorDiv.className = "message system-message typing-indicator-wrapper";
        indicatorDiv.id = "typing-indicator-node";
        
        const avatarDiv = document.createElement("div");
        avatarDiv.className = "avatar";
        avatarDiv.textContent = "🤖";
        
        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "message-bubble";
        bubbleDiv.innerHTML = `
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;
        
        indicatorDiv.appendChild(avatarDiv);
        indicatorDiv.appendChild(bubbleDiv);
        chatMessagesContainer.appendChild(indicatorDiv);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        
        userInput.disabled = true;
        sendBtn.disabled = true;
    }

    function removeTypingIndicator() {
        const node = document.getElementById("typing-indicator-node");
        if (node) {
            node.remove();
        }
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }

    // Send Message core function
    async function sendMessage(text) {
        if (!text.trim()) return;
        
        appendMessage("user", text);
        addLog("input", `Gửi: "${text}"`);
        showTypingIndicator();
        
        const payload = {
            message: text,
            provider: aiProvider.value,
            api_key: apiKeyInput.value.trim() || null
        };
        
        addLog("api", `Đang gọi API endpoint /api/chat (${aiProvider.value.toUpperCase()})...`);
        
        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`Mã lỗi HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            
            addLog("api", `Phản hồi 200 OK. Confidence: "${data.confidence}", Emergency: ${data.is_emergency}`);
            
            removeTypingIndicator();
            appendDiagnosticMessage(data);
            
        } catch (error) {
            console.error("API Call failed:", error);
            removeTypingIndicator();
            addLog("error", `Lỗi gọi API: ${error.message}`);
            appendMessage("system", `⚠️ Rất tiếc, đã xảy ra lỗi kết nối với máy chủ AI: ${error.message}. Vui lòng kiểm tra lại dịch vụ backend.`);
        }
    }

    // Handle form submit
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (text) {
            sendMessage(text);
            userInput.value = "";
        }
    });

    window.setInputValue = function(value) {
        userInput.value = value;
        userInput.focus();
    };

    // --- PRESET SCENARIO TRIGGERS ---
    
    // Happy Path
    presetHappy.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p><strong>[DEMO: Happy Path]</strong> Đang giả lập triệu chứng ho khan và đau họng nhẹ.</p>
                </div>
            </div>
        `;
        userInput.value = "";
        sendMessage("Tôi bị ho khan, đau họng nhẹ, không sốt.");
    });

    // Low Confidence
    presetLowConf.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p><strong>[DEMO: Low Confidence]</strong> Đang giả lập triệu chứng quá mơ hồ để AI yêu cầu hỏi thêm.</p>
                </div>
            </div>
        `;
        userInput.value = "";
        sendMessage("Tôi thấy người không ổn.");
    });

    // Safety Case
    presetSafety.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p><strong>[DEMO: Safety Red-Flag Interceptor]</strong> Đang kiểm thử dấu hiệu khẩn cấp nguy hiểm.</p>
                </div>
            </div>
        `;
        userInput.value = "";
        sendMessage("Em bị đau ngực và khó thở nhiều quá bác sĩ ơi.");
    });

    // Correction Path
    presetCorrection.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p><strong>[DEMO: Correction Path]</strong> Bắt đầu bằng ho rát họng, sau đó cập nhật thêm dị ứng da nổi mẩn.</p>
                </div>
            </div>
        `;
        
        addLog("system", "Khởi động kịch bản Correction Path...");
        userInput.value = "";
        
        sendMessage("Tôi bị ho rát họng khó chịu");
        
        setTimeout(() => {
            userInput.value = "À tôi còn nổi mẩn đỏ dị ứng ngứa toàn thân nữa";
            addLog("system", "Auto-type: Người dùng bổ sung triệu chứng nổi mẩn ngứa.");
        }, 3500);
    });
});
