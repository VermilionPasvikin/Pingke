const app = getApp();

Page({
  data: {
    userInfo: {},
    stats: {
      evaluations_count: 0,
      discussions_count: 0,
      comments_count: 0
    }
  },

  onLoad: function() {
    this.loadUserInfo();
  },

  onShow: function() {
    this.loadUserInfo();
  },

  onPullDownRefresh: function() {
    this.loadUserInfo();
    wx.stopPullDownRefresh();
  },

  loadUserInfo: function() {
    const authHeader = app.getAuthHeader();

    wx.request({
      url: `${app.globalData.apiBaseUrl}/me`,
      method: 'GET',
      header: authHeader,
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            userInfo: res.data,
            stats: res.data.stats || {}
          });
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          app.wechatLogin();
        }
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' });
      }
    });
  },

  editNickname: function() {
    wx.navigateTo({
      url: '/pages/edit_nickname/edit_nickname'
    });
  },

  navigateToMyEvaluations: function() {
    wx.navigateTo({
      url: '/pages/my_evaluations/my_evaluations'
    });
  },

  navigateToMyDiscussions: function() {
    wx.navigateTo({
      url: '/pages/my_discussions/my_discussions'
    });
  }
});
