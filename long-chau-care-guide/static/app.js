// Frontend logic for Long Chau Care Guide prescription explainer.

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessagesContainer = document.getElementById("chat-messages-container");
    const sendBtn = document.getElementById("send-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");
    const aiProvider = document.getElementById("ai-provider");
    const logConsole = document.getElementById("log-console");
    const clearLogsBtn = document.getElementById("clear-logs-btn");

    const presetHappy = document.getElementById("preset-happy");
    const presetLowConf = document.getElementById("preset-low-conf");
    const presetSafety = document.getElementById("preset-safety");
    const presetCorrection = document.getElementById("preset-correction");
    const presetCombinedFull = document.getElementById("preset-combined-full");
    const presetCombinedMissing = document.getElementById("preset-combined-missing");

    let chatHistory = [];

    const savedProvider = localStorage.getItem("longchau_api_provider");
    aiProvider.value = savedProvider === "openai" ? "openai" : "gemini";
    localStorage.setItem("longchau_api_provider", aiProvider.value);

    aiProvider.addEventListener("change", () => {
        localStorage.setItem("longchau_api_provider", aiProvider.value);
    });

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function addLog(type, message) {
        const timestamp = new Date().toLocaleTimeString("vi-VN");
        const logLine = document.createElement("div");
        logLine.className = `log-line ${type}`;
        logLine.textContent = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
        logConsole.appendChild(logLine);
        logConsole.scrollTop = logConsole.scrollHeight;
    }

    function isMeaningfulArray(arr) {
        if (!Array.isArray(arr) || arr.length === 0) return false;
        return arr.some((item) => {
            const text = String(item ?? "").trim().toLowerCase();
            return text && !["none", "không", "không có", "n/a", "null"].includes(text);
        });
    }

    function resetWelcome(message = "Lịch sử trò chuyện đã được làm mới. Mình sẵn sàng giải thích đơn thuốc hoặc tên thuốc.") {
        chatMessagesContainer.innerHTML = `
            <div class="message system-message">
                <div class="avatar" aria-hidden="true">AI</div>
                <div class="message-bubble">
                    <p>${escapeHtml(message)}</p>
                </div>
            </div>
        `;
    }

    clearLogsBtn.addEventListener("click", () => {
        logConsole.innerHTML = '<div class="log-line system">[System] Logs cleared.</div>';
    });

    clearChatBtn.addEventListener("click", () => {
        chatHistory = [];
        resetWelcome();
        addLog("system", "Conversation reset.");
    });

    function appendMessage(sender, content) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;

        const avatarDiv = document.createElement("div");
        avatarDiv.className = "avatar";
        avatarDiv.textContent = sender === "user" ? "You" : "AI";

        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "message-bubble";
        bubbleDiv.innerHTML = content;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        chatMessagesContainer.appendChild(messageDiv);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        return messageDiv;
    }

    function createReportButton(data) {
        const reportBtn = document.createElement("button");
        reportBtn.className = "report-btn";
        reportBtn.type = "button";
        reportBtn.title = "Báo cáo vấn đề";
        reportBtn.textContent = "Report";
        reportBtn.onclick = () => window.openReportModal(data.message || "No message content");
        return reportBtn;
    }

    function renderMarkdown(markdown) {
        if (window.marked) {
            return marked.parse(markdown);
        }
        return escapeHtml(markdown).replace(/\n/g, "<br>");
    }

    function buildLongTextControls() {
        return `
            <div class="action-row">
                <button class="content-toggle" type="button" data-action="summary">Tóm tắt nội dung dài</button>
                <button class="content-toggle" type="button" data-action="full">Xem đầy đủ</button>
            </div>
        `;
    }

    function summarizeMarkdownTable(markdown) {
        const lines = markdown.split("\n").filter((line) => line.trim().startsWith("|"));
        if (lines.length < 3) return "";

        const rows = lines.slice(2).map((line) => line
            .split("|")
            .slice(1, -1)
            .map((cell) => cell.replace(/\*\*/g, "").replace(/\s+/g, " ").trim()));

        const items = rows.map((cells) => {
            const [drug, use, sourceUsage, safety, sideEffects, source] = cells;
            return `
                <div class="summary-card">
                    <h4>${escapeHtml(drug || "Thuốc")}</h4>
                    <p><strong>Dùng để làm gì:</strong> ${escapeHtml(shortenSentence(use))}</p>
                    <p><strong>Cách dùng:</strong> ${escapeHtml(shortenSentence(sourceUsage))}</p>
                    <p><strong>Lưu ý:</strong> ${escapeHtml(shortenSentence(safety || sideEffects || source))}</p>
                </div>
            `;
        }).join("");

        return `<div class="summary-grid">${items}</div>`;
    }

    function shortenSentence(text) {
        const clean = String(text || "").replace(/\s+/g, " ").trim();
        if (!clean) return "Chưa có dữ liệu trong database demo.";
        const withoutLongChauPrefix = clean
            .replace(/^Trước khi sử dụng thuốc bạn cần đọc kỹ hướng dẫn sử dụng và tham khảo thông tin bên dưới\.?\s*/i, "")
            .replace(/^Thông báo cho thầy thuốc các tác dụng không mong muốn gặp phải khi sử dụng thuốc\.?\s*/i, "");
        const clauses = withoutLongChauPrefix
            .split(/(?<=[.!?。])\s+|;\s+|\.\s*Chống chỉ định\s+/i)
            .map((part) => part.trim())
            .filter(Boolean);
        const firstMeaningful = clauses.find((part) => part.length >= 18) || clauses[0] || withoutLongChauPrefix;
        const words = firstMeaningful.split(" ");
        if (words.length <= 32) return firstMeaningful;
        return `${words.slice(0, 32).join(" ")}. Xem đầy đủ để đọc toàn bộ chi tiết.`;
    }

    function attachContentToggles(wrapper, markdown) {
        const markdownNode = wrapper.querySelector(".markdown-content");
        const summaryHtml = summarizeMarkdownTable(markdown);
        if (!markdownNode || !summaryHtml) return;

        wrapper.querySelectorAll("[data-action]").forEach((button) => {
            button.addEventListener("click", () => {
                if (button.dataset.action === "summary") {
                    markdownNode.innerHTML = summaryHtml;
                    addLog("rule", "Rendered semantic summary for long prescription output.");
                } else {
                    markdownNode.innerHTML = renderMarkdown(markdown);
                    addLog("rule", "Rendered full prescription output.");
                }
            });
        });
    }

    function appendDiagnosticMessage(data) {
        const messageDiv = document.createElement("div");
        messageDiv.className = "message system-message";

        const avatarDiv = document.createElement("div");
        avatarDiv.className = "avatar";
        avatarDiv.textContent = "AI";

        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "message-bubble";

        const message = escapeHtml(data.message || "");
        const prescriptionMarkdown = String(data.prescription_explanation || "").trim();
        const hasPrescription = Boolean(prescriptionMarkdown);

        let htmlContent = `<p>${message}</p>`;

        if (data.is_emergency) {
            htmlContent = `
                <div class="emergency-alert-card">
                    <div class="result-section-title">Cảnh báo khẩn cấp</div>
                    <p>${message}</p>
                    ${renderList(data.warnings, "warning-list")}
                    ${renderList(data.recommendations, "advice-list")}
                </div>
            `;
            addLog("rule", "Emergency guardrail response rendered.");
        } else if (hasPrescription) {
            htmlContent += `
                <div class="diagnostic-container">
                    <div class="prescription-explanation">
                        <div class="result-section-title">Bảng giải thích đơn thuốc</div>
                        <div class="markdown-content">${renderMarkdown(prescriptionMarkdown)}</div>
                        ${buildLongTextControls()}
                    </div>
                    ${renderCombinedEffect(data.combined_effect)}
                    ${renderSectionList("Tác dụng phụ cần chú ý", data.side_effects, "side-effects-list")}
                    ${renderSectionList("Cảnh báo an toàn", data.warnings, "warning-list")}
                </div>
            `;
            addLog("database", "Prescription explanation rendered from matched medicine data.");
        } else if (data.confidence === "low") {
            htmlContent += `
                <div class="diagnostic-container">
                    <div class="notice-card warning">
                        <strong>Vui lòng cung cấp thêm thông tin</strong>
                        <p>Nhập tên thuốc cụ thể trong đơn hoặc dán nguyên đơn thuốc. Nếu hỏi theo triệu chứng, hệ thống sẽ không kê đơn hoặc đề xuất thuốc mới.</p>
                    </div>
                    ${renderClarifyingQuestions(data.clarifying_questions)}
                </div>
            `;
            addLog("rule", "Low confidence response rendered without suggesting replacement medicine.");
        } else {
            htmlContent += `
                <div class="diagnostic-container">
                    ${renderSectionList("Lưu ý", data.recommendations, "advice-list")}
                    ${renderSectionList("Cảnh báo an toàn", data.warnings, "warning-list")}
                </div>
            `;
            addLog("rule", "General safety response rendered.");
        }

        htmlContent += `
            <div class="medical-disclaimer">
                Lưu ý: Thông tin chỉ mang tính tham khảo để hiểu đơn thuốc, không thay thế chỉ định của bác sĩ hoặc tư vấn trực tiếp từ dược sĩ.
            </div>
        `;

        bubbleDiv.innerHTML = htmlContent;
        bubbleDiv.appendChild(createReportButton(data));
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        chatMessagesContainer.appendChild(messageDiv);
        attachContentToggles(bubbleDiv, prescriptionMarkdown);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    function renderList(items, className) {
        if (!isMeaningfulArray(items)) return "";
        return `<ul class="${className}">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
    }

    function renderSectionList(title, items, className) {
        if (!isMeaningfulArray(items)) return "";
        return `
            <div class="notice-card">
                <div class="result-section-title">${escapeHtml(title)}</div>
                ${renderList(items, className)}
            </div>
        `;
    }

    function renderCombinedEffect(text) {
        if (!text || !String(text).trim()) return "";
        return `
            <div class="combined-effect-section">
                <strong>Tác dụng kết hợp</strong>
                <p>${escapeHtml(text).replace(/\n/g, "<br>")}</p>
            </div>
        `;
    }

    function renderClarifyingQuestions(questions) {
        if (!isMeaningfulArray(questions)) return "";
        return `
            <div class="hint-chips">
                ${questions.map((q) => `<button class="hint-chip" type="button" onclick="setInputValue('${escapeHtml(q)}')">${escapeHtml(q)}</button>`).join("")}
            </div>
        `;
    }

    function showTypingIndicator() {
        const indicatorDiv = document.createElement("div");
        indicatorDiv.className = "message system-message typing-indicator-wrapper";
        indicatorDiv.id = "typing-indicator-node";

        const avatarDiv = document.createElement("div");
        avatarDiv.className = "avatar";
        avatarDiv.textContent = "AI";

        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = "message-bubble";
        bubbleDiv.innerHTML = `
            <div class="typing-indicator">
                <span class="typing-line"></span>
                <span class="typing-line"></span>
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
        if (node) node.remove();
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }

    async function sendMessage(text) {
        if (!text.trim()) return;

        appendMessage("user", escapeHtml(text));
        addLog("input", `Sent ${text.length} chars.`);
        showTypingIndicator();

        const payload = {
            message: text,
            provider: aiProvider.value,
            chat_history: chatHistory
        };

        chatHistory.push({ role: "user", content: text });
        addLog("api", `Calling /api/chat with ${aiProvider.value}.`);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            chatHistory.push({ role: "assistant", content: data.message });

            addLog("api", `Response OK. Confidence=${data.confidence}; prescription=${Boolean(data.prescription_explanation)}.`);
            removeTypingIndicator();
            appendDiagnosticMessage(data);
        } catch (error) {
            console.error("API call failed:", error);
            removeTypingIndicator();
            addLog("error", error.message);
            appendMessage("system", `<p>Không kết nối được backend: ${escapeHtml(error.message)}. Kiểm tra lại server rồi thử lại.</p>`);
        }
    }

    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;
        userInput.value = "";
        sendMessage(text);
    });

    window.setInputValue = function(value) {
        userInput.value = value;
        userInput.focus();
    };

    presetHappy.addEventListener("click", () => {
        sendMessage("Allopurinol");
    });

    presetLowConf.addEventListener("click", () => {
        sendMessage("bác sĩ kê đơn thuốc Azopt Alcon cho tôi thì nên lưu ý những điều gì");
    });

    presetSafety.addEventListener("click", () => {
        sendMessage("tôi bị gout nên uống thuốc gì");
    });

    presetCorrection.addEventListener("click", () => {
        sendMessage("1. CEFUROXIM 500MG ngày uống 2 lần. 2. BROMHEXIN 8MG ngày uống 3 lần. 3. PARACETAMOL 500MG + CAFFEINE 65MG ngày uống 3 lần.");
    });

    presetCombinedFull.addEventListener("click", () => {
        sendMessage("Azopt Alcon");
    });

    presetCombinedMissing.addEventListener("click", () => {
        sendMessage("Thuốc Tiên Khí Xanh 500mg trong đơn của tôi dùng để làm gì?");
    });
});

window.currentReportMessage = "";

window.openReportModal = function(msg) {
    window.currentReportMessage = msg;
    document.getElementById("report-feedback").value = "";
    document.getElementById("report-status").textContent = "";
    document.getElementById("report-modal").hidden = false;
};

window.closeReportModal = function() {
    document.getElementById("report-modal").hidden = true;
};

window.submitReport = async function() {
    const feedback = document.getElementById("report-feedback").value.trim();
    const status = document.getElementById("report-status");
    const reportBtn = document.querySelector(".modal-actions .primary-btn");

    if (!feedback) {
        status.textContent = "Vui lòng nhập lý do báo cáo.";
        return;
    }

    const originalText = reportBtn.textContent;
    reportBtn.textContent = "Đang gửi...";
    reportBtn.disabled = true;

    try {
        const response = await fetch("/api/report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: window.currentReportMessage,
                user_feedback: feedback
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        status.textContent = "Đã ghi nhận báo cáo. Cảm ơn bạn.";
        setTimeout(() => window.closeReportModal(), 900);
    } catch (error) {
        status.textContent = `Không gửi được báo cáo: ${error.message}`;
    } finally {
        reportBtn.textContent = originalText;
        reportBtn.disabled = false;
    }
};
