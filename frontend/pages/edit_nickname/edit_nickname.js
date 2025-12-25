const app = getApp();

Page({
  data: {
    nickname: '',
    originalNickname: '',
    canSave: false
  },

  onLoad: function() {
    this.loadUserInfo();
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
            nickname: res.data.nickname || '',
            originalNickname: res.data.nickname || ''
          });
        }
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' });
      }
    });
  },

  onNicknameInput: function(e) {
    const nickname = e.detail.value;
    const canSave = nickname.trim() !== '' && nickname !== this.data.originalNickname;
    this.setData({
      nickname,
      canSave
    });
  },

  saveNickname: function() {
    if (!this.data.canSave) return;

    const nickname = this.data.nickname.trim();
    if (!nickname) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' });
      return;
    }

    const authHeader = app.getAuthHeader();

    wx.showLoading({ title: '保存中...' });

    wx.request({
      url: `${app.globalData.apiBaseUrl}/me/nickname`,
      method: 'PUT',
      header: authHeader,
      data: { nickname },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '保存成功', icon: 'success' });
          if (app.globalData.userInfo) {
            app.globalData.userInfo.nickName = nickname;
          }
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        } else {
          wx.showToast({
            title: res.data.error || '保存失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  }
});
