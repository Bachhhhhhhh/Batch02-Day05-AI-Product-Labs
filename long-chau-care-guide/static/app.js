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

    // Logger Elements
    const logConsole = document.getElementById("log-console");
    const clearLogsBtn = document.getElementById("clear-logs-btn");

    // Demo Preset Buttons
    const presetHappy = document.getElementById("preset-happy");
    const presetLowConf = document.getElementById("preset-low-conf");
    const presetSafety = document.getElementById("preset-safety");
    const presetCorrection = document.getElementById("preset-correction");

    // Load saved Provider from LocalStorage
    if (localStorage.getItem("longchau_api_provider")) {
        aiProvider.value = localStorage.getItem("longchau_api_provider");
    }

    aiProvider.addEventListener("change", () => {
        localStorage.setItem("longchau_api_provider", aiProvider.value);
    });

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

    // Custom Toast Notification
    window.showToast = function (message) {
        let toast = document.getElementById("toast-notification");
        if (!toast) {
            toast = document.createElement("div");
            toast.id = "toast-notification";
            toast.style.position = "fixed";
            toast.style.bottom = "24px";
            toast.style.right = "24px";
            toast.style.backgroundColor = "var(--primary-dark)";
            toast.style.color = "white";
            toast.style.padding = "14px 24px";
            toast.style.borderRadius = "8px";
            toast.style.boxShadow = "0 10px 25px rgba(0,0,0,0.2)";
            toast.style.zIndex = "10000";
            toast.style.fontSize = "0.95rem";
            toast.style.fontWeight = "500";
            toast.style.transition = "all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)";
            toast.style.transform = "translateY(100px)";
            toast.style.opacity = "0";
            document.body.appendChild(toast);
        }

        toast.innerHTML = `🛒 ${message}`;
        toast.style.display = "block";

        // Trigger animation
        setTimeout(() => {
            toast.style.transform = "translateY(0)";
            toast.style.opacity = "1";
        }, 10);

        // Hide after 3s
        setTimeout(() => {
            toast.style.transform = "translateY(20px)";
            toast.style.opacity = "0";
            setTimeout(() => {
                toast.style.display = "none";
            }, 300);
        }, 3000);
    };

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
            function isMeaningfulArray(arr) {
                if (!arr || !Array.isArray(arr) || arr.length === 0) return false;
                return arr.some(item => {
                    if (typeof item !== 'string') return true;
                    const text = item.trim().toLowerCase();
                    return text !== "" && text !== "none" && text !== "không" && text !== "không có" && text !== "n/a" && text !== "null";
                });
            }

            const hasSymptoms = isMeaningfulArray(data.symptoms);
            const hasCategories = isMeaningfulArray(data.categories);

            if (!hasSymptoms && !hasCategories) {
                // General conversation or out-of-scope response
                if (data.clarifying_questions && data.clarifying_questions.length > 0) {
                    htmlContent += `
                        <div class="diagnostic-container">
                            <div class="hint-chips" style="margin-top: 10px;">
                                ${data.clarifying_questions.map(q => `
                                    <button class="hint-chip" onclick="setInputValue('${q.replace('Bạn có ', 'Tôi bị ').replace('không?', '')}')">${q}</button>
                                `).join("")}
                            </div>
                        </div>
                    `;
                }
                addLog("rule", "Giao tiếp chung hoặc câu hỏi ngoài phạm vi y tế, chỉ hiển thị lời nhắn.");
            } else {
                const symptomTags = hasSymptoms
                    ? data.symptoms.filter(s => s && s.trim() !== "" && s.toLowerCase() !== "không có").map(s => `<span class="symptom-tag safe-tag">${s}</span>`).join(" ")
                    : "";

                let adviceList = "";
                if (isMeaningfulArray(data.recommendations)) {
                    adviceList = `
                        <div class="result-section-title">Lời khuyên chăm sóc ban đầu:</div>
                        <ul class="advice-list">
                            ${data.recommendations.filter(r => r && r.trim() !== "" && r.toLowerCase() !== "không có").map(r => `<li>${r}</li>`).join("")}
                        </ul>
                    `;
                }

                let warningList = "";
                if (isMeaningfulArray(data.warnings)) {
                    warningList = `
                        <div class="result-section-title">Cảnh báo an toàn:</div>
                        <ul class="warning-list">
                            ${data.warnings.filter(w => w && w.trim() !== "" && w.toLowerCase() !== "không có").map(w => `<li>${w}</li>`).join("")}
                        </ul>
                    `;
                }

                let referencesList = "";
                if (data.references && data.references.length > 0) {
                    referencesList = `
                        <div class="result-section-title" style="margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; font-size: 0.85rem;">
                            📚 Dữ liệu trích xuất từ:
                        </div>
                        <ul class="references-list" style="font-size: 0.85rem; color: var(--text-light); padding-left: 20px; margin-top: 5px; list-style-type: disc;">
                            ${data.references.map(ref => `<li><a href="${ref.url}" target="_blank" style="color: var(--primary-light); text-decoration: none;">${ref.name}</a></li>`).join("")}
                        </ul>
                    `;
                }

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
                                    <a href="https://nhathuoclongchau.com.vn/tim-kiem?s=${encodeURIComponent(p.name).replace(/%20/g, '+')}" target="_blank" class="product-action-btn" style="text-decoration: none; display: flex; align-items: center; justify-content: center;">Xem trên Long Châu</a>
                                </div>
                            `).join("")}
                        </div>
                    `;
                } else {
                    productsGridHtml = `<p style="font-size: 0.85rem; color: var(--text-light); font-style: italic;">Không có sản phẩm OTC tự dùng trực tiếp cho triệu chứng này.</p>`;
                }

                htmlContent += `
                    <div class="diagnostic-container">
                        ${symptomTags ? `<div class="result-section-title">Triệu chứng nhận diện:</div><div class="symptoms-tags">${symptomTags}</div>` : ''}
                        
                        ${productsGridHtml}
                        
                        ${adviceList}
                        
                        ${warningList}
                        
                        ${referencesList}
                    </div>
                `;
                addLog("database", `Đã trích xuất ${data.symptoms ? data.symptoms.length : 0} triệu chứng và gợi ý ${data.products ? data.products.length : 0} sản phẩm. Nguồn: ${data.references ? data.references.length : 0}.`);
            }
        }
        
        // Add Medical Disclaimer to all AI responses
        htmlContent += `
            <div class="medical-disclaimer" style="margin-top: 15px; padding-top: 10px; border-top: 1px dashed rgba(255,255,255,0.1); font-size: 0.8rem; color: #9ca3af; font-style: italic;">
                ⚠️ Lưu ý: Thông tin chỉ mang tính chất tham khảo, không thay thế chỉ định của Bác sĩ.
            </div>
        `;

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
            provider: aiProvider.value
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

    window.setInputValue = function (value) {
        userInput.value = value;
        userInput.focus();
    };

    // --- PRESET SCENARIO TRIGGERS ---

    // Happy Path
    presetHappy.addEventListener("click", () => {
        addLog("system", "Khởi động kịch bản Happy Path (Tương tác Thuốc-Thức ăn)...");
        userInput.value = "";
        sendMessage("Thuốc Paracetamol có uống cùng với cà phê được không bạn?");
    });

    // Low Confidence
    presetLowConf.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p>Xin chào! Tôi là <strong>Long Châu Care Guide</strong> - Trợ lý AI hỗ trợ tìm kiếm sản phẩm chăm sóc sức khỏe.</p>
                </div>
            </div>
        `;
        
        addLog("system", "Khởi động kịch bản Low Confidence (Thuốc không có thật)...");
        userInput.value = "";
        sendMessage("Thuốc XZ-999 trị bệnh gì vậy?");
    });

    // Safety Case (Failure Mode)
    presetSafety.addEventListener("click", () => {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar">🤖</div>
                <div class="message-bubble">
                    <p>Xin chào! Tôi là <strong>Long Châu Care Guide</strong> - Trợ lý AI hỗ trợ tìm kiếm sản phẩm chăm sóc sức khỏe.</p>
                </div>
            </div>
        `;
        
        addLog("system", "Khởi động kịch bản Failure Mode (Hỏi liều lượng)...");
        userInput.value = "";
        sendMessage("Mình đang bị sốt cao, ngày uống 10 viên Panadol Extra được không?");
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
