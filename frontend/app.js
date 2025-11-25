App({
  globalData: {
    userInfo: null,
    apiBaseUrl: 'http://10.101.181.74:5001/api'
  },
  
  onLaunch: function() {
    // 小程序启动时执行
    console.log('小程序启动');
    
    // 可以在这里进行登录逻辑
    this.checkLoginStatus();
  },
  
  checkLoginStatus: function() {
    // 检查登录状态的逻辑
    const token = wx.getStorageSync('token');
    if (token) {
      console.log('已登录');
    } else {
      console.log('未登录');
    }
  }
});