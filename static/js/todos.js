/**
 * Todo 相关功能
 */

function fetchTodos() {
  // 按日期筛选todos
  fetch(CONFIG.API_BASE + "?date=" + currentDate)
    .then((r) => r.json())
    .then((data) => {
      const list = document.getElementById("todo-list");
      list.innerHTML = "";
      data.reverse(); // 新增的 todo 显示在最上面
      data.forEach((todo, idx) => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        let contentClass = "flex-grow-1 todo-content";
        if (todo.completed) contentClass += " todo-completed";
        li.innerHTML = `
          <span class="${contentClass}" ondblclick="toggleComplete(${
          todo.id
        })" id="content-${todo.id}">${todo.content}</span>
          <span class="todo-dates">${
            todo.completed
              ? "完成: " + formatDate(todo.completed_at)
              : "创建: " + formatDate(todo.created_at)
          }</span>
          <div class="todo-actions">
              <button class="btn btn-sm btn-outline-secondary" onclick="copyTodoContent(${
                todo.id
              }, this)">复制</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="editTodo(${
                todo.id
              })">修改</button>
              <button class="btn btn-sm btn-outline-danger" onclick="deleteTodo(${
                todo.id
              })">删除</button>
          </div>
        `;
        li.style.display = "flex";
        li.style.alignItems = "flex-start";
        list.appendChild(li);
      });

      // 更新计数
      updateTodoCounts();
    });
}

function toggleComplete(id) {
  fetch(CONFIG.API_BASE + "/" + id + "?date=" + currentDate, { method: "GET" })
    .then((r) => r.json())
    .then((todo) => {
      const completed = !todo.completed;
      fetch(CONFIG.API_BASE + "/" + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          completed,
          date: currentDate,
        }),
      }).then(fetchTodos);
    });
}

function editTodo(id) {
  const span = document.getElementById("content-" + id);
  const old = span.textContent;
  const textarea = document.createElement("textarea");
  textarea.value = old;
  textarea.className = "form-control d-inline";
  textarea.style.marginRight = "8px";
  textarea.style.flex = "1 1 0%";
  textarea.style.marginLeft = "0";
  textarea.style.resize = "vertical";
  textarea.style.minHeight = "38px";
  textarea.rows = 1;

  span.replaceWith(textarea);

  // 设置textarea功能
  setupTextarea(textarea);
  textarea.focus();

  // 选中所有文本
  textarea.select();

  textarea.onblur = function () {
    fetch(CONFIG.API_BASE + "/" + id, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: textarea.value,
        date: currentDate,
      }),
    }).then(fetchTodos);
  };

  // 重写键盘事件处理，支持Shift+Enter换行，Enter保存
  textarea.onkeydown = function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      textarea.blur();
    }
    if (e.key === "Escape") {
      e.preventDefault();
      fetchTodos(); // 取消编辑，重新加载
    }
  };
}

function deleteTodo(id) {
  fetch(CONFIG.API_BASE + "/" + id + "?date=" + currentDate, {
    method: "DELETE",
  }).then(fetchTodos);
}

function copyTodo(id) {
  fetch(CONFIG.API_BASE + "/" + id + "/copy?date=" + currentDate, {
    method: "POST",
  }).then(fetchTodos);
}

function moveTodo(id, newOrder) {
  fetch(CONFIG.API_BASE)
    .then((r) => r.json())
    .then((data) => {
      if (newOrder < 0 || newOrder >= data.length) return;
      fetch(CONFIG.API_BASE + "/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id, order: newOrder }),
      }).then(fetchTodos);
    });
}

// 复制todo内容到剪贴板
function copyTodoContent(id, buttonElement) {
  const contentElement = document.getElementById("content-" + id);
  const todoContent = contentElement.textContent;

  // 使用现代剪贴板API
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard
      .writeText(todoContent)
      .then(() => {
        showCopySuccess(buttonElement);
      })
      .catch(() => {
        // 如果现代API失败，使用传统方法
        fallbackCopyTextToClipboard(todoContent, buttonElement);
      });
  } else {
    // 使用传统方法
    fallbackCopyTextToClipboard(todoContent, buttonElement);
  }
}

function exportCurrentDate() {
  window.open(CONFIG.API_BASE + "/export/" + currentDate, "_blank");
}
