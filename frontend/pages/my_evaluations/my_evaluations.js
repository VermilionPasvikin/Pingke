const app = getApp();

Page({
  data: {
    evaluations: [],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    hasMore: true
  },

  onLoad: function() {
    this.loadEvaluations(true);
  },

  onShow: function() {
    this.setData({ page: 1, hasMore: true });
    this.loadEvaluations(true);
  },

  onPullDownRefresh: function() {
    this.setData({ page: 1, hasMore: true });
    this.loadEvaluations(true);
    wx.stopPullDownRefresh();
  },

  onReachBottom: function() {
    if (!this.data.hasMore || this.data.loading) return;
    this.loadEvaluations(false);
  },

  loadEvaluations: function(refresh = false) {
    if (this.data.loading) return;

    this.setData({ loading: true });

    const userId = app.globalData.userId;
    const authHeader = app.getAuthHeader();

    wx.request({
      url: `${app.globalData.apiBaseUrl}/users/${userId}/evaluations`,
      method: 'GET',
      header: authHeader,
      data: {
        page: refresh ? 1 : this.data.page,
        per_page: this.data.pageSize
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newEvaluations = res.data.evaluations || [];

          const processedEvaluations = newEvaluations.map(item => ({
            ...item,
            created_at: this.formatDate(item.created_at),
            tags: Array.isArray(item.tags) ?
                  item.tags :
                  (typeof item.tags === 'string' ?
                   item.tags.split(',').map(tag => tag.trim()).filter(t => t) : [])
          }));

          const updatedEvaluations = refresh ?
                processedEvaluations :
                [...this.data.evaluations, ...processedEvaluations];

          this.setData({
            evaluations: updatedEvaluations,
            total: res.data.total,
            page: refresh ? 2 : this.data.page + 1,
            hasMore: newEvaluations.length === this.data.pageSize
          });
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          app.wechatLogin();
        }
      },
      fail: () => {
        wx.showToast({ title: '加载失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  formatDate: function(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  deleteEvaluation: function(e) {
    const id = e.currentTarget.dataset.id;

    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这条评价吗？',
      confirmColor: '#FF0000',
      success: (res) => {
        if (res.confirm) {
          this.performDelete(id);
        }
      }
    });
  },

  performDelete: function(id) {
    const authHeader = app.getAuthHeader();

    wx.showLoading({ title: '删除中...' });

    wx.request({
      url: `${app.globalData.apiBaseUrl}/evaluations/${id}`,
      method: 'DELETE',
      header: authHeader,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '删除成功', icon: 'success' });
          this.setData({ page: 1, hasMore: true });
          this.loadEvaluations(true);
        } else {
          wx.showToast({
            title: res.data.error || '删除失败',
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
