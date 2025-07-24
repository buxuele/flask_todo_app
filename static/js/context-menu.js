/**
 * 右键菜单相关功能
 */

// 为日期列表项添加右键菜单事件
function addContextMenuToDateItem(li, dateStr) {
  li.addEventListener("contextmenu", function (e) {
    e.preventDefault();
    rightClickedDate = dateStr;

    const contextMenu = document.getElementById("context-menu");
    contextMenu.style.display = "block";
    contextMenu.style.left = e.pageX + "px";
    contextMenu.style.top = e.pageY + "px";
  });
}

// 复制日期列表功能 - 创建新的独立日期副本
function copyDateList() {
  if (!rightClickedDate) return;

  // 获取当前显示的名称（可能是别名）
  const currentDisplayName = document.querySelector(
    `[data-date="${rightClickedDate}"] .date-name`
  ).textContent;
  const copyName = currentDisplayName + "-copy";

  console.log(
    `复制日期列表: ${rightClickedDate} (${currentDisplayName}) -> ${copyName}`
  );

  // 生成一个不冲突的新日期：使用一个未来的日期
  // 策略：从明天开始，找到第一个没有数据的日期
  fetch(CONFIG.API_BASE + "/counts")
    .then((r) => r.json())
    .then((counts) => {
      const existingDates = Object.keys(counts);

      // 从明天开始找一个空闲的日期
      let newDate;
      let daysOffset = 1;
      do {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + daysOffset);
        newDate = futureDate.toISOString().split("T")[0];
        daysOffset++;
      } while (existingDates.includes(newDate) && daysOffset < 365); // 最多找365天

      console.log(`找到空闲日期: ${newDate}`);

      // 1. 复制任务到新日期
      return fetch(CONFIG.API_BASE + "/copy-date", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_date: rightClickedDate,
          target_date: newDate,
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
          return newDate;
        });
    })
    .then((newDate) => {
      // 2. 为新日期设置别名
      return fetch(CONFIG.API_BASE.replace("/todos", "/date-aliases"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date: newDate,
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
          return newDate;
        });
    })
    .then((newDate) => {
      // 3. 刷新日期列表显示新的副本
      generateDateList();

      // 4. 切换到新创建的副本日期
      setTimeout(() => {
        switchDate(newDate);
        console.log(`复制完成，已切换到新日期: ${newDate}`);
      }, 500); // 延迟一点确保列表已刷新
    })
    .catch((error) => {
      alert("复制失败: " + error.message);
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
        alert("重命名失败: " + result.error);
      } else {
        console.log("重命名成功:", result.message);
        // 重新生成日期列表以显示新别名
        generateDateList();
        // 显示成功提示
        console.log(`日期已重命名为: ${newName.trim()}`);
      }
    })
    .catch((error) => {
      alert("重命名失败，请重试: " + error.message);
      console.error("设置日期别名失败:", error);
    });

  document.getElementById("context-menu").style.display = "none";
}

// 删除日期列表功能
function deleteDateList() {
  if (!rightClickedDate) return;

  if (
    !confirm(
      `确定要删除 ${formatDateForDisplay(
        rightClickedDate
      )} 的所有任务吗？此操作不可恢复！`
    )
  ) {
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

      // 删除成功，不显示任何警告
      console.log("删除成功:", result.message);
    })
    .catch((error) => {
      console.error("删除任务失败详细信息:", error);
      alert("删除失败，请重试: " + error.message);
    });

  document.getElementById("context-menu").style.display = "none";
}
