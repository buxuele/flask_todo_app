/**
 * 应用配置和常量
 */
const CONFIG = {
  API_BASE: "/api/todos",
  DATE_FORMAT: "YYYY-MM-DD",
  LOCALE: "zh-CN",
};

// 获取当前日期
const today = new Date();
let currentDate = today.toISOString().split("T")[0]; // 当前选中的日期 YYYY-MM-DD

// 全局变量
let allTodos = []; // 存储所有日期的todos
let isSearchMode = false; // 是否处于搜索模式
let rightClickedDate = null; // 存储右键点击的日期
let pinnedDates = new Set(); // 存储置顶的日期
