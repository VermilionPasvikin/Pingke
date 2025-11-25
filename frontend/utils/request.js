// utils/request.js
const app = getApp();

/**
 * 封装的请求函数
 * @param {Object} options - 请求配置
 * @param {string} options.url - 请求地址
 * @param {string} [options.method='GET'] - 请求方法
 * @param {Object} [options.data] - 请求数据
 * @param {boolean} [options.showLoading=true] - 是否显示加载提示
 * @returns {Promise} 请求Promise
 */
function request(options) {
  const {
    url,
    method = 'GET',
    data = {},
    showLoading = true
  } = options;

  // 确保URL正确拼接
  const requestUrl = url.startsWith('http') ? url : `${app.globalData.apiBaseUrl}${url}`;

  return new Promise((resolve, reject) => {
    // 显示加载提示
    if (showLoading) {
      wx.showLoading({
        title: '加载中...',
      });
    }

    // 发起请求
    wx.request({
      url: requestUrl,
      method: method,
      data: data,
      header: {
        'content-type': method === 'GET' ? 'application/json' : 'application/x-www-form-urlencoded',
        // 可以在这里添加token等认证信息
        'Authorization': wx.getStorageSync('token') ? `Bearer ${wx.getStorageSync('token')}` : ''
      },
      success: (res) => {
        // 隐藏加载提示
        if (showLoading) {
          wx.hideLoading();
        }

        // 处理响应
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          // 错误处理
          let errorMsg = res.data.message || `请求失败(${res.statusCode})`;
          wx.showToast({
            title: errorMsg,
            icon: 'none'
          });
          reject(new Error(errorMsg));
        }
      },
      fail: (error) => {
        // 隐藏加载提示
        if (showLoading) {
          wx.hideLoading();
        }

        // 网络错误处理
        wx.showToast({
          title: '网络错误，请检查网络连接',
          icon: 'none'
        });
        reject(error);
      }
    });
  });
}

// 导出常用的请求方法
module.exports = {
  request,
  // GET请求
  get: (url, data = {}, showLoading = true) => {
    return request({
      url,
      method: 'GET',
      data,
      showLoading
    });
  },
  
  // POST请求
  post: (url, data = {}, showLoading = true) => {
    return request({
      url,
      method: 'POST',
      data,
      showLoading
    });
  },
  
  // PUT请求
  put: (url, data = {}, showLoading = true) => {
    return request({
      url,
      method: 'PUT',
      data,
      showLoading
    });
  },
  
  // DELETE请求
  delete: (url, data = {}, showLoading = true) => {
    return request({
      url,
      method: 'DELETE',
      data,
      showLoading
    });
  }
};