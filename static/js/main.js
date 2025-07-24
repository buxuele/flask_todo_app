/**
 * 主应用初始化和事件绑定
 */

// 表单提交事件
document.getElementById("add-form").onsubmit = function (e) {
  e.preventDefault();
  const content = document.getElementById("new-todo").value.trim();
  if (!content) return;
  fetch(CONFIG.API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, date: currentDate }),
  }).then(() => {
    document.getElementById("new-todo").value = "";
    fetchTodos();
  });
};

// 点击其他地方隐藏右键菜单
document.addEventListener("click", function () {
  document.getElementById("context-menu").style.display = "none";
});

// 支持回车键搜索
document
  .getElementById("search-input")
  .addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      searchTodos();
    }
  });

// 初始化新任务输入框
const newTodoTextarea = document.getElementById("new-todo");
setupTextarea(newTodoTextarea);

// 应用初始化
function initApp() {
  // 生成日期列表
  generateDateList();

  // 设置初始标题
  const title = document.getElementById("current-date-title");
  title.textContent = `${formatDateForDisplay(currentDate)} Todo`;

  // 加载当前日期的todos
  fetchTodos();
}

// 页面加载完成后初始化
document.addEventListener("DOMContentLoaded", function () {
  initApp();
});
