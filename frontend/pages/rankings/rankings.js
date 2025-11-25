// pages/rankings/rankings.js
const app = getApp();
const { request, get } = require('../../utils/request.js');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    activeTab: 0,
    tabOptions: ['课程排行', '教师排行', '热门标签', '学院排行'],
    semesterIndex: 0,
    semesterOptions: ['全部学期', '2024春', '2023秋', '2023春', '2022秋'],
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
    console.log('排行榜页面加载');
    // 直接加载真实数据
    this.loadRankingsData();
  },
  
  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function() {
    // 如果数据为空，可以选择重新加载
    if (this.data.courseRankings.length === 0 && 
        this.data.teacherRankings.length === 0 && 
        this.data.tagRankings.length === 0 && 
        this.data.departmentRankings.length === 0) {
      this.loadRankingsData();
    }
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
    console.log('开始加载所有排行榜数据');
    this.setData({ loading: true });
    
    // 使用Promise.allSettled确保即使某些请求失败，所有请求都能完成并更新加载状态
    Promise.allSettled([
      this.loadCourseRankings(),
      this.loadTeacherRankings(),
      this.loadTagRankings(),
      this.loadDepartmentRankings()
    ]).then(results => {
      // 分析结果，记录成功和失败的请求
      let successCount = 0;
      let failCount = 0;
      
      results.forEach((result, index) => {
        const types = ['课程', '教师', '标签', '学院'];
        if (result.status === 'fulfilled') {
          successCount++;
          console.log(`${types[index]}排行数据加载成功`);
        } else {
          failCount++;
          console.error(`${types[index]}排行数据加载失败:`, result.reason);
        }
      });
      
      console.log(`排行榜数据加载完成: 成功${successCount}个, 失败${failCount}个`);
      this.setData({ loading: false });
    }).catch(err => {
      console.error('加载排行榜数据时发生错误:', err);
      this.setData({ loading: false });
    });
  },

  /**
   * 加载课程排行榜
   */
  loadCourseRankings: function() {
    // 优化参数处理，不再将'全部学期'和'全部学院'设置为null
    // 而是使用实际的选项值，让后端决定如何处理
    const semester = this.data.semesterOptions[this.data.semesterIndex];
    const department = this.data.departmentOptions[this.data.departmentIndex];
    
    console.log('加载课程排行，参数:', { semester, department, semesterIndex: this.data.semesterIndex, departmentIndex: this.data.departmentIndex });
    
    // 构建请求参数，不包含null值
    const params = {
      limit: 20
    };
    
    // 只有当不是'全部学期'时才添加semester参数
    if (this.data.semesterIndex > 0) {
      params.semester = semester;
    }
    
    // 只有当不是'全部学院'时才添加department参数
    if (this.data.departmentIndex > 0) {
      params.department = department;
    }
    
    console.log('最终发送的请求参数:', params);
    
    return get('/rankings/courses', params).then(res => {
      console.log('课程排行API完整返回数据:', JSON.stringify(res));
      
      // 检查并处理各种可能的数据格式
      if (res && Array.isArray(res.courses)) {
        console.log('检测到courses数组，长度:', res.courses.length);
        // 确保每个课程对象都有必要的属性，防止渲染错误
        const validatedData = res.courses.map(course => {
          console.log('处理课程数据:', course);
          return {
            id: course.id || '',
            name: course.name || '未知课程', // 与WXML中保持一致
            teacher: course.teacher || { name: '未知教师' },
            avg_score: course.avg_score || '--',
            evaluation_count: course.evaluation_count || 0
          };
        });
        this.setData({ courseRankings: validatedData });
      } else if (res && Array.isArray(res.rankings)) {
        console.log('检测到rankings数组，长度:', res.rankings.length);
        // API返回格式为 {rankings: Array}
        // 确保每个课程对象都有必要的属性，处理后端API返回的字段名
        const validatedData = res.rankings.map(course => {
          console.log('处理课程数据:', course);
          return {
            id: course.course_id || course.id || '', // 优先使用course_id，兼容id
            name: course.course_name || course.name || '未知课程', // 优先使用course_name，兼容name
            teacher: course.teacher_name ? { name: course.teacher_name } : (course.teacher || { name: '未知教师' }), // 处理teacher_name或teacher对象
            avg_score: course.avg_score || '--',
            evaluation_count: course.evaluation_count || 0
          };
        });
        this.setData({ courseRankings: validatedData });
      } else if (res && Array.isArray(res)) {
        console.log('检测到直接返回数组，长度:', res.length);
        // 可能API直接返回了数组
        const validatedData = res.map(course => {
          console.log('处理课程数据:', course);
          return {
            id: course.course_id || course.id || '', // 优先使用course_id，兼容id
            name: course.course_name || course.name || '未知课程', // 优先使用course_name，兼容name
            teacher: course.teacher_name ? { name: course.teacher_name } : (course.teacher || { name: '未知教师' }), // 处理teacher_name或teacher对象
            avg_score: course.avg_score || '--',
            evaluation_count: course.evaluation_count || 0
          };
        });
        this.setData({ courseRankings: validatedData });
      } else if (res && typeof res === 'object') {
        // 检查是否有其他可能的数据字段
        console.log('检测到对象类型但非预期格式，尝试查找其他可能的数据字段');
        
        // 遍历对象属性，查找可能的数据数组
        for (const key in res) {
          if (Array.isArray(res[key])) {
            console.log(`发现潜在数据数组 ${key}，长度:`, res[key].length);
            // 验证数据结构
            const validatedData = res[key].map(course => {
              console.log('处理课程数据:', course);
              return {
                id: course.course_id || course.id || '', // 优先使用course_id，兼容id
                name: course.course_name || course.name || '未知课程', // 优先使用course_name，兼容name
                teacher: course.teacher_name ? { name: course.teacher_name } : (course.teacher || { name: '未知教师' }), // 处理teacher_name或teacher对象
                avg_score: course.avg_score || '--',
                evaluation_count: course.evaluation_count || 0
              };
            });
            this.setData({ courseRankings: validatedData });
            return;
          }
        }
        
        console.warn('课程排行数据格式不正确，未找到有效数组:', res);
        this.setData({ courseRankings: [] });
      } else {
        console.warn('课程排行数据格式不正确或为空:', res);
        this.setData({ courseRankings: [] });
      }
    }).catch(err => {
      console.error('加载课程排行失败:', err);
      wx.showToast({
        title: '加载课程排行失败',
        icon: 'none',
        duration: 2000
      });
      this.setData({ courseRankings: [] });
      throw err;
    });
  },

  /**
   * 加载教师排行榜
   */
  loadTeacherRankings: function() {
    console.log('加载教师排行');
    
    return get('/rankings/teachers', {
      limit: 20
    }).then(res => {
      console.log('教师排行数据返回:', res);
      // 确保数据结构正确
      if (res && Array.isArray(res.teachers)) {
        // 处理teacher_name字段映射为name
        const formattedData = res.teachers.map(item => ({
          ...item,
          name: item.teacher_name || item.name || '未知教师',
          id: item.teacher_id || item.id
        }));
        this.setData({ teacherRankings: formattedData });
      } else if (res && Array.isArray(res.rankings)) {
        // API返回格式为 {rankings: Array}
        // 处理teacher_name字段映射为name
        const formattedData = res.rankings.map(item => ({
          ...item,
          name: item.teacher_name || item.name || '未知教师',
          id: item.teacher_id || item.id
        }));
        this.setData({ teacherRankings: formattedData });
      } else if (res && Array.isArray(res)) {
        // 可能API直接返回了数组
        // 处理teacher_name字段映射为name
        const formattedData = res.map(item => ({
          ...item,
          name: item.teacher_name || item.name || '未知教师',
          id: item.teacher_id || item.id
        }));
        this.setData({ teacherRankings: formattedData });
      } else {
        console.warn('教师排行数据格式不正确:', res);
        this.setData({ teacherRankings: [] });
      }
    }).catch(err => {
      console.error('加载教师排行失败:', err);
      wx.showToast({
        title: '加载教师排行失败',
        icon: 'none'
      });
      this.setData({ teacherRankings: [] });
      throw err;
    });
  },

  /**
   * 加载标签排行榜
   */
  loadTagRankings: function() {
    console.log('加载标签排行');
    
    return get('/rankings/tags', {
      limit: 10 // 根据需求限制最多显示10个标签
    }).then(res => {
      console.log('标签排行数据返回:', res);
      
      // 处理数据，转换为前端期望的二维数组格式
      let tagRankings = [];
      
      if (res && Array.isArray(res.tags)) {
        // 格式1: {tags: [{tag: '标签名', count: 数量}]}
        tagRankings = res.tags.map(item => [item.tag || item.name || '无标签', item.count || 0]);
      } else if (res && Array.isArray(res.rankings)) {
        // 格式2: {rankings: [{tag: '标签名', count: 数量}]}
        tagRankings = res.rankings.map(item => [item.tag || item.name || '无标签', item.count || 0]);
      } else if (res && Array.isArray(res)) {
        // 格式3: 直接数组 [{tag: '标签名', count: 数量}] 或 [['标签名', 数量]]
        if (res.length > 0 && Array.isArray(res[0])) {
          // 已经是二维数组格式
          tagRankings = res.map(item => [item[0] || '无标签', item[1] || 0]);
        } else {
          // 对象数组格式
          tagRankings = res.map(item => [item.tag || item.name || '无标签', item.count || 0]);
        }
      } else {
        console.warn('标签排行数据格式不正确:', res);
        tagRankings = [];
      }
      
      // 确保最多只显示10个标签
      tagRankings = tagRankings.slice(0, 10);
      console.log('转换后的标签数据:', tagRankings);
      
      this.setData({ tagRankings });
    }).catch(err => {
      console.error('加载标签排行失败:', err);
      wx.showToast({
        title: '加载标签排行失败',
        icon: 'none'
      });
      this.setData({ tagRankings: [] });
      throw err;
    });
  },

  /**
   * 加载学院排行榜
   */
  loadDepartmentRankings: function() {
    console.log('加载学院排行');
    
    return get('/rankings/departments', {}).then(res => {
      console.log('学院排行数据返回:', res);
      // 确保数据结构正确
      if (res && Array.isArray(res.departments)) {
        this.setData({ departmentRankings: res.departments });
      } else if (res && Array.isArray(res.rankings)) {
        // API返回格式为 {rankings: Array}
        this.setData({ departmentRankings: res.rankings });
      } else if (res && Array.isArray(res)) {
        // 可能API直接返回了数组
        this.setData({ departmentRankings: res });
      } else {
        console.warn('学院排行数据格式不正确:', res);
        this.setData({ departmentRankings: [] });
      }
    }).catch(err => {
      console.error('加载学院排行失败:', err);
      wx.showToast({
        title: '加载学院排行失败',
        icon: 'none'
      });
      this.setData({ departmentRankings: [] });
      throw err;
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
    console.log('导航到课程详情，课程ID:', courseId, '类型:', typeof courseId);
    
    // 增强ID验证
    if (!courseId) {
      console.error('课程ID为空');
      wx.showToast({
        title: '课程ID错误',
        icon: 'none'
      });
      return;
    }
    
    // 转换为字符串并去除空格
    const idStr = String(courseId).trim();
    if (idStr === '') {
      console.error('课程ID为空字符串');
      wx.showToast({
        title: '课程ID错误',
        icon: 'none'
      });
      return;
    }
    
    // 编码ID以确保特殊字符正确传递
    const encodedId = encodeURIComponent(idStr);
    console.log('编码后的课程ID:', encodedId);
    
    // 使用正确的路径
    wx.navigateTo({
        url: `/pages/course_detail/course_detail?id=${encodedId}`
      });
      console.log('导航到课程详情页:', `/pages/course_detail/course_detail?id=${encodedId}`);
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