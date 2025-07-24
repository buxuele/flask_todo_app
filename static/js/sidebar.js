/**
 * 侧边栏相关功能
 */

function generateDateList() {
  const dateList = document.getElementById("date-list");
  dateList.innerHTML = "";

  // 获取所有有数据的日期（包括用户创建的副本）
  fetch(CONFIG.API_BASE + "/counts")
    .then((r) => r.json())
    .then((counts) => {
      // 获取所有有数据的日期
      const allDates = Object.keys(counts);

      // 只添加今天的日期（如果不存在的话），其他日期只有在有数据时才显示
      const today = new Date().toISOString().split("T")[0];
      if (!allDates.includes(today)) {
        allDates.push(today);
      }

      // 按日期排序（最新在前）
      allDates.sort((a, b) => new Date(b) - new Date(a));

      // 获取日期别名
      return fetch(CONFIG.API_BASE.replace("/todos", "/date-aliases"))
        .then((r) => r.json())
        .then((aliases) => {
          allDates.forEach((dateStr) => {
            const li = document.createElement("li");
            li.className = "date-item";
            if (dateStr === currentDate) {
              li.classList.add("active");
            }

            // 始终使用具体日期显示，不使用别名
            const displayName = formatDateForDisplay(dateStr);

            li.innerHTML = `
              <span class="date-name">${displayName}</span>
            `;

            // 添加数据属性以便准确识别
            li.dataset.date = dateStr;

            li.onclick = () => switchDate(dateStr);

            // 添加右键菜单事件
            addContextMenuToDateItem(li, dateStr);

            dateList.appendChild(li);
          });

          updateTodoCounts();
        });
    })
    .catch((error) => {
      console.error("获取日期列表失败:", error);
      // 如果获取失败，使用默认的7天显示
      const dates = [];
      const baseDate = new Date();
      for (let i = 0; i >= -7; i--) {
        const date = new Date(baseDate);
        date.setDate(baseDate.getDate() + i);
        dates.push(date.toISOString().split("T")[0]);
      }

      dates.forEach((dateStr) => {
        const li = document.createElement("li");
        li.className = "date-item";
        if (dateStr === currentDate) {
          li.classList.add("active");
        }

        li.innerHTML = `
          <span class="date-name">${formatDateForDisplay(dateStr)}</span>
        `;

        li.dataset.date = dateStr;
        li.onclick = () => switchDate(dateStr);
        addContextMenuToDateItem(li, dateStr);
        dateList.appendChild(li);
      });

      updateTodoCounts();
    });
}

function switchDate(dateStr) {
  currentDate = dateStr;

  // 更新侧边栏选中状态
  document.querySelectorAll(".date-item").forEach((item) => {
    item.classList.remove("active");
  });

  // 找到对应的日期项并设置为活跃状态
  document.querySelectorAll(".date-item").forEach((item) => {
    if (item.dataset.date === dateStr) {
      item.classList.add("active");
    }
  });

  // 更新标题
  const title = document.getElementById("current-date-title");
  title.textContent = `${formatDateForDisplay(dateStr)} Todo`;

  // 重新加载该日期的todos
  fetchTodos();
}

function updateTodoCounts() {
  // 不再需要显示计数，保留函数以免其他地方调用出错
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const icon = document.getElementById("collapse-icon");
  const mainContent = document.querySelector(".main-content");

  sidebar.classList.toggle("collapsed");

  if (sidebar.classList.contains("collapsed")) {
    icon.textContent = "▶";
    mainContent.style.marginLeft = "0";
  } else {
    icon.textContent = "◀";
    mainContent.style.marginLeft = "0";
  }
}
