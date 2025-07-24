/**
 * 搜索相关功能
 */

function searchTodos() {
  const searchTerm = document.getElementById("search-input").value.trim();
  if (!searchTerm) {
    alert("请输入搜索关键词");
    return;
  }

  isSearchMode = true;
  document.getElementById("clear-search-btn").style.display = "inline-block";

  // 获取所有日期的todos进行搜索
  fetchAllTodos().then(() => {
    const filteredTodos = allTodos.filter((todo) =>
      todo.content.toLowerCase().includes(searchTerm.toLowerCase())
    );

    displaySearchResults(filteredTodos, searchTerm);
  });
}

function clearSearch() {
  isSearchMode = false;
  document.getElementById("search-input").value = "";
  document.getElementById("clear-search-btn").style.display = "none";

  // 恢复当前日期的显示
  const title = document.getElementById("current-date-title");
  title.textContent = `${formatDateForDisplay(currentDate)} Todo`;

  fetchTodos();
}

function fetchAllTodos() {
  // 获取所有日期的todos
  return fetch(CONFIG.API_BASE + "/counts")
    .then((r) => r.json())
    .then((counts) => {
      const promises = Object.keys(counts).map((date) =>
        fetch(CONFIG.API_BASE + "?date=" + date).then((r) => r.json())
      );

      return Promise.all(promises).then((results) => {
        allTodos = results.flat();
      });
    });
}

function displaySearchResults(filteredTodos, searchTerm) {
  const list = document.getElementById("todo-list");
  const title = document.getElementById("current-date-title");

  title.textContent = `搜索结果: "${searchTerm}" (${filteredTodos.length}条)`;

  list.innerHTML = "";

  if (filteredTodos.length === 0) {
    list.innerHTML =
      '<li class="list-group-item text-center text-muted">未找到匹配的任务</li>';
    return;
  }

  filteredTodos.forEach((todo) => {
    const li = document.createElement("li");
    li.className = "list-group-item";
    let contentClass = "flex-grow-1 todo-content";
    if (todo.completed) contentClass += " todo-completed";

    // 高亮搜索关键词
    const highlightedContent = todo.content.replace(
      new RegExp(searchTerm, "gi"),
      `<mark>${searchTerm}</mark>`
    );

    li.innerHTML = `
      <span class="${contentClass}" ondblclick="toggleComplete(${
      todo.id
    })" id="content-${todo.id}">${highlightedContent}</span>
      <span class="todo-dates">${formatDateForDisplay(todo.date)} | ${
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
}
