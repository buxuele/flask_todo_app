/**
 * 工具函数
 */

function formatDate(dt) {
  if (!dt) return "";
  const d = new Date(dt);
  if (isNaN(d)) return "";
  // 直接使用本地时间格式化
  return d.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatDateForDisplay(dateStr) {
  // 避免时区问题，直接解析日期字符串
  const [year, month, day] = dateStr.split("-");
  const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

  // 始终显示具体的月日，不使用相对时间
  return date.toLocaleDateString("zh-CN", {
    month: "long",
    day: "numeric",
  });
}

// 处理textarea的自动调整高度和Shift+Enter换行
function setupTextarea(textarea) {
  // 自动调整高度
  function adjustHeight() {
    textarea.style.height = "auto";
    textarea.style.height = Math.max(38, textarea.scrollHeight) + "px";
  }

  textarea.addEventListener("input", adjustHeight);

  // 处理键盘事件
  textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (textarea.form) {
        textarea.form.dispatchEvent(new Event("submit"));
      }
    }
  });

  // 初始调整
  adjustHeight();
}

// 传统的复制方法（兼容性更好）
function fallbackCopyTextToClipboard(text, buttonElement) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  textArea.style.top = "-999999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const successful = document.execCommand("copy");
    if (successful) {
      showCopySuccess(buttonElement);
    } else {
      console.error("复制失败");
    }
  } catch (err) {
    console.error("复制失败:", err);
  }

  document.body.removeChild(textArea);
}

// 显示复制成功状态
function showCopySuccess(buttonElement) {
  const originalText = buttonElement.textContent;
  buttonElement.textContent = "已复制";
  buttonElement.classList.remove("btn-outline-secondary");
  buttonElement.classList.add("btn-success");

  // 2秒后恢复原状
  setTimeout(() => {
    buttonElement.textContent = originalText;
    buttonElement.classList.remove("btn-success");
    buttonElement.classList.add("btn-outline-secondary");
  }, 2000);
}
