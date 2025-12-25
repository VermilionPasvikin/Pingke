const app = getApp();

Page({
  data: {
    activeTab: 0,
    allList: [],
    discussions: [],
    replies: [],
    displayList: [],
    discussionsCount: 0,
    repliesCount: 0,
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    hasMore: true
  },

  onLoad: function() {
    this.loadDiscussions(true);
  },

  onShow: function() {
    this.setData({ page: 1, hasMore: true });
    this.loadDiscussions(true);
  },

  onPullDownRefresh: function() {
    this.setData({ page: 1, hasMore: true });
    this.loadDiscussions(true);
    wx.stopPullDownRefresh();
  },

  onReachBottom: function() {
    if (!this.data.hasMore || this.data.loading) return;
    this.loadDiscussions(false);
  },

  switchTab: function(e) {
    const tab = parseInt(e.currentTarget.dataset.tab);
    this.setData({ activeTab: tab });
    this.updateDisplayList();
  },

  loadDiscussions: function(refresh = false) {
    if (this.data.loading) return;

    this.setData({ loading: true });

    const userId = app.globalData.userId;
    const authHeader = app.getAuthHeader();

    wx.request({
      url: `${app.globalData.apiBaseUrl}/users/${userId}/discussions`,
      method: 'GET',
      header: authHeader,
      data: {
        page: refresh ? 1 : this.data.page,
        per_page: this.data.pageSize
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newDiscussions = res.data.discussions || [];

          const processedDiscussions = newDiscussions.map(item => ({
            ...item,
            created_at: this.formatDate(item.created_at)
          }));

          const updatedList = refresh ?
                processedDiscussions :
                [...this.data.allList, ...processedDiscussions];

          const discussions = updatedList.filter(item => item.type === 'discussion');
          const replies = updatedList.filter(item => item.type === 'reply');

          this.setData({
            allList: updatedList,
            discussions: discussions,
            replies: replies,
            discussionsCount: discussions.length,
            repliesCount: replies.length,
            total: res.data.total,
            page: refresh ? 2 : this.data.page + 1,
            hasMore: newDiscussions.length === this.data.pageSize
          });

          this.updateDisplayList();
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

  updateDisplayList: function() {
    let displayList;
    if (this.data.activeTab === 0) {
      displayList = this.data.allList;
    } else if (this.data.activeTab === 1) {
      displayList = this.data.discussions;
    } else {
      displayList = this.data.replies;
    }
    this.setData({ displayList });
  },

  formatDate: function(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hour}:${minute}`;
  },

  deleteDiscussion: function(e) {
    const id = e.currentTarget.dataset.id;
    const type = e.currentTarget.dataset.type;

    const content = type === 'discussion' ? '讨论及其所有回复' : '回复';

    wx.showModal({
      title: '确认删除',
      content: `删除后无法恢复，确定要删除这条${content}吗？`,
      confirmColor: '#FF0000',
      success: (res) => {
        if (res.confirm) {
          this.performDelete(id, type);
        }
      }
    });
  },

  performDelete: function(id, type) {
    const authHeader = app.getAuthHeader();
    const endpoint = type === 'discussion' ?
                    `discussions/${id}` :
                    `comments/${id}`;

    wx.showLoading({ title: '删除中...' });

    wx.request({
      url: `${app.globalData.apiBaseUrl}/${endpoint}`,
      method: 'DELETE',
      header: authHeader,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '删除成功', icon: 'success' });
          this.setData({ page: 1, hasMore: true });
          this.loadDiscussions(true);
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
