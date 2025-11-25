// pages/evaluation_list/evaluation_list.js
const app = getApp();

Page({
  /**
   * 页面的初始数据
   */
  data: {
    courseId: null,
    evaluations: [],
    scoreFilterIndex: 0,
    scoreFilterOptions: ['全部评分', '5星', '4星', '3星', '2星', '1星'],
    sortIndex: 0,
    sortOptions: ['最新发布', '点赞最多', '评分最高', '评分最低'],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    // 用于标记正在请求的点赞操作，防止重复点击
    likingEvaluationIds: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    if (options.course_id) {
      this.setData({ courseId: options.course_id });
      this.loadEvaluations(true);
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
    this.loadEvaluations(true);
  },

  /**
   * 加载评价列表
   */
  loadEvaluations: function(refresh = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    // 准备请求参数
    const params = {
      course_id: this.data.courseId,
      page: refresh ? 1 : this.data.page,
      page_size: this.data.pageSize,
      sort_by: this.data.sortIndex === 0 ? 'newest' : 
               this.data.sortIndex === 1 ? 'likes_desc' :
               this.data.sortIndex === 2 ? 'score_desc' : 'score_asc'
    };
    
    // 添加评分筛选
    if (this.data.scoreFilterIndex > 0) {
      params.score = 6 - this.data.scoreFilterIndex; // 转换为实际分数值
    }
    
    // 调用API获取评价列表
    wx.request({
      url: `${app.globalData.apiBaseUrl}/evaluations`,
      method: 'GET',
      data: params,
      success: (res) => {
        if (res.statusCode === 200) {
          let newEvaluations = res.data.evaluations || [];
          // 添加调试日志检查score数据类型
          newEvaluations.forEach((item, index) => {
            console.log(`Evaluation List Item ${index} score:`, item.score, typeof item.score);
          });
          // 预处理评分数据，确保score为数字类型，并添加字段映射
          newEvaluations = newEvaluations.map(item => ({
            ...item,
            score: typeof item.score === 'number' ? item.score : Number(item.score) || 0,
            likes_count: item.likes !== undefined ? item.likes : 0,
            is_liked: item.is_liked || false,
            // 确保tags始终是数组格式，如果是字符串则根据逗号分割
            tags: Array.isArray(item.tags) ? 
                  item.tags : 
                  (typeof item.tags === 'string' ? item.tags.split(',').map(tag => tag.trim()) : [])
          }));
          const updatedEvaluations = refresh ? newEvaluations : [...this.data.evaluations, ...newEvaluations];
          
          this.setData({
            evaluations: updatedEvaluations,
            page: refresh ? 2 : this.data.page + 1,
            hasMore: newEvaluations.length === this.data.pageSize
          });
        }
      },
      fail: (err) => {
        console.error('加载评价失败:', err);
        wx.showToast({ title: '加载失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  /**
   * 评分筛选变更
   */
  onScoreFilterChange: function(e) {
    this.setData({ 
      scoreFilterIndex: e.detail.value,
      page: 1, 
      hasMore: true 
    });
    this.loadEvaluations(true);
  },

  /**
   * 排序方式变更
   */
  onSortChange: function(e) {
    this.setData({ 
      sortIndex: e.detail.value,
      page: 1, 
      hasMore: true 
    });
    this.loadEvaluations(true);
  },

  /**
   * 加载更多评价
   */
  loadMore: function() {
    if (!this.data.hasMore || this.data.loading) return;
    this.loadEvaluations(false);
  },

  /**
   * 检查是否有正在进行的点赞请求
   */
  isLiking: function(evaluationId) {
    return this.data.likingEvaluationIds.includes(evaluationId);
  },

  /**
   * 设置点赞请求状态
   */
  setLikingStatus: function(evaluationId, isLiking) {
    const currentIds = [...this.data.likingEvaluationIds];
    if (isLiking) {
      if (!currentIds.includes(evaluationId)) {
        currentIds.push(evaluationId);
      }
    } else {
      const index = currentIds.indexOf(evaluationId);
      if (index > -1) {
        currentIds.splice(index, 1);
      }
    }
    this.setData({ likingEvaluationIds: currentIds });
  },

  /**
   * 点赞评价
   */
  likeEvaluation: function(e) {
    const evaluationId = e.currentTarget.dataset.id;
    
    if (!evaluationId) {
      console.error('评价ID无效');
      wx.showToast({ title: '操作失败：ID无效', icon: 'none' });
      return;
    }

    // 检查是否正在进行点赞请求
    if (this.isLiking(evaluationId)) {
      console.log('正在进行点赞操作，请稍后重试');
      wx.showToast({ title: '操作处理中，请稍后重试', icon: 'none' });
      return;
    }
    
    // 先找到要点赞的评价
    const evaluationIndex = this.data.evaluations.findIndex(item => item.id === evaluationId);
    if (evaluationIndex === -1) {
      console.error('未找到评价');
      wx.showToast({ title: '操作失败：未找到评价', icon: 'none' });
      return;
    }
    
    // 获取当前点赞状态
    const currentEvaluation = this.data.evaluations[evaluationIndex];
    const isCurrentlyLiked = currentEvaluation.is_liked || false;

    // 设置点赞中状态，防止重复点击
    this.setLikingStatus(evaluationId, true);
    
    // 先更新本地状态，提供即时反馈
    const updatedEvaluations = [...this.data.evaluations];
    updatedEvaluations[evaluationIndex] = {
      ...currentEvaluation,
      is_liked: !isCurrentlyLiked,
      likes_count: isCurrentlyLiked ? 
                  (currentEvaluation.likes_count || 0) - 1 : 
                  (currentEvaluation.likes_count || 0) + 1
    };
    this.setData({ evaluations: updatedEvaluations });
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}/evaluations/${evaluationId}/like`,
      method: 'POST',
      success: (res) => {
        // 重置点赞状态
        this.setLikingStatus(evaluationId, false);
        
        if (res.statusCode === 200) {
          console.log('点赞API响应:', res.data);
          // 使用后端返回的数据更新点赞状态
          const finalUpdatedEvaluations = [...this.data.evaluations];
          finalUpdatedEvaluations[evaluationIndex] = {
            ...finalUpdatedEvaluations[evaluationIndex],
            is_liked: res.data.is_liked !== undefined ? res.data.is_liked : finalUpdatedEvaluations[evaluationIndex].is_liked,
            likes_count: res.data.likes !== undefined ? res.data.likes : (res.data.likes_count !== undefined ? res.data.likes_count : finalUpdatedEvaluations[evaluationIndex].likes_count)
          };
          this.setData({ evaluations: finalUpdatedEvaluations });
          // 显示操作成功提示
          wx.showToast({ title: '操作成功', icon: 'success' });
        } else {
          console.error('点赞操作失败，状态码:', res.statusCode, '响应:', res.data);
          // 如果失败，回滚本地状态
          this.setData({
            evaluations: this.data.evaluations.map(item => {
              if (item.id === evaluationId) {
                return currentEvaluation;
              }
              return item;
            })
          });
          wx.showToast({ 
            title: `操作失败: ${res.data.message || '未知错误'}`, 
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        console.error('点赞操作失败:', err);
        // 重置点赞状态
        this.setLikingStatus(evaluationId, false);
        // 如果失败，回滚本地状态
        this.setData({
          evaluations: this.data.evaluations.map(item => {
            if (item.id === evaluationId) {
              return currentEvaluation;
            }
            return item;
          })
        });
        wx.showToast({ title: '操作失败', icon: 'none' });
      }
    });
  }
});