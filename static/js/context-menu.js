/**
 * 右键菜单相关功能
 */

// 为日期列表项添加右键菜单事件
function addContextMenuToDateItem(li, dateStr) {
  li.addEventListener("contextmenu", function (e) {
    e.preventDefault();
    rightClickedDate = dateStr;

    // 更新置顶菜单项的文本
    const pinMenuItem = document.getElementById("pin-menu-item");
    if (pinnedDates.has(dateStr)) {
      pinMenuItem.textContent = "取消置顶";
    } else {
      pinMenuItem.textContent = "置顶";
    }

    const contextMenu = document.getElementById("context-menu");
    contextMenu.style.display = "block";
    contextMenu.style.left = e.pageX + "px";
    contextMenu.style.top = e.pageY + "px";
  });
}

// 复制日期列表功能 - 创建新的独立日期副本，使用唯一标识符避免冲突
function copyDateList() {
  if (!rightClickedDate) return;

  // 获取当前显示的名称（可能是别名）
  const currentDisplayName = document.querySelector(
    `[data-date="${rightClickedDate}"] .date-name`
  ).textContent;

  // 生成唯一的复制标识符：使用时间戳确保唯一性
  const timestamp = Date.now();
  const copyName = currentDisplayName + "-copy";

  // 生成一个基于时间戳的唯一"日期"标识符
  // 格式：copy-YYYYMMDD-timestamp，确保不会与真实日期冲突
  const today = new Date();
  const datePrefix =
    today.getFullYear() +
    String(today.getMonth() + 1).padStart(2, "0") +
    String(today.getDate()).padStart(2, "0");
  const uniqueId = `copy-${datePrefix}-${timestamp}`;

  console.log(
    `复制日期列表: ${rightClickedDate} (${currentDisplayName}) -> ${copyName} (ID: ${uniqueId})`
  );

  // 1. 复制任务到新的唯一标识符
  fetch(CONFIG.API_BASE + "/copy-date", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_date: rightClickedDate,
      target_date: uniqueId,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`复制任务失败: HTTP ${response.status}`);
      }
    })
    .then((result) => {
      if (result.error) {
        throw new Error(result.error);
      }
      console.log(`任务复制成功: ${result.message}`);
      return uniqueId;
    })
    .then((newId) => {
      // 2. 为新ID设置别名 - 显示为原始名称加上-copy
      return fetch(CONFIG.API_BASE.replace("/todos", "/date-aliases"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date: newId,
          alias: copyName,
        }),
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error(`设置别名失败: HTTP ${response.status}`);
          }
        })
        .then((result) => {
          if (result.error) {
            throw new Error(result.error);
          }
          console.log(`别名设置成功: ${copyName}`);
          return newId;
        });
    })
    .then((newId) => {
      // 3. 刷新日期列表显示新的副本
      generateDateList();

      // 4. 显示成功提示
      showNotification(
        `已复制 "${currentDisplayName}" 为 "${copyName}"`,
        "success",
        "复制成功"
      );

      // 5. 切换到新创建的副本
      setTimeout(() => {
        switchDate(newId);
        console.log(`复制完成，已切换到新ID: ${newId}`);
      }, 500); // 延迟一点确保列表已刷新
    })
    .catch((error) => {
      showNotification("复制失败: " + error.message, "error", "复制失败");
      console.error("复制任务失败:", error);
    });

  document.getElementById("context-menu").style.display = "none";
}

// 重命名日期列表功能 - 设置日期别名
function renameDateList() {
  if (!rightClickedDate) return;

  // 获取当前显示的名称（可能是别名）
  const currentDisplayName = document.querySelector(
    `[data-date="${rightClickedDate}"] .date-name`
  ).textContent;
  const newName = prompt(`请输入新的名称:`, currentDisplayName);

  if (!newName || newName.trim() === "") {
    document.getElementById("context-menu").style.display = "none";
    return;
  }

  console.log(`重命名日期 ${rightClickedDate} 为: ${newName.trim()}`);

  // 调用API设置日期别名
  fetch(CONFIG.API_BASE.replace("/todos", "/date-aliases"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      date: rightClickedDate,
      alias: newName.trim(),
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    })
    .then((result) => {
      if (result.error) {
        showNotification("重命名失败: " + result.error, "error", "重命名失败");
      } else {
        console.log("重命名成功:", result.message);
        // 重新生成日期列表以显示新别名
        generateDateList();
        // 显示成功提示
        showNotification(
          `已重命名为 "${newName.trim()}"`,
          "success",
          "重命名成功"
        );
      }
    })
    .catch((error) => {
      showNotification("重命名失败: " + error.message, "error", "重命名失败");
      console.error("设置日期别名失败:", error);
    });

  document.getElementById("context-menu").style.display = "none";
}

// 删除日期列表功能
function deleteDateList() {
  if (!rightClickedDate) return;

  const displayName = document.querySelector(
    `[data-date="${rightClickedDate}"] .date-name`
  ).textContent;

  if (!confirm(`确定要删除 "${displayName}" 的所有任务吗？此操作不可恢复！`)) {
    document.getElementById("context-menu").style.display = "none";
    return;
  }

  // 使用新的批量删除API
  fetch(CONFIG.API_BASE + "/date/" + rightClickedDate, { method: "DELETE" })
    .then((response) => {
      console.log("删除响应状态:", response.status, response.statusText);
      console.log("响应是否OK:", response.ok);

      if (response.ok) {
        return response.json();
      } else {
        // 记录详细的错误信息
        return response.text().then((text) => {
          console.error("删除失败响应内容:", text);
          throw new Error(
            `删除失败: ${response.status} ${response.statusText} - ${text}`
          );
        });
      }
    })
    .then((result) => {
      console.log("删除成功响应:", result);

      // 删除成功后，刷新日期列表（让被删除的日期从左侧消失）
      generateDateList();

      // 如果删除的是当前日期，切换到今天
      if (rightClickedDate === currentDate) {
        const today = new Date().toISOString().split("T")[0];
        switchDate(today);
      }

      // 显示删除成功提示
      showNotification(
        `已删除 "${displayName}" 的所有任务`,
        "success",
        "删除成功"
      );
      console.log("删除成功:", result.message);
    })
    .catch((error) => {
      console.error("删除任务失败详细信息:", error);
      showNotification("删除失败: " + error.message, "error", "删除失败");
    });

  document.getElementById("context-menu").style.display = "none";
}
// 置顶/取消置顶日期列表功能
function togglePinDateList() {
  if (!rightClickedDate) return;

  const displayName = document.querySelector(
    `[data-date="${rightClickedDate}"] .date-name`
  ).textContent;

  if (pinnedDates.has(rightClickedDate)) {
    // 取消置顶
    pinnedDates.delete(rightClickedDate);
    showNotification(`已取消置顶 "${displayName}"`, "success", "取消置顶");
    console.log(`取消置顶日期: ${rightClickedDate}`);
  } else {
    // 置顶
    pinnedDates.add(rightClickedDate);
    showNotification(`已置顶 "${displayName}"`, "success", "置顶成功");
    console.log(`置顶日期: ${rightClickedDate}`);
  }

  // 保存置顶状态到本地存储
  savePinnedDates();

  // 重新生成日期列表以反映置顶状态
  generateDateList();

  document.getElementById("context-menu").style.display = "none";
}

// 保存置顶状态到本地存储
function savePinnedDates() {
  try {
    localStorage.setItem("pinnedDates", JSON.stringify([...pinnedDates]));
  } catch (error) {
    console.error("保存置顶状态失败:", error);
  }
}

// 从本地存储加载置顶状态
function loadPinnedDates() {
  try {
    const saved = localStorage.getItem("pinnedDates");
    if (saved) {
      const dates = JSON.parse(saved);
      pinnedDates = new Set(dates);
    }
  } catch (error) {
    console.error("加载置顶状态失败:", error);
    pinnedDates = new Set();
  }
}
