// pages/write_evaluation/write_evaluation.js
const app = getApp();

Page({
  /**
   * 页面的初始数据
   */
  data: {
    courseId: null,
    selectedScore: 0,
    predefinedTags: ['通俗易懂', '内容丰富', '作业较少', '考试简单', '老师负责', '实用性强', '互动性强', '有趣生动', '学术氛围', '实践导向'],
    customTags: [], // 存储自定义标签
    selectedTags: [],
    tagsState: [], // 存储预定义标签的选中状态
    customTag: '', // 自定义标签输入框的值
    canAddCustomTag: false, // 控制添加按钮是否可用
    comment: '',
    anonymous: true,
    submitting: false
  },




  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    if (options.course_id) {
      this.setData({ courseId: options.course_id });
      // 初始化标签状态数组
      const tagsState = this.data.predefinedTags.map(() => false);
      this.setData({ tagsState });
    } else {
      wx.showToast({ title: '课程ID错误', icon: 'none' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    }
  },

  /**
   * 选择评分
   */
  selectScore: function(e) {
    const score = e.currentTarget.dataset.score;
    this.setData({ selectedScore: score });
  },

  /**
   * 获取评分对应的文本描述
   */
  getScoreText: function(score) {
    const scoreTexts = ['请选择评分', '很差', '较差', '一般', '良好', '优秀'];
    return scoreTexts[score] || scoreTexts[0];
  },
  
  /**
   * 检查标签是否被选中
   */
  isSelected: function(tag) {
    return this.data.selectedTags && this.data.selectedTags.indexOf(tag) !== -1;
  },

  /**
   * 切换标签选择状态
   */
  toggleTag: function(e) {
    const tag = e.currentTarget.dataset.tag;
    const index = e.currentTarget.dataset.index;
    const selectedTags = [...this.data.selectedTags];
    const tagsState = [...this.data.tagsState];
    
    // 检查是否已选中
    if (selectedTags.includes(tag)) {
      // 如果已选中，则取消选中
      const tagIndex = selectedTags.indexOf(tag);
      selectedTags.splice(tagIndex, 1);
      tagsState[index] = false;
    } else {
      // 如果未选中，则添加选中（最多选3个）
      if (selectedTags.length < 3) {
        selectedTags.push(tag);
        tagsState[index] = true;
      } else {
        wx.showToast({ title: '最多选择3个标签', icon: 'none' });
        return;
      }
    }
    
    // 直接更新数据，触发样式变化
    this.setData({ 
      selectedTags, 
      tagsState,
      canAddCustomTag: this.data.customTag.trim() !== '' && selectedTags.length < 3
    });
    
    // 移除直接DOM操作，完全依赖数据绑定更新样式
  },

  /**
   * 自定义标签输入
   */
  onCustomTagInput: function(e) {
    const customTag = e.detail.value;
    // 更新自定义标签值并根据是否有内容更新按钮可用状态
    this.setData({ 
      customTag: customTag,
      canAddCustomTag: customTag.trim() !== '' && this.data.selectedTags.length < 3
    });
  },

  /**
   * 切换自定义标签选择状态
   */
  toggleCustomTag: function(e) {
    const tag = e.currentTarget.dataset.tag;
    const selectedTags = [...this.data.selectedTags];
    const customTags = [...this.data.customTags];
    
    // 检查是否已选中
    if (selectedTags.includes(tag)) {
      // 如果已选中，则取消选中并从customTags数组中移除
      const tagIndex = selectedTags.indexOf(tag);
      selectedTags.splice(tagIndex, 1);
      
      // 从customTags数组中移除该标签
      const customTagIndex = customTags.indexOf(tag);
      if (customTagIndex !== -1) {
        customTags.splice(customTagIndex, 1);
      }
    } else {
      // 如果未选中，则添加选中（最多选3个）
      if (selectedTags.length < 3) {
        selectedTags.push(tag);
      } else {
        wx.showToast({ title: '最多选择3个标签', icon: 'none' });
        return;
      }
    }
    
    // 更新选中标签数组、自定义标签数组和按钮状态
    this.setData({ 
      selectedTags,
      customTags,
      canAddCustomTag: this.data.customTag.trim() !== '' && selectedTags.length < 3
    });
  },

  /**
   * 添加自定义标签
   */
  addCustomTag: function() {
    const tag = this.data.customTag.trim();
    if (!tag) return;
    
    // 检查是否已达到3个标签限制
    if (this.data.selectedTags.length >= 3) {
      wx.showToast({ title: '最多选择3个标签', icon: 'none' });
      return;
    }
    
    // 检查是否已存在相同标签（在预定义标签或自定义标签中）
    if (this.data.predefinedTags.includes(tag) || 
        this.data.customTags.includes(tag) || 
        this.data.selectedTags.includes(tag)) {
      wx.showToast({ title: '该标签已存在', icon: 'none' });
      return;
    }
    
    // 添加自定义标签到customTags数组和selectedTags数组
    const customTags = [...this.data.customTags, tag];
    const selectedTags = [...this.data.selectedTags, tag];
    
    // 直接更新数据，确保UI能正确响应变化
    this.setData({
      customTags,
      selectedTags,
      customTag: '',
      canAddCustomTag: false // 清空输入后按钮不可用
    });
  },

  /**
   * 评论输入
   */
  onCommentInput: function(e) {
    this.setData({ comment: e.detail.value });
  },

  /**
   * 切换匿名状态
   */
  toggleAnonymous: function(e) {
    this.setData({ anonymous: e.detail.value });
  },

  /**
   * 提交评价
   */
  submitEvaluation: function() {
    // 验证表单
    if (!this.data.selectedScore) {
      wx.showToast({ title: '请选择评分', icon: 'none' });
      return;
    }
    
    if (this.data.submitting) return;
    
    this.setData({ submitting: true });
    
    // 准备提交数据
    const evaluationData = {
      course_id: this.data.courseId,
      score: this.data.selectedScore,
      tags: this.data.selectedTags,
      comment: this.data.comment.trim(),
      anonymous: this.data.anonymous
    };
    
    // 提交评价
    wx.request({
      url: `${app.globalData.apiBaseUrl}/evaluations`,
      method: 'POST',
      data: evaluationData,
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({ title: '评价提交成功', icon: 'success' });
          // 延迟返回上一页
          setTimeout(() => {
            wx.navigateBack();
          }, 1500);
        } else {
          wx.showToast({ title: '提交失败，请重试', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误，请重试', icon: 'none' });
      },
      complete: () => {
        this.setData({ submitting: false });
      }
    });
  }
});