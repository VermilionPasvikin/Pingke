// pages/rankings/rankings.js
const app = getApp();

Page({
  /**
   * 页面的初始数据
   */
  data: {
    activeTab: 0,
    tabOptions: ['课程排行', '教师排行', '热门标签', '学院排行'],
    semesterIndex: 0,
    semesterOptions: ['全部学期', '2024春季', '2023秋季', '2023春季'],
    departmentIndex: 0,
    departmentOptions: ['全部学院', '计算机学院', '商学院', '文学院', '理学院', '工学院'],
    courseRankings: [],
    teacherRankings: [],
    tagRankings: [],
    departmentRankings: [],
    loading: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    this.loadRankingsData();
  },

  /**
   * 切换标签页
   */
  switchTab: function(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({ activeTab: index });
    
    // 根据选中的标签加载对应的数据
    if (index === 0 && this.data.courseRankings.length === 0) {
      this.loadCourseRankings();
    } else if (index === 1 && this.data.teacherRankings.length === 0) {
      this.loadTeacherRankings();
    } else if (index === 2 && this.data.tagRankings.length === 0) {
      this.loadTagRankings();
    } else if (index === 3 && this.data.departmentRankings.length === 0) {
      this.loadDepartmentRankings();
    }
  },

  /**
   * 加载所有排行榜数据
   */
  loadRankingsData: function() {
    this.loadCourseRankings();
    this.loadTeacherRankings();
    this.loadTagRankings();
    this.loadDepartmentRankings();
  },

  /**
   * 加载课程排行榜
   */
  loadCourseRankings: function() {
    const semester = this.data.semesterIndex > 0 ? this.data.semesterOptions[this.data.semesterIndex] : null;
    const department = this.data.departmentIndex > 0 ? this.data.departmentOptions[this.data.departmentIndex] : null;
    
    wx.request({
      url: `${app.globalData.apiBaseUrl}/rankings/courses`,
      method: 'GET',
      data: {
        semester: semester,
        department: department,
        limit: 20
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ courseRankings: res.data.courses || [] });
        }
      },
      fail: (err) => {
        console.error('加载课程排行失败:', err);
      }
    });
  },

  /**
   * 加载教师排行榜
   */
  loadTeacherRankings: function() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/rankings/teachers`,
      method: 'GET',
      data: {
        limit: 20
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ teacherRankings: res.data.teachers || [] });
        }
      },
      fail: (err) => {
        console.error('加载教师排行失败:', err);
      }
    });
  },

  /**
   * 加载标签排行榜
   */
  loadTagRankings: function() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/rankings/tags`,
      method: 'GET',
      data: {
        limit: 30
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ tagRankings: res.data.tags || [] });
        }
      },
      fail: (err) => {
        console.error('加载标签排行失败:', err);
      }
    });
  },

  /**
   * 加载学院排行榜
   */
  loadDepartmentRankings: function() {
    wx.request({
      url: `${app.globalData.apiBaseUrl}/rankings/departments`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ departmentRankings: res.data.departments || [] });
        }
      },
      fail: (err) => {
        console.error('加载学院排行失败:', err);
      }
    });
  },

  /**
   * 学期筛选变更
   */
  onSemesterChange: function(e) {
    this.setData({ semesterIndex: e.detail.value });
    this.loadCourseRankings();
  },

  /**
   * 学院筛选变更
   */
  onDepartmentChange: function(e) {
    this.setData({ departmentIndex: e.detail.value });
    this.loadCourseRankings();
  },

  /**
   * 跳转到课程详情
   */
  navigateToCourseDetail: function(e) {
    const courseId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/course_detail/course_detail?id=${courseId}`
    });
  },

  /**
   * 跳转到教师详情
   */
  navigateToTeacherDetail: function(e) {
    const teacherId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/teacher_detail/teacher_detail?id=${teacherId}`
    });
  },

  /**
   * 按标签搜索课程
   */
  searchByTag: function(e) {
    const tag = e.currentTarget.dataset.tag;
    wx.navigateTo({
      url: `/pages/index/index?tag=${encodeURIComponent(tag)}`
    });
  },

  /**
   * 根据标签使用次数计算显示大小
   */
  getTagSize: function(count) {
    // 根据使用次数返回不同的字体大小，范围12-18px
    if (count > 100) return 18;
    if (count > 50) return 16;
    if (count > 20) return 14;
    return 12;
  }
});