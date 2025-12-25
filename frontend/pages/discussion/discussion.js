// pages/discussion/discussion.js
const app = getApp();

Page({
  /**
   * 页面的初始数据
   */
  data: {
    courseId: null,
    courseInfo: {},
    discussions: [],
    mainInput: '',
    replyInputs: {},
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    // 用于标记正在请求的点赞操作，防止重复点击
    likingDiscussionIds: [],
    likingReplyIds: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    if (options.course_id) {
      this.setData({ courseId: options.course_id });
      this.loadCourseInfo();
      this.loadDiscussions(true);
    } else {
      wx.showToast({ title: '课程ID错误', icon: 'none' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function() {
    // 页面显示时刷新数据
    this.setData({ page: 1, hasMore: true });
    this.loadDiscussions(true);
  },

  /**
   * 加载课程信息
   */
  loadCourseInfo: function() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/courses/${this.data.courseId}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ courseInfo: res.data });
        }
      },
      fail: () => {
        wx.showToast({ title: '加载课程信息失败', icon: 'none' });
      }
    });
  },

  /**
   * 加载讨论列表
   */
  loadDiscussions: function(refresh = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}/discussions`,
      method: 'GET',
      data: {
        course_id: this.data.courseId,
        page: refresh ? 1 : this.data.page,
        page_size: this.data.pageSize
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const newDiscussions = res.data.discussions || [];
          // 为每个讨论添加显示状态和回复
          const processedDiscussions = newDiscussions.map(item => ({
            ...item,
            showAllReplies: false,
            replies: item.replies || []
          }));
          
          const updatedDiscussions = refresh ? processedDiscussions : [...this.data.discussions, ...processedDiscussions];
          
          this.setData({
            discussions: updatedDiscussions,
            page: refresh ? 2 : this.data.page + 1,
            hasMore: newDiscussions.length === this.data.pageSize
          });
        }
      },
      fail: (err) => {
        console.error('加载讨论失败:', err);
        wx.showToast({ title: '加载失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  /**
   * 监听主输入框输入
   */
  onMainInput: function(e) {
    this.setData({ mainInput: e.detail.value });
  },

  /**
   * 监听回复输入框输入
   */
  onReplyInput: function(e) {
    const discussionId = e.currentTarget.dataset.id;
    const value = e.detail.value;
    this.setData({
      [`replyInputs[${discussionId}]`]: value
    });
  },

  /**
   * 提交讨论
   */
  submitDiscussion: function() {
    console.log('提交讨论，当前mainInput值:', this.data.mainInput);
    const content = this.data.mainInput.trim();
    if (!content) {
      console.log('内容为空，不提交');
      return;
    }

    // 获取认证头
    const authHeader = app.getAuthHeader();

    wx.request({
      url: `${app.globalData.apiBaseUrl}/discussions`,
      method: 'POST',
      header: authHeader,
      data: {
        course_id: this.data.courseId,
        content: content
      },
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({ title: '发送成功' });
          this.setData({ mainInput: '' });
          // 重新加载讨论列表
          this.loadDiscussions(true);
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          app.wechatLogin();
        } else {
          wx.showToast({ title: '发送失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '发送失败', icon: 'none' });
      }
    });
  },

  /**
   * 提交回复
   */
  submitReply: function(e) {
    const discussionId = e.currentTarget.dataset.id;
    const content = this.data.replyInputs[discussionId]?.trim();

    if (!content) return;

    // 获取认证头
    const authHeader = app.getAuthHeader();

    wx.request({
      url: `${app.globalData.apiBaseUrl}/discussions/${discussionId}/replies`,
      method: 'POST',
      header: authHeader,
      data: { content: content },
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({ title: '回复成功' });

          // 清空回复输入框
          this.setData({
            [`replyInputs[${discussionId}]`]: ''
          });

          // 更新该讨论的回复列表
          const updatedDiscussions = this.data.discussions.map(item => {
            if (item.id === discussionId) {
              return {
                ...item,
                replies: [...item.replies, res.data],
                replies_count: item.replies_count + 1
              };
            }
            return item;
          });
          this.setData({ discussions: updatedDiscussions });
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          app.wechatLogin();
        } else {
          wx.showToast({ title: '回复失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '回复失败', icon: 'none' });
      }
    });
  },

  /**
   * 检查是否有正在进行的点赞请求
   */
  isLiking: function(id, type) {
    if (type === 'discussion') {
      return this.data.likingDiscussionIds.includes(id);
    } else if (type === 'reply') {
      return this.data.likingReplyIds.includes(id);
    }
    return false;
  },

  /**
   * 设置点赞请求状态
   */
  setLikingStatus: function(id, type, isLiking) {
    if (type === 'discussion') {
      const currentIds = [...this.data.likingDiscussionIds];
      if (isLiking) {
        if (!currentIds.includes(id)) {
          currentIds.push(id);
        }
      } else {
        const index = currentIds.indexOf(id);
        if (index > -1) {
          currentIds.splice(index, 1);
        }
      }
      this.setData({ likingDiscussionIds: currentIds });
    } else if (type === 'reply') {
      const currentIds = [...this.data.likingReplyIds];
      if (isLiking) {
        if (!currentIds.includes(id)) {
          currentIds.push(id);
        }
      } else {
        const index = currentIds.indexOf(id);
        if (index > -1) {
          currentIds.splice(index, 1);
        }
      }
      this.setData({ likingReplyIds: currentIds });
    }
  },

  /**
   * 点赞讨论
   */
  likeDiscussion: function(e) {
    const discussionId = e.currentTarget.dataset.id;
    
    if (!discussionId) {
      console.error('讨论ID无效');
      wx.showToast({ title: '操作失败：ID无效', icon: 'none' });
      return;
    }

    // 检查是否正在进行点赞请求
    if (this.isLiking(discussionId, 'discussion')) {
      console.log('正在进行点赞操作，请稍后重试');
      wx.showToast({ title: '操作处理中，请稍后重试', icon: 'none' });
      return;
    }
    
    // 先找到要点赞的讨论
    const discussionIndex = this.data.discussions.findIndex(item => item.id === discussionId);
    if (discussionIndex === -1) {
      console.error('未找到讨论');
      wx.showToast({ title: '操作失败：未找到讨论', icon: 'none' });
      return;
    }
    
    // 获取当前点赞状态
    const currentDiscussion = this.data.discussions[discussionIndex];
    const isCurrentlyLiked = currentDiscussion.is_liked || false;

    // 设置点赞中状态，防止重复点击
    this.setLikingStatus(discussionId, 'discussion', true);
    
    // 先更新本地状态，提供即时反馈
    const updatedDiscussions = [...this.data.discussions];
    updatedDiscussions[discussionIndex] = {
      ...currentDiscussion,
      is_liked: !isCurrentlyLiked,
      likes_count: isCurrentlyLiked ? 
                  (currentDiscussion.likes_count || 0) - 1 : 
                  (currentDiscussion.likes_count || 0) + 1
    };
    this.setData({ discussions: updatedDiscussions });
    
    // 获取认证头
    const authHeader = app.getAuthHeader();
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}/discussions/${discussionId}/like`,
      method: 'POST',
      header: {
        ...authHeader
      },
      success: (res) => {
        // 重置点赞状态
        this.setLikingStatus(discussionId, 'discussion', false);
        
        if (res.statusCode === 200) {
          console.log('点赞API响应:', res.data);
          // 使用后端返回的数据更新点赞状态
          const finalUpdatedDiscussions = [...this.data.discussions];
          finalUpdatedDiscussions[discussionIndex] = {
            ...finalUpdatedDiscussions[discussionIndex],
            is_liked: res.data.is_liked !== undefined ? res.data.is_liked : finalUpdatedDiscussions[discussionIndex].is_liked,
            likes_count: res.data.likes !== undefined ? res.data.likes : (res.data.likes_count !== undefined ? res.data.likes_count : finalUpdatedDiscussions[discussionIndex].likes_count)
          };
          this.setData({ discussions: finalUpdatedDiscussions });
          // 显示操作成功提示
          wx.showToast({ title: '操作成功', icon: 'success' });
        } else {
          console.error('点赞操作失败，状态码:', res.statusCode, '响应:', res.data);
          // 如果失败，回滚本地状态
          this.setData({
            discussions: this.data.discussions.map(item => {
              if (item.id === discussionId) {
                return currentDiscussion;
              }
              return item;
            })
          });
          
          // 如果是未登录错误，引导用户登录
          if (res.statusCode === 401) {
            wx.showToast({ 
              title: '请先登录', 
              icon: 'none',
              duration: 2000
            });
            // 重新执行微信登录
            app.wechatLogin();
          } else {
            wx.showToast({ 
              title: `操作失败: ${res.data.message || '未知错误'}`, 
              icon: 'none',
              duration: 2000
            });
          }
        }
      },
      fail: (err) => {
        console.error('点赞操作失败:', err);
        // 重置点赞状态
        this.setLikingStatus(discussionId, 'discussion', false);
        // 如果失败，回滚本地状态
        this.setData({
          discussions: this.data.discussions.map(item => {
            if (item.id === discussionId) {
              return currentDiscussion;
            }
            return item;
          })
        });
        wx.showToast({ title: '操作失败', icon: 'none' });
      }
    });
  },

  /**
   * 点赞回复
   */
  likeReply: function(e) {
    const discussionId = e.currentTarget.dataset.discussionId;
    const replyId = e.currentTarget.dataset.replyId;
    
    if (!discussionId || !replyId) {
      console.error('讨论ID或回复ID无效');
      wx.showToast({ title: '操作失败：ID无效', icon: 'none' });
      return;
    }

    // 检查是否正在进行点赞请求
    if (this.isLiking(replyId, 'reply')) {
      console.log('正在进行点赞操作，请稍后重试');
      wx.showToast({ title: '操作处理中，请稍后重试', icon: 'none' });
      return;
    }
    
    // 先找到对应的讨论和回复
    const discussionIndex = this.data.discussions.findIndex(item => item.id === discussionId);
    if (discussionIndex === -1) {
      console.error('未找到讨论');
      wx.showToast({ title: '操作失败：未找到讨论', icon: 'none' });
      return;
    }
    
    const discussion = this.data.discussions[discussionIndex];
    const replyIndex = discussion.replies.findIndex(reply => reply.id === replyId);
    if (replyIndex === -1) {
      console.error('未找到回复');
      wx.showToast({ title: '操作失败：未找到回复', icon: 'none' });
      return;
    }
    
    // 获取当前点赞状态
    const currentReply = discussion.replies[replyIndex];
    const isCurrentlyLiked = currentReply.is_liked || false;

    // 设置点赞中状态，防止重复点击
    this.setLikingStatus(replyId, 'reply', true);
    
    // 先更新本地状态，提供即时反馈
    const updatedDiscussions = [...this.data.discussions];
    updatedDiscussions[discussionIndex] = {
      ...discussion,
      replies: [...discussion.replies].map((reply, index) => {
        if (index === replyIndex) {
          return {
            ...reply,
            is_liked: !isCurrentlyLiked,
            likes_count: isCurrentlyLiked ? 
                        (reply.likes_count || 0) - 1 : 
                        (reply.likes_count || 0) + 1
          };
        }
        return reply;
      })
    };
    this.setData({ discussions: updatedDiscussions });
    
    // 获取认证头
    const authHeader = app.getAuthHeader();
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}/replies/${replyId}/like`,
      method: 'POST',
      header: {
        ...authHeader
      },
      success: (res) => {
        // 重置点赞状态
        this.setLikingStatus(replyId, 'reply', false);
        
        if (res.statusCode === 200) {
          console.log('点赞API响应:', res.data);
          // 使用后端返回的数据更新点赞状态
          const finalUpdatedDiscussions = [...this.data.discussions];
          finalUpdatedDiscussions[discussionIndex] = {
            ...finalUpdatedDiscussions[discussionIndex],
            replies: finalUpdatedDiscussions[discussionIndex].replies.map((reply, index) => {
              if (index === replyIndex) {
                return {
                  ...reply,
                  is_liked: res.data.is_liked !== undefined ? res.data.is_liked : reply.is_liked,
                  likes_count: res.data.likes !== undefined ? res.data.likes : (res.data.likes_count !== undefined ? res.data.likes_count : reply.likes_count)
                };
              }
              return reply;
            })
          };
          this.setData({ discussions: finalUpdatedDiscussions });
          // 显示操作成功提示
          wx.showToast({ title: '操作成功', icon: 'success' });
        } else {
          console.error('点赞操作失败，状态码:', res.statusCode, '响应:', res.data);
          // 如果失败，回滚本地状态
          const rolledBackDiscussions = [...this.data.discussions];
          rolledBackDiscussions[discussionIndex] = {
            ...rolledBackDiscussions[discussionIndex],
            replies: rolledBackDiscussions[discussionIndex].replies.map((reply, index) => {
              if (index === replyIndex) {
                return currentReply;
              }
              return reply;
            })
          };
          this.setData({ discussions: rolledBackDiscussions });
          
          // 如果是未登录错误，引导用户登录
          if (res.statusCode === 401) {
            wx.showToast({ 
              title: '请先登录', 
              icon: 'none',
              duration: 2000
            });
            // 重新执行微信登录
            app.wechatLogin();
          } else {
            wx.showToast({ 
              title: `操作失败: ${res.data.message || '未知错误'}`, 
              icon: 'none',
              duration: 2000
            });
          }
        }
      },
      fail: (err) => {
        console.error('点赞操作失败:', err);
        // 重置点赞状态
        this.setLikingStatus(replyId, 'reply', false);
        // 如果失败，回滚本地状态
        const rolledBackDiscussions = [...this.data.discussions];
        rolledBackDiscussions[discussionIndex] = {
          ...rolledBackDiscussions[discussionIndex],
          replies: rolledBackDiscussions[discussionIndex].replies.map((reply, index) => {
            if (index === replyIndex) {
              return currentReply;
            }
            return reply;
          })
        };
        this.setData({ discussions: rolledBackDiscussions });
        wx.showToast({ title: '操作失败', icon: 'none' });
      }
    });
  },

  /**
   * 切换回复显示
   */
  toggleReplies: function(e) {
    const discussionId = e.currentTarget.dataset.id;
    const updatedDiscussions = this.data.discussions.map(item => {
      if (item.id === discussionId) {
        return { ...item, showAllReplies: !item.showAllReplies };
      }
      return item;
    });
    this.setData({ discussions: updatedDiscussions });
  },

  /**
   * 加载更多
   */
  onReachBottom: function() {
    if (!this.data.hasMore || this.data.loading) return;
    this.loadDiscussions(false);
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh: function() {
    this.setData({ page: 1, hasMore: true });
    this.loadDiscussions(true).then(() => {
      wx.stopPullDownRefresh();
    });
  }
});