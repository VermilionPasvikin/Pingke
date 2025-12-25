App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://192.168.1.103:5001/api',
    token: null,
    userId: null
  },
  
  onLaunch: function() {
    // 小程序启动时执行
    console.log('小程序启动');
    
    // 自动登录
    this.wechatLogin();
  },
  
  wechatLogin: function() {
    const that = this;
    
    // 调用微信登录接口
    wx.login({
      success: (res) => {
        if (res.code) {
          console.log('获取微信登录code:', res.code);
          
          // 发送code到后端换取token
          wx.request({
            url: `${that.globalData.apiBaseUrl}/auth/wechat-login`,
            method: 'POST',
            data: {
              code: res.code
            },
            success: (response) => {
              if (response.statusCode === 200 && response.data.token) {
                // 保存token和用户信息
                that.globalData.token = response.data.token;
                that.globalData.userId = response.data.user_id;
                wx.setStorageSync('token', response.data.token);
                wx.setStorageSync('userId', response.data.user_id);
                
                console.log('微信登录成功');
                console.log('用户ID:', response.data.user_id);
              } else {
                console.error('微信登录失败:', response.data.message || '未知错误');
              }
            },
            fail: (err) => {
              console.error('网络请求失败:', err);
            }
          });
        } else {
          console.error('获取微信登录code失败:', res.errMsg);
        }
      },
      fail: (err) => {
        console.error('微信登录失败:', err);
      }
    });
  },
  
  getUserProfile: function() {
    const that = this;
    
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          const userInfo = res.userInfo;
          that.globalData.userInfo = userInfo;
          
          // 如果已经登录，更新用户信息到后端
          if (that.globalData.token && that.globalData.userId) {
            wx.request({
              url: `${that.globalData.apiBaseUrl}/users/${that.globalData.userId}`,
              method: 'PUT',
              header: {
                'Authorization': `Bearer ${that.globalData.token}`
              },
              data: {
                nickname: userInfo.nickName,
                avatar_url: userInfo.avatarUrl,
                gender: userInfo.gender
              },
              success: (updateRes) => {
                console.log('用户信息更新成功');
                resolve(userInfo);
              },
              fail: (err) => {
                console.error('更新用户信息失败:', err);
                resolve(userInfo); // 即使更新失败，也返回用户信息
              }
            });
          } else {
            resolve(userInfo);
          }
        },
        fail: (err) => {
          console.error('获取用户信息失败:', err);
          reject(err);
        }
      });
    });
  },
  
  // 获取带认证头的请求头
  getAuthHeader: function() {
    const token = wx.getStorageSync('token') || this.globalData.token;
    if (token) {
      return {
        'Authorization': `Bearer ${token}`
      };
    }
    return {};
  }
});