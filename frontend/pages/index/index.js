// pages/index/index.js
const app = getApp();
const request = require('../../utils/request.js');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    courses: [],
    searchQuery: '',
    semesterIndex: 0,
    semesterOptions: ['全部学期', '2024春季', '2023秋季', '2023春季'],
    sortIndex: 0,
    sortOptions: ['综合排序', '评分最高', '评分最低', '评论最多'],
    selectedDepartments: [],
    // 添加学院列表数据源
    departmentOptions: ['全部学院', '计算机与人工智能学院', '数学与统计学院', '轻工业学院', '外国语学院', '经济管理学院', '商学院'],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    this.loadCourses();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function() {
    // 页面显示时刷新数据
    this.setData({ page: 1, hasMore: true });
    this.loadCourses(true);
  },

  /**
   * 加载课程列表
   */
  loadCourses: function(refresh = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    // 准备请求参数
    const params = {
      page: refresh ? 1 : this.data.page,
      page_size: this.data.pageSize,
      sort_by: this.data.sortIndex === 0 ? 'default' : 
               this.data.sortIndex === 1 ? 'score_desc' :
               this.data.sortIndex === 2 ? 'score_asc' : 'comments_desc'
    };
    
    if (this.data.searchQuery) {
      params.q = this.data.searchQuery;
    }
    
    if (this.data.semesterIndex > 0) {
      params.semester = this.data.semesterOptions[this.data.semesterIndex];
    }
    
    if (this.data.selectedDepartments.length > 0) {
      params.departments = this.data.selectedDepartments.join(',');
    }
    
    // 调用API获取课程列表
    wx.request({
      url: `${app.globalData.apiBaseUrl}/courses`,
      method: 'GET',
      data: params,
      success: (res) => {
        if (res.statusCode === 200) {
          const newCourses = res.data.courses || [];
          const updatedCourses = refresh ? newCourses : [...this.data.courses, ...newCourses];
          
          this.setData({
            courses: updatedCourses,
            page: refresh ? 2 : this.data.page + 1,
            hasMore: newCourses.length === this.data.pageSize
          });
        }
      },
      fail: (err) => {
        console.error('加载课程失败:', err);
        wx.showToast({ title: '加载失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  /**
   * 搜索输入处理
   */
  onSearchInput: function(e) {
    this.setData({ searchQuery: e.detail.value });
  },

  /**
   * 执行搜索
   */
  onSearch: function() {
    this.setData({ page: 1, hasMore: true });
    this.loadCourses(true);
  },

  /**
   * 学期筛选变更
   */
  onSemesterChange: function(e) {
    this.setData({ 
      semesterIndex: e.detail.value,
      page: 1, 
      hasMore: true 
    });
    this.loadCourses(true);
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
    this.loadCourses(true);
  },

  /**
   * 显示学院筛选器
   */
  showDepartmentFilter: function() {
    const that = this;
    // 创建一个临时数组来存储用户的选择
    let tempSelections = [...this.data.selectedDepartments];
    
    // 直接显示操作菜单
    wx.showActionSheet({
      itemList: ['添加学院', '移除学院', '清空选择', '显示已选学院'],
      success(res) {
        if (res.tapIndex === 0) {
          // 添加学院
          wx.showActionSheet({
            itemList: that.data.departmentOptions.slice(1),
            success(res) {
              const selectedDept = that.data.departmentOptions[res.tapIndex + 1];
              if (!tempSelections.includes(selectedDept)) {
                tempSelections.push(selectedDept);
              }
              that.setData({
                selectedDepartments: tempSelections,
                page: 1,
                hasMore: true
              });
              that.loadCourses(true);
            }
          });
        } else if (res.tapIndex === 1 && tempSelections.length > 0) {
          // 移除学院
          wx.showActionSheet({
            itemList: tempSelections,
            success(res) {
              tempSelections.splice(res.tapIndex, 1);
              that.setData({
                selectedDepartments: tempSelections,
                page: 1,
                hasMore: true
              });
              that.loadCourses(true);
            }
          });
        } else if (res.tapIndex === 2) {
          // 清空选择
          that.setData({
            selectedDepartments: [],
            page: 1,
            hasMore: true
          });
          that.loadCourses(true);
        } else if (res.tapIndex === 3) {
          // 显示已选学院
          wx.showModal({
            title: '已选学院',
            content: tempSelections.length > 0 ? tempSelections.join('\n') : '未选择任何学院',
            showCancel: false
          });
        }
      },
      fail(res) {
        console.log('筛选操作失败');
      }
    });
  },

  /**
   * 加载更多课程
   */
  loadMore: function() {
    if (!this.data.hasMore || this.data.loading) return;
    this.loadCourses(false);
  },

  /**
   * 跳转到课程详情页
   */
  navigateToCourseDetail: function(e) {
    const courseId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/course_detail/course_detail?id=${courseId}`
    });
  }
});