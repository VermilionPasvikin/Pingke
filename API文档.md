# 评课系统API文档

## 目录

1. [文档目的](#文档目的)
2. [API概述](#api概述)
3. [API规范](#api规范)
4. [认证方式](#认证方式)
5. [课程相关API](#课程相关api)
6. [评价相关API](#评价相关api)
7. [讨论相关API](#讨论相关api)
8. [排行榜相关API](#排行榜相关api)
9. [错误码说明](#错误码说明)

## 文档目的

本文档旨在详细描述评课系统的API接口，为前端开发人员提供清晰的接口调用指南。

## API概述

评课系统API采用RESTful设计风格，提供了课程、评价、讨论和排行榜等核心功能的接口。所有API接口均支持JSON格式的数据交换，使用HTTP方法（GET、POST、PUT、DELETE）表示操作类型。

### 基础URL

开发环境：`http://localhost:5000/api`

生产环境：`https://api.pingke.edu.cn/api`

## API规范

### 请求格式

#### HTTP方法

| 方法 | 描述 |
|------|------|
| GET | 获取资源 |
| POST | 创建资源 |
| PUT | 更新资源 |
| DELETE | 删除资源 |

#### 请求头

所有请求必须包含以下头信息：

```
Content-Type: application/json
Accept: application/json
```

对于需要认证的请求，还需包含：

```
Authorization: Bearer {token}
```

### 响应格式

所有API响应均采用统一格式：

#### 成功响应

```json
{
  "success": true,
  "message": "操作成功",
  "data": { /* 返回的数据 */ },
  "meta": { /* 元数据，如分页信息 */ }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": 400,
  "detail": { /* 详细错误信息 */ }
}
```

## 认证方式

目前系统使用简单的用户标识进行区分，未来将升级为JWT认证机制。

### 当前认证方式

在请求中通过`user_id`参数标识用户身份。此方式仅用于区分不同用户，不进行严格的身份验证。

## 课程相关API

### 1. 获取课程列表

#### 请求信息

- **URL**: `/courses`
- **方法**: `GET`
- **功能**: 获取课程列表，支持筛选和分页
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| department | string | 否 | 学院筛选条件 |
| semester | string | 否 | 学期筛选条件 |
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页数量，默认20 |

#### 示例请求

```
GET /api/courses?department=计算机学院&semester=2023-2024-1&page=1&per_page=20
```

#### 成功响应

```json
{
  "success": true,
  "message": "获取课程列表成功",
  "data": [
    {
      "id": 1,
      "course_code": "CS101",
      "name": "计算机基础",
      "description": "介绍计算机科学的基本概念和原理",
      "credit": 3,
      "semester": "2023-2024-1",
      "teacher_id": 1,
      "teacher_name": "张教授",
      "average_score": 4.5
    },
    // 更多课程...
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "参数错误",
  "error_code": 400,
  "detail": "page参数必须为正整数"
}
```

### 2. 获取课程详情

#### 请求信息

- **URL**: `/courses/{id}`
- **方法**: `GET`
- **功能**: 获取课程详细信息
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | integer | 是 | 课程ID |

#### 示例请求

```
GET /api/courses/1
```

#### 成功响应

```json
{
  "success": true,
  "message": "获取课程详情成功",
  "data": {
    "id": 1,
    "course_code": "CS101",
    "name": "计算机基础",
    "description": "介绍计算机科学的基本概念和原理",
    "credit": 3,
    "semester": "2023-2024-1",
    "teacher": {
      "id": 1,
      "name": "张教授",
      "department": "计算机学院",
      "title": "教授",
      "introduction": "从事计算机教育多年，研究方向为人工智能"
    },
    "evaluation_stats": {
      "total": 156,
      "average_score": 4.5,
      "workload_score": 4.3,
      "content_score": 4.6,
      "teaching_score": 4.7
    }
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "课程不存在",
  "error_code": 404
}
```

### 3. 搜索课程

#### 请求信息

- **URL**: `/courses/search`
- **方法**: `GET`
- **功能**: 根据关键词搜索课程
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页数量，默认20 |

#### 示例请求

```
GET /api/courses/search?keyword=计算机&page=1&per_page=20
```

#### 成功响应

```json
{
  "success": true,
  "message": "搜索成功",
  "data": [
    {
      "id": 1,
      "course_code": "CS101",
      "name": "计算机基础",
      "teacher_name": "张教授",
      "average_score": 4.5
    },
    // 更多搜索结果...
  ],
  "meta": {
    "total": 10,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "搜索关键词不能为空",
  "error_code": 400
}
```

## 评价相关API

### 1. 提交评价

#### 请求信息

- **URL**: `/courses/{course_id}/evaluations`
- **方法**: `POST`
- **功能**: 提交课程评价
- **是否需要认证**: 是（需要user_id）

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 请求体

```json
{
  "user_id": "string",
  "score": 5,
  "workload_score": 4,
  "content_score": 5,
  "teaching_score": 5,
  "tags": ["标签1", "标签2"],
  "comment": "评价内容"
}
```

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | string | 是 | 用户标识 |
| score | integer | 是 | 总评分（1-5分） |
| workload_score | integer | 是 | 工作量评分（1-5分） |
| content_score | integer | 是 | 内容评分（1-5分） |
| teaching_score | integer | 是 | 教学评分（1-5分） |
| tags | array | 否 | 评价标签列表 |
| comment | string | 否 | 评价内容 |

#### 示例请求

```
POST /api/courses/1/evaluations
Content-Type: application/json

{
  "user_id": "user123",
  "score": 5,
  "workload_score": 4,
  "content_score": 5,
  "teaching_score": 5,
  "tags": ["深入浅出", "案例丰富"],
  "comment": "这是一门非常好的课程，老师讲解清晰，内容充实。"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "评价提交成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": "user123",
    "score": 5,
    "workload_score": 4,
    "content_score": 5,
    "teaching_score": 5,
    "tags": ["深入浅出", "案例丰富"],
    "comment": "这是一门非常好的课程，老师讲解清晰，内容充实。",
    "created_at": "2023-11-01T12:00:00Z",
    "likes": 0
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "您已经评价过该课程",
  "error_code": 400,
  "detail": "一个用户只能评价一次"
}
```

### 2. 获取课程评价列表

#### 请求信息

- **URL**: `/courses/{course_id}/evaluations`
- **方法**: `GET`
- **功能**: 获取课程的评价列表
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页数量，默认20 |
| sort | string | 否 | 排序方式（latest/earliest/highest/lowest），默认latest |

#### 示例请求

```
GET /api/courses/1/evaluations?page=1&per_page=20&sort=highest
```

#### 成功响应

```json
{
  "success": true,
  "message": "获取评价列表成功",
  "data": [
    {
      "id": 1,
      "user_id": "user123",
      "score": 5,
      "workload_score": 4,
      "content_score": 5,
      "teaching_score": 5,
      "tags": ["深入浅出", "案例丰富"],
      "comment": "这是一门非常好的课程，老师讲解清晰，内容充实。",
      "created_at": "2023-11-01T12:00:00Z",
      "likes": 10
    },
    // 更多评价...
  ],
  "meta": {
    "total": 156,
    "page": 1,
    "per_page": 20,
    "total_pages": 8,
    "sort": "highest"
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "课程不存在",
  "error_code": 404
}
```

### 3. 点赞评价

#### 请求信息

- **URL**: `/evaluations/{evaluation_id}/like`
- **方法**: `POST`
- **功能**: 点赞或取消点赞评价
- **是否需要认证**: 是（需要user_id）

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| evaluation_id | integer | 是 | 评价ID |

#### 请求体

```json
{
  "user_id": "string"
}
```

#### 示例请求

```
POST /api/evaluations/1/like
Content-Type: application/json

{
  "user_id": "user456"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "点赞成功",
  "data": {
    "evaluation_id": 1,
    "likes": 11,
    "liked": true
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "评价不存在",
  "error_code": 404
}
```

## 讨论相关API

### 1. 获取课程讨论列表

#### 请求信息

- **URL**: `/courses/{course_id}/comments`
- **方法**: `GET`
- **功能**: 获取课程的讨论列表
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页数量，默认20 |
| sort | string | 否 | 排序方式（latest/earliest/hottest），默认latest |

#### 示例请求

```
GET /api/courses/1/comments?page=1&per_page=20&sort=latest
```

#### 成功响应

```json
{
  "success": true,
  "message": "获取讨论列表成功",
  "data": [
    {
      "id": 1,
      "user_id": "user123",
      "user_name": "学生A",
      "content": "这门课的作业难度怎么样？",
      "created_at": "2023-11-01T10:00:00Z",
      "likes": 5,
      "replies_count": 2,
      "replies": [
        {
          "id": 2,
          "user_id": "user456",
          "user_name": "学生B",
          "content": "作业难度适中，认真学的话没问题。",
          "created_at": "2023-11-01T11:00:00Z",
          "likes": 3
        }
      ]
    },
    // 更多讨论...
  ],
  "meta": {
    "total": 50,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "课程不存在",
  "error_code": 404
}
```

### 2. 发表讨论

#### 请求信息

- **URL**: `/courses/{course_id}/comments`
- **方法**: `POST`
- **功能**: 在课程讨论区发表内容
- **是否需要认证**: 是（需要user_id）

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 请求体

```json
{
  "user_id": "string",
  "user_name": "string",
  "content": "string"
}
```

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | string | 是 | 用户标识 |
| user_name | string | 是 | 用户昵称 |
| content | string | 是 | 讨论内容 |

#### 示例请求

```
POST /api/courses/1/comments
Content-Type: application/json

{
  "user_id": "user123",
  "user_name": "学生A",
  "content": "想请教一下期末考核的形式是什么？"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "讨论发表成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": "user123",
    "user_name": "学生A",
    "content": "想请教一下期末考核的形式是什么？",
    "created_at": "2023-11-01T13:00:00Z",
    "likes": 0,
    "replies_count": 0
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "内容不能为空",
  "error_code": 400
}
```

### 3. 回复讨论

#### 请求信息

- **URL**: `/comments/{comment_id}/replies`
- **方法**: `POST`
- **功能**: 回复现有讨论
- **是否需要认证**: 是（需要user_id）

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| comment_id | integer | 是 | 父评论ID |

#### 请求体

```json
{
  "user_id": "string",
  "user_name": "string",
  "content": "string"
}
```

#### 示例请求

```
POST /api/comments/1/replies
Content-Type: application/json

{
  "user_id": "user456",
  "user_name": "学生B",
  "content": "期末主要是闭卷考试，还有小组作业。"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "回复成功",
  "data": {
    "id": 2,
    "course_id": 1,
    "parent_id": 1,
    "user_id": "user456",
    "user_name": "学生B",
    "content": "期末主要是闭卷考试，还有小组作业。",
    "created_at": "2023-11-01T14:00:00Z",
    "likes": 0
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "父评论不存在",
  "error_code": 404
}
```

### 4. 点赞讨论

#### 请求信息

- **URL**: `/comments/{comment_id}/like`
- **方法**: `POST`
- **功能**: 点赞或取消点赞讨论
- **是否需要认证**: 是（需要user_id）

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| comment_id | integer | 是 | 评论ID |

#### 请求体

```json
{
  "user_id": "string"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "点赞成功",
  "data": {
    "comment_id": 1,
    "likes": 6,
    "liked": true
  }
}
```

## 排行榜相关API

### 1. 获取课程排行榜

#### 请求信息

- **URL**: `/rankings/courses`
- **方法**: `GET`
- **功能**: 获取课程排行榜
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| category | string | 否 | 排名分类（overall/workload/content/teaching），默认overall |
| limit | integer | 否 | 返回数量，默认20 |

#### 示例请求

```
GET /api/rankings/courses?category=overall&limit=20
```

#### 成功响应

```json
{
  "success": true,
  "message": "获取排行榜成功",
  "data": [
    {
      "course_id": 1,
      "course_name": "计算机基础",
      "course_code": "CS101",
      "teacher_name": "张教授",
      "score": 4.8,
      "rank": 1
    },
    {
      "course_id": 2,
      "course_name": "数据结构",
      "course_code": "CS201",
      "teacher_name": "李教授",
      "score": 4.7,
      "rank": 2
    },
    // 更多排名...
  ],
  "meta": {
    "category": "overall",
    "limit": 20
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "message": "无效的分类",
  "error_code": 400,
  "detail": "category参数必须是overall、workload、content或teaching之一"
}
```

## 错误码说明

| 错误码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复评价） |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用 |

---

**版本信息：**
- 文档版本：1.0.0
- 发布日期：2025-11-11

**版权声明：**
本文档版权归评课系统开发团队所有，未经授权，不得复制或传播。