/**
 * 加载状态管理
 */

class LoadingManager {
  constructor() {
    this.loadingCount = 0;
    this.createLoadingElement();
  }

  createLoadingElement() {
    // 创建全局加载指示器
    const loadingDiv = document.createElement("div");
    loadingDiv.id = "global-loading";
    loadingDiv.className = "loading-overlay";
    loadingDiv.innerHTML = `
      <div class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <div class="loading-text">加载中...</div>
      </div>
    `;
    loadingDiv.style.display = "none";
    document.body.appendChild(loadingDiv);
  }

  show(message = "加载中...") {
    this.loadingCount++;
    const loadingElement = document.getElementById("global-loading");
    const textElement = loadingElement.querySelector(".loading-text");
    if (textElement) {
      textElement.textContent = message;
    }
    loadingElement.style.display = "flex";
  }

  hide() {
    this.loadingCount = Math.max(0, this.loadingCount - 1);
    if (this.loadingCount === 0) {
      const loadingElement = document.getElementById("global-loading");
      loadingElement.style.display = "none";
    }
  }

  // 包装fetch请求，自动显示/隐藏加载状态
  async fetchWithLoading(url, options = {}, message = "加载中...") {
    this.show(message);
    try {
      const response = await fetch(url, options);
      return response;
    } finally {
      this.hide();
    }
  }
}

// 创建全局加载管理器实例
const loadingManager = new LoadingManager();

// 数据缓存管理
class CacheManager {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5分钟缓存
  }

  set(key, data) {
    this.cache.set(key, {
      data: data,
      timestamp: Date.now(),
    });
  }

  get(key) {
    const cached = this.cache.get(key);
    if (!cached) return null;

    // 检查是否过期
    if (Date.now() - cached.timestamp > this.cacheTimeout) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  clear() {
    this.cache.clear();
  }

  // 清除特定前缀的缓存
  clearByPrefix(prefix) {
    for (const key of this.cache.keys()) {
      if (key.startsWith(prefix)) {
        this.cache.delete(key);
      }
    }
  }
}

// 创建全局缓存管理器实例
const cacheManager = new CacheManager();
