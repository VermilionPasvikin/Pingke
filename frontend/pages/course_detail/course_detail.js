// pages/course_detail/course_detail.js
const app = getApp();

Page({
  /**
   * 页面的初始数据
   */
  data: {
    courseId: null,
    course: {},
    popularTags: [],
    ratingDistribution: {},
    recentEvaluations: [],
    recentComments: [],
    loading: true
  },
  
  // 用于标记正在请求的点赞操作，防止重复点击
  pendingLikes: {},
  
  // 检查是否有正在进行的点赞请求
  isLiking: function(id, type) {
    return this.pendingLikes[`${type}_${id}`] === true;
  },
  
  // 设置点赞请求状态
  setLikingState: function(id, type, isPending) {
    this.pendingLikes[`${type}_${id}`] = isPending;
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    if (options.id) {
      this.setData({ courseId: options.id });
      this.loadCourseDetails();
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
    // 如果页面已加载过，刷新数据
    if (this.data.courseId && !this.data.loading) {
      this.loadCourseDetails();
    }
  },

  /**
   * 加载课程详情数据
   */
  loadCourseDetails: function() {
    this.setData({ loading: true });
    
    // 加载课程基本信息
    wx.request({
      url: `${app.globalData.apiBaseUrl}/courses/${this.data.courseId}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          // 从teacher对象中提取department信息并添加到course对象中
          const courseData = res.data;
          if (courseData.teacher && courseData.teacher.department) {
            courseData.department = courseData.teacher.department;
          }
          this.setData({ course: courseData });
        }
      },
      fail: (err) => {
        console.error('加载课程详情失败:', err);
      }
    });
    
    // 加载热门标签
    wx.request({
      url: `${app.globalData.apiBaseUrl}/courses/${this.data.courseId}/popular_tags`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ popularTags: res.data.tags || [] });
        }
      }
    });
    
    // 加载评分分布
    wx.request({
      url: `${app.globalData.apiBaseUrl}/courses/${this.data.courseId}/rating_distribution`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          // 获取评分分布数据
          const distribution = res.data.distribution || {};
          
          // 计算总评价数
          let totalEvaluations = 0;
          for (let score = 1; score <= 5; score++) {
            const value = Number(distribution[score]) || 0;
            totalEvaluations += value;
          }
          
          // 计算百分比
          const processedDistribution = {};
          for (let score = 1; score <= 5; score++) {
            // 确保每个评分都有数值，且为数字类型
            const value = Number(distribution[score]) || 0;
            // 计算百分比并保留一位小数
            const percentage = totalEvaluations > 0 ? 
                             parseFloat(((value / totalEvaluations) * 100).toFixed(1)) : 
                             0;
            processedDistribution[score] = percentage;
          }
          
          this.setData({ ratingDistribution: processedDistribution });
        }
      }
    });
    
    // 加载最近评价
    wx.request({
      url: `${app.globalData.apiBaseUrl}/evaluations`,
      method: 'GET',
      data: {
        course_id: this.data.courseId,
        limit: 3
      },
      success: (res) => {
        if (res.statusCode === 200) {
          let evaluations = res.data.evaluations || [];
          // 添加调试日志检查score数据类型
          evaluations.forEach((item, index) => {
            console.log(`Evaluation ${index} score:`, item.score, typeof item.score);
          });
          // 预处理评分数据，确保score为数字类型，并添加likes_count和is_liked字段
          evaluations = evaluations.map(item => ({
            ...item,
            score: typeof item.score === 'number' ? item.score : Number(item.score) || 0,
            likes_count: item.likes !== undefined ? item.likes : 0,
            is_liked: item.is_liked || false,
            // 确保tags始终是数组格式，如果是字符串则根据逗号分割
            tags: Array.isArray(item.tags) ? 
                  item.tags : 
                  (typeof item.tags === 'string' ? item.tags.split(',').map(tag => tag.trim()) : [])
          }));
          this.setData({ recentEvaluations: evaluations });
        }
      },
    });
    
    // 加载最近评论
    wx.request({
      url: `${app.globalData.apiBaseUrl}/comments`,
      method: 'GET',
      data: {
        course_id: this.data.courseId,
        limit: 3
      },
      success: (res) => {
        if (res.statusCode === 200) {
          let comments = res.data.comments || [];
          // 确保每个评论都有likes_count字段，值为likes字段的值，并将reply_count映射到replies_count
          comments = comments.map(item => ({
            ...item,
            replies_count: item.reply_count || 0,
            likes_count: item.likes !== undefined ? item.likes : 0,
            is_liked: item.is_liked || false
          }));
          this.setData({ recentComments: comments });
        }
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  /**
   * 跳转到评价列表
   */
  navigateToEvaluationList: function() {
    wx.navigateTo({
      url: `/pages/evaluation_list/evaluation_list?course_id=${this.data.courseId}`
    });
  },

  /**
   * 跳转到讨论列表
   */
  navigateToComments: function() {
    wx.navigateTo({
      url: `/pages/discussion/discussion?course_id=${this.data.courseId}`
    });
  },

  /**
   * 点赞评价
   */
  likeEvaluation: function(e) {
    const evaluationId = e.currentTarget.dataset.id;
    const LIKE_TYPE = 'evaluation';
    
    // 检查是否有重复点击
    if (this.isLiking(evaluationId, LIKE_TYPE)) {
      console.log('正在进行点赞操作，请稍后重试');
      return;
    }
    
    if (!evaluationId) {
      console.error('评价ID无效');
      wx.showToast({ title: '操作失败：ID无效', icon: 'none' });
      return;
    }
    
    // 先找到要点赞的评价
    const evaluationIndex = this.data.recentEvaluations.findIndex(item => item.id === evaluationId);
    if (evaluationIndex === -1) {
      console.error('未找到评价');
      wx.showToast({ title: '操作失败：未找到评价', icon: 'none' });
      return;
    }
    
    // 获取当前点赞状态
    const currentEvaluation = this.data.recentEvaluations[evaluationIndex];
    const isCurrentlyLiked = currentEvaluation.is_liked || false;
    
    // 设置点赞中状态，防止重复点击
    this.setLikingState(evaluationId, LIKE_TYPE, true);
    
    // 先更新本地状态，提供即时反馈
    const updatedEvaluations = [...this.data.recentEvaluations];
    updatedEvaluations[evaluationIndex] = {
      ...currentEvaluation,
      is_liked: !isCurrentlyLiked,
      likes_count: isCurrentlyLiked ? 
                  (currentEvaluation.likes_count || 0) - 1 : 
                  (currentEvaluation.likes_count || 0) + 1
    };
    this.setData({ recentEvaluations: updatedEvaluations });
    
    // 获取认证头
  const authHeader = app.getAuthHeader();
  
  wx.request({
      url: `${app.globalData.apiBaseUrl}/evaluations/${evaluationId}/like`,
      method: 'POST',
      header: {
        ...authHeader
      },
      success: (res) => {
        // 重置点赞状态
        this.setLikingState(evaluationId, LIKE_TYPE, false);
        
        if (res.statusCode === 200) {
          console.log('点赞API响应:', res.data);
          // 使用后端返回的数据更新点赞状态
          const finalUpdatedEvaluations = [...this.data.recentEvaluations];
          // 重新查找索引，因为数组可能已经被其他操作修改
          const newIndex = finalUpdatedEvaluations.findIndex(item => item.id === evaluationId);
          if (newIndex !== -1) {
            finalUpdatedEvaluations[newIndex] = {
              ...finalUpdatedEvaluations[newIndex],
              is_liked: res.data.is_liked !== undefined ? res.data.is_liked : finalUpdatedEvaluations[newIndex].is_liked,
              likes_count: res.data.likes !== undefined ? res.data.likes : (res.data.likes_count !== undefined ? res.data.likes_count : finalUpdatedEvaluations[newIndex].likes_count)
            };
            this.setData({ recentEvaluations: finalUpdatedEvaluations });
          }
          // 显示操作成功提示
          wx.showToast({ title: '操作成功', icon: 'success' });
        } else {
          console.error('点赞操作失败，状态码:', res.statusCode, '响应:', res.data);
          // 如果失败，回滚本地状态
          this.rollbackEvaluationLike(evaluationId, currentEvaluation);
          
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
        // 重置点赞状态并回滚
        this.setLikingState(evaluationId, LIKE_TYPE, false);
        this.rollbackEvaluationLike(evaluationId, currentEvaluation);
        wx.showToast({ title: '操作失败', icon: 'none' });
      }
    });
  },
  
  // 回滚评价点赞状态
  rollbackEvaluationLike: function(evaluationId, originalState) {
    const updatedEvaluations = this.data.recentEvaluations.map(item => {
      if (item.id === evaluationId) {
        return originalState;
      }
      return item;
    });
    this.setData({ recentEvaluations: updatedEvaluations });
  },

  /**
   * 点赞讨论/评论
   */
  likeComment: function(e) {
    const commentId = e.currentTarget.dataset.id;
    const LIKE_TYPE = 'comment';
    console.log('点赞评论/讨论ID:', commentId);
    
    // 检查是否有重复点击
    if (this.isLiking(commentId, LIKE_TYPE)) {
      console.log('正在进行点赞操作，请稍后重试');
      return;
    }
    
    if (!commentId) {
      console.error('评论ID无效');
      wx.showToast({ title: '操作失败：ID无效', icon: 'none' });
      return;
    }
    
    // 先找到要点赞的评论
    const commentIndex = this.data.recentComments.findIndex(item => item.id === commentId);
    if (commentIndex === -1) {
      console.error('未找到评论');
      wx.showToast({ title: '操作失败：未找到评论', icon: 'none' });
      return;
    }
    
    // 获取当前点赞状态
    const currentComment = this.data.recentComments[commentIndex];
    const isCurrentlyLiked = currentComment.is_liked || false;
    
    // 设置点赞中状态，防止重复点击
    this.setLikingState(commentId, LIKE_TYPE, true);
    
    // 先更新本地状态，提供即时反馈
    const updatedComments = [...this.data.recentComments];
    updatedComments[commentIndex] = {
      ...currentComment,
      is_liked: !isCurrentlyLiked,
      likes_count: isCurrentlyLiked ? 
                  (currentComment.likes_count || 0) - 1 : 
                  (currentComment.likes_count || 0) + 1
    };
    this.setData({ recentComments: updatedComments });
    
    // 使用封装的request方法发送请求
    // 获取认证头
    const authHeader = app.getAuthHeader();
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}/comments/${commentId}/like`,
      method: 'POST',
      header: {
        'content-type': 'application/json',
        ...authHeader
      },
      success: (res) => {
        // 重置点赞状态
        this.setLikingState(commentId, LIKE_TYPE, false);
        
        console.log('点赞API响应:', res);
        if (res.statusCode === 200) {
          console.log('评论点赞API响应数据:', res.data);
          // 使用后端返回的数据更新点赞状态
          const finalUpdatedComments = [...this.data.recentComments];
          // 重新查找索引，因为数组可能已经被其他操作修改
          const newIndex = finalUpdatedComments.findIndex(item => item.id === commentId);
          if (newIndex !== -1) {
            finalUpdatedComments[newIndex] = {
              ...finalUpdatedComments[newIndex],
              is_liked: res.data.is_liked !== undefined ? res.data.is_liked : finalUpdatedComments[newIndex].is_liked,
              likes_count: res.data.likes !== undefined ? res.data.likes : (res.data.likes_count !== undefined ? res.data.likes_count : finalUpdatedComments[newIndex].likes_count)
            };
            this.setData({ recentComments: finalUpdatedComments });
          }
          // 显示操作成功提示
          wx.showToast({ title: '操作成功', icon: 'success' });
        } else {
          console.error('点赞操作失败，状态码:', res.statusCode, '响应:', res.data);
          // 如果失败，回滚本地状态
          this.rollbackCommentLike(commentId, currentComment);
          
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
        console.error('点赞网络请求失败:', err);
        // 重置点赞状态并回滚
        this.setLikingState(commentId, LIKE_TYPE, false);
        this.rollbackCommentLike(commentId, currentComment);
        wx.showToast({ 
          title: '网络请求失败', 
          icon: 'none',
          duration: 2000
        });
      }
    });
  },
  
  // 回滚评论点赞状态
  rollbackCommentLike: function(commentId, originalState) {
    const updatedComments = this.data.recentComments.map(item => {
      if (item.id === commentId) {
        return originalState;
      }
      return item;
    });
    this.setData({ recentComments: updatedComments });
  },

  /**
   * 回复评论
   */
  replyComment: function(e) {
    const commentId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/comments/comments?course_id=${this.data.courseId}&reply_to=${commentId}`
    });
  },

  /**
   * 写评价
   */
  writeEvaluation: function() {
    wx.navigateTo({
      url: `/pages/write_evaluation/write_evaluation?course_id=${this.data.courseId}`
    });
  },

  /**
   * 参与讨论
   */
  writeComment: function() {
    wx.navigateTo({
      url: `/pages/discussion/discussion?course_id=${this.data.courseId}`
    });
  }
});