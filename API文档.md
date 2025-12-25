# 评课系统API文档

## 目录

1. [文档目的](#文档目的)
2. [API概述](#api概述)
3. [API规范](#api规范)
4. [认证方式](#认证方式)
5. [课程相关API](#课程相关api)
6. [教师相关API](#教师相关api)
7. [评价相关API](#评价相关api)
8. [讨论相关API](#讨论相关api)
9. [评论相关API](#评论相关api)
10. [排行榜相关API](#排行榜相关api)
11. [错误码说明](#错误码说明)

## 文档目的

本文档旨在详细描述评课系统的API接口，为前端开发人员提供清晰的接口调用指南。

## API概述

评课系统API采用RESTful设计风格，提供了课程、评价、讨论和排行榜等核心功能的接口。所有API接口均支持JSON格式的数据交换，使用HTTP方法（GET、POST、PUT、DELETE）表示操作类型。

### 基础URL

开发环境：`http://<开发环境后端服务IP>:5001/api` (前端frontend/app.js中配置)

生产环境：`https://<生产环境后端服务IP>:5001/api`

**注意：** 前端代码中通过request.js自动添加了`/api`前缀，因此实际API调用路径会被转换为`http://192.168.1.103:5001/api/{endpoint}`或`https://api.pingke.edu.cn/api/{endpoint}`。后端API本身不需要`/api`前缀，该前缀由前端自动添加。

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

系统使用 JWT (JSON Web Token) 进行认证。用户通过微信登录后，后端会生成一个 JWT token，前端需要在后续请求的 Authorization 头中携带该 token。

**请求头示例**：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 认证相关 API

#### 1. 微信登录

- **URL**: `/api/auth/wechat-login`
- **方法**: `POST`
- **功能**: 通过微信 code 获取 openid 并创建/查找用户，生成 JWT token
- **是否需要认证**: 否

#### 请求体

```json
{
  "code": "微信登录code"
}
```

#### 成功响应

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "user": {
    "id": 1,
    "nickname": "微信用户",
    "avatar_url": "https://thirdwx.qlogo.cn/..."
  }
}
```

#### 2. 更新用户信息

- **URL**: `/api/users/{user_id}`
- **方法**: `PUT`
- **功能**: 更新用户信息
- **是否需要认证**: 是

#### 请求体

```json
{
  "nickname": "张三",
  "avatar_url": "https://thirdwx.qlogo.cn/..."
}
```

#### 成功响应

```json
{
  "id": 1,
  "nickname": "张三",
  "avatar_url": "https://thirdwx.qlogo.cn/..."
}
```

#### 3. 获取当前用户信息

- **URL**: `/api/me`
- **方法**: `GET`
- **功能**: 获取当前登录用户信息及统计数据
- **是否需要认证**: 是

#### 成功响应

```json
{
  "id": 1,
  "nickname": "张三",
  "avatar_url": "https://thirdwx.qlogo.cn/...",
  "openid": "oXz8R5XXXXXXXXXXXXXXXX",
  "created_at": "2024-01-15T10:30:00Z",
  "stats": {
    "evaluations_count": 5,
    "discussions_count": 3,
    "comments_count": 12,
    "total_posts": 20
  }
}
```

#### 4. 更新当前用户昵称

- **URL**: `/api/me/nickname`
- **方法**: `PUT`
- **功能**: 更新当前用户的昵称
- **是否需要认证**: 是

#### 请求体

```json
{
  "nickname": "新昵称"
}
```

#### 成功响应

```json
{
  "id": 1,
  "nickname": "新昵称",
  "avatar_url": "https://thirdwx.qlogo.cn/..."
}
```

#### 5. 获取指定用户评价列表

- **URL**: `/api/users/{user_id}/evaluations`
- **方法**: `GET`
- **功能**: 获取指定用户的评价列表
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页数量，默认20 |

#### 成功响应

```json
{
  "evaluations": [
    {
      "id": 1,
      "course_id": 1,
      "score": 5,
      "workload_score": 4,
      "content_score": 5,
      "teaching_score": 5,
      "tags": "干货,易懂",
      "comment": "老师讲得非常好",
      "likes": 10,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

#### 6. 获取指定用户讨论列表

- **URL**: `/api/users/{user_id}/discussions`
- **方法**: `GET`
- **功能**: 获取指定用户的讨论列表（包括评论和回复）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| per_page | integer | 否 | 每页数量，默认20 |

#### 成功响应

```json
{
  "discussions": [
    {
      "id": 1,
      "course_id": 1,
      "user_id": 1,
      "user_name": "张三",
      "content": "请问这门课难不难？",
      "parent_id": null,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "type": "discussion",
      "likes_count": 5,
      "parent_author": null,
      "parent_content": null
    }
  ],
  "total": 30,
  "page": 1,
  "per_page": 20
}

## 课程相关API

### 1. 获取课程列表

#### 请求信息

- **URL**: `/api/courses`
- **方法**: `GET`
- **功能**: 获取课程列表，支持筛选、排序和分页
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，兼容per_page参数 |
| keyword | string | 否 | 搜索关键词 |
| sort_by | string | 否 | 排序方式，可选值：`score`（按评分）, `created_at`（按创建时间）, `hot`（按热度）, `default`（默认排序，等同于created_at） |
| teacher_id | integer | 否 | 教师ID筛选 |
| department | string | 否 | 学院筛选条件（单个学院） |
| departments | string | 否 | 学院筛选条件（多个学院，逗号分隔） |
| semester | string | 否 | 学期筛选 |

#### 示例请求

```
GET /api/courses?keyword=计算机&sort_by=score&page=1&page_size=10
```

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "courses": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "description": "介绍数据结构基本概念和算法",
        "credit": 3,
        "semester": "2024春",
        "teacher": {
          "id": 1,
          "name": "张三",
          "department": "计算机学院",
          "title": "教授"
        },
        "average_score": 4.5,
        "evaluation_count": 20
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

### 2. 获取课程详情

#### 请求信息

- **URL**: `/api/courses/{course_id}`
- **方法**: `GET`
- **功能**: 获取课程详细信息，包含评分统计
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 示例请求

```
GET /api/courses/1
```

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "id": 1,
    "course_code": "CS101",
    "name": "数据结构",
    "description": "介绍数据结构基本概念和算法",
    "credit": 3,
    "semester": "2024春",
    "teacher": {
      "id": 1,
      "name": "张三",
      "department": "计算机学院",
      "title": "教授"
    },
    "average_score": 4.5,
    "evaluation_count": 20,
    "workload_average": 4.2,
    "content_average": 4.6,
    "teaching_average": 4.8,
    "tags_distribution": {
      "干货": 15,
      "易懂": 12,
      "实用": 8
    }
  }
}
```

### 3. 添加课程

#### 请求信息

- **URL**: `/api/courses`
- **方法**: `POST`
- **功能**: 添加新课程
- **是否需要认证**: 是

#### 请求体

```json
{
  "course_code": "CS101",
  "name": "数据结构",
  "description": "介绍数据结构基本概念和算法",
  "credit": 3,
  "semester": "2024春",
  "teacher_id": 1
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 1,
    "course_code": "CS101",
    "name": "数据结构",
    "description": "介绍数据结构基本概念和算法",
    "credit": 3,
    "semester": "2024春",
    "teacher_id": 1
  }
}
```

### 4. 更新课程

#### 请求信息

- **URL**: `/api/courses/{course_id}`
- **方法**: `PUT`
- **功能**: 更新课程信息
- **是否需要认证**: 是

#### 请求体

```json
{
  "course_code": "CS101",
  "name": "数据结构",
  "description": "更新后的描述",
  "credit": 3,
  "semester": "2024春",
  "teacher_id": 1
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "course_code": "CS101",
    "name": "数据结构",
    "description": "更新后的描述",
    "credit": 3,
    "semester": "2024春",
    "teacher_id": 1
  }
}
```

### 5. 删除课程

#### 请求信息

- **URL**: `/api/courses/{course_id}`
- **方法**: `DELETE`
- **功能**: 删除课程
- **是否需要认证**: 是

#### 成功响应

```json
{
  "success": true,
  "message": "删除成功"
}
```

### 6. 获取课程热门标签

#### 请求信息

- **URL**: `/api/courses/{course_id}/popular_tags`
- **方法**: `GET`
- **功能**: 获取指定课程的热门标签
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "tags": ["干货", "易懂", "实用", "有趣", "深入"]
  }
}
```

### 7. 获取课程评分分布

#### 请求信息

- **URL**: `/api/courses/{course_id}/rating_distribution`
- **方法**: `GET`
- **功能**: 获取课程评分分布
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | integer | 是 | 课程ID |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "distribution": {
      "1": 1,
      "2": 2,
      "3": 5,
      "4": 8,
      "5": 14
    }
  }
}

## 教师相关API

### 1. 获取教师列表

#### 请求信息

- **URL**: `/api/teachers`
- **方法**: `GET`
- **功能**: 获取所有教师列表
- **是否需要认证**: 否

#### 成功响应

```json
[
  {
    "id": 1,
    "name": "张三",
    "department": "计算机学院",
    "title": "教授",
    "introduction": "张三教授是计算机学院的知名教授...",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### 2. 添加教师

#### 请求信息

- **URL**: `/api/teachers`
- **方法**: `POST`
- **功能**: 添加新教师
- **是否需要认证**: 是

#### 请求体

```json
{
  "name": "张三",
  "department": "计算机学院",
  "title": "教授",
  "introduction": "张三教授是计算机学院的知名教授..."
}
```

#### 成功响应

```json
{
  "id": 1,
  "name": "张三",
  "department": "计算机学院",
  "title": "教授",
  "introduction": "张三教授是计算机学院的知名教授...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. 获取单个教师信息

#### 请求信息

- **URL**: `/api/teachers/{teacher_id}`
- **方法**: `GET`
- **功能**: 获取指定教师的详细信息
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| teacher_id | integer | 是 | 教师ID |

#### 成功响应

```json
{
  "id": 1,
  "name": "张三",
  "department": "计算机学院",
  "title": "教授",
  "introduction": "张三教授是计算机学院的知名教授...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. 更新教师信息

#### 请求信息

- **URL**: `/api/teachers/{teacher_id}`
- **方法**: `PUT`
- **功能**: 更新指定教师的信息
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| teacher_id | integer | 是 | 教师ID |

#### 请求体

```json
{
  "name": "张三",
  "department": "计算机学院",
  "title": "教授",
  "introduction": "张三教授是计算机学院的知名教授..."
}
```

#### 成功响应

```json
{
  "id": 1,
  "name": "张三",
  "department": "计算机学院",
  "title": "教授",
  "introduction": "张三教授是计算机学院的知名教授...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 5. 删除教师

#### 请求信息

- **URL**: `/api/teachers/{teacher_id}`
- **方法**: `DELETE`
- **功能**: 删除指定教师
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| teacher_id | integer | 是 | 教师ID |

#### 成功响应

```json
{
  "message": "Teacher deleted successfully"
}
```

#### 错误响应

```json
{
  "error": "Cannot delete teacher with associated courses"
}
```

### 6. 获取教师的所有课程

#### 请求信息

- **URL**: `/api/teachers/{teacher_id}/courses`
- **方法**: `GET`
- **功能**: 获取指定教师的所有课程及其评分信息
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| teacher_id | integer | 是 | 教师ID |

#### 成功响应

```json
[
  {
    "id": 1,
    "course_code": "CS101",
    "name": "数据结构",
    "description": "介绍数据结构基本概念和算法",
    "credit": 3,
    "semester": "2024春",
    "teacher_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "avg_score": 4.5,
    "evaluation_count": 20
  }
]
```
```

## 评价相关API

### 1. 获取评价列表

#### 请求信息

- **URL**: `/api/evaluations`
- **方法**: `GET`
- **功能**: 获取评价列表，支持分页、筛选和排序
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，兼容per_page参数 |
| course_id | integer | 否 | 课程ID筛选 |
| user_id | integer | 否 | 用户ID筛选 |
| sort_by | string | 否 | 排序方式，可选值：`score`（按评分）, `created_at`（按创建时间）, `likes`（按点赞数） |
| min_score | integer | 否 | 最低评分筛选 |
| max_score | integer | 否 | 最高评分筛选 |
| tags | string | 否 | 标签筛选（逗号分隔） |

#### 示例请求

```
GET /api/evaluations?course_id=1&sort_by=likes&page=1&page_size=10
```

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "evaluations": [
      {
        "id": 1,
        "course_id": 1,
        "user": {
          "id": 1,
          "nickname": "张三",
          "avatar_url": "https://thirdwx.qlogo.cn/..."
        },
        "score": 5,
        "workload_score": 4,
        "content_score": 5,
        "teaching_score": 5,
        "tags": "干货,易懂",
        "comment": "老师讲得非常好",
        "likes": 10,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 10
  }
}
```

### 2. 获取单个评价详情

#### 请求信息

- **URL**: `/api/evaluations/{evaluation_id}`
- **方法**: `GET`
- **功能**: 获取单个评价的详细信息
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| evaluation_id | integer | 是 | 评价ID |

#### 示例请求

```
GET /api/evaluations/1
```

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "course": {
      "id": 1,
      "name": "数据结构",
      "course_code": "CS101"
    },
    "user": {
      "id": 1,
      "nickname": "张三",
      "avatar_url": "https://thirdwx.qlogo.cn/..."
    },
    "score": 5,
    "workload_score": 4,
    "content_score": 5,
    "teaching_score": 5,
    "tags": "干货,易懂",
    "comment": "老师讲得非常好",
    "likes": 10,
    "created_at": "2024-01-15T10:30:00Z",
    "is_liked": false
  }
}
```

### 3. 添加评价

#### 请求信息

- **URL**: `/api/evaluations`
- **方法**: `POST`
- **功能**: 添加新评价
- **是否需要认证**: 是

#### 请求体

```json
{
  "course_id": 1,
  "score": 5,
  "workload_score": 4,
  "content_score": 5,
  "teaching_score": 5,
  "tags": "干货,易懂",
  "comment": "老师讲得非常好"
}
```

#### 示例请求

```
POST /api/evaluations
Content-Type: application/json

{
  "course_id": 1,
  "score": 5,
  "workload_score": 4,
  "content_score": 5,
  "teaching_score": 5,
  "tags": "干货,易懂",
  "comment": "老师讲得非常好"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": 1,
    "score": 5,
    "workload_score": 4,
    "content_score": 5,
    "teaching_score": 5,
    "tags": "干货,易懂",
    "comment": "老师讲得非常好",
    "likes": 0,
    "created_at": "2024-01-15T10:30:00Z"
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

### 4. 更新评价

#### 请求信息

- **URL**: `/api/evaluations/{evaluation_id}`
- **方法**: `PUT`
- **功能**: 更新评价信息
- **是否需要认证**: 是

#### 请求体

```json
{
  "score": 5,
  "workload_score": 4,
  "content_score": 5,
  "teaching_score": 5,
  "tags": "干货,易懂",
  "comment": "更新后的评论内容"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": 1,
    "score": 5,
    "workload_score": 4,
    "content_score": 5,
    "teaching_score": 5,
    "tags": "干货,易懂",
    "comment": "更新后的评论内容",
    "likes": 10,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 5. 删除评价

#### 请求信息

- **URL**: `/api/evaluations/{evaluation_id}`
- **方法**: `DELETE`
- **功能**: 删除评价
- **是否需要认证**: 是

#### 成功响应

```json
{
  "success": true,
  "message": "删除成功"
}
```

### 6. 点赞/取消点赞评价

#### 请求信息

- **URL**: `/api/evaluations/{evaluation_id}/like`
- **方法**: `POST`
- **功能**: 点赞或取消点赞评价
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| evaluation_id | integer | 是 | 评价ID |

#### 示例请求

```
POST /api/evaluations/1/like
```

#### 成功响应

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
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

### 1. 获取讨论列表

#### 请求信息

- **URL**: `/api/discussions`
- **方法**: `GET`
- **功能**: 获取讨论列表，支持分页和筛选
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，兼容per_page参数 |
| course_id | integer | 否 | 课程ID筛选 |
| parent_id | integer | 否 | 父讨论ID筛选（用于获取回复） |
| sort_by | string | 否 | 排序方式，可选值：`created_at`（按创建时间）, `likes`（按点赞数）, `replies`（按回复数） |

#### 示例请求

```
GET /api/discussions?course_id=1&page=1&page_size=10
```

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "discussions": [
      {
        "id": 1,
        "course_id": 1,
        "user": {
          "id": 1,
          "nickname": "张三",
          "avatar_url": "https://thirdwx.qlogo.cn/..."
        },
        "content": "请问这门课难不难？",
        "parent_id": null,
        "likes": 5,
        "replies_count": 2,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 30,
    "page": 1,
    "page_size": 10
  }
}
```

### 2. 添加讨论

#### 请求信息

- **URL**: `/api/discussions`
- **方法**: `POST`
- **功能**: 添加新讨论或回复
- **是否需要认证**: 是

#### 请求体

```json
{
  "course_id": 1,
  "content": "请问这门课难不难？",
  "parent_id": null  // 回复时填写父讨论ID
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": 1,
    "content": "请问这门课难不难？",
    "parent_id": null,
    "likes": 0,
    "replies_count": 0,
    "created_at": "2024-01-15T10:30:00Z"
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

### 3. 更新讨论

#### 请求信息

- **URL**: `/api/discussions/{discussion_id}`
- **方法**: `PUT`
- **功能**: 更新讨论内容
- **是否需要认证**: 是

#### 请求体

```json
{
  "content": "更新后的讨论内容"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": 1,
    "content": "更新后的讨论内容",
    "parent_id": null,
    "likes": 5,
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 4. 删除讨论

#### 请求信息

- **URL**: `/api/discussions/{discussion_id}`
- **方法**: `DELETE`
- **功能**: 删除讨论
- **是否需要认证**: 是

#### 成功响应

```json
{
  "success": true,
  "message": "删除成功"
}
```

### 5. 添加讨论回复

#### 请求信息

- **URL**: `/api/discussions/{discussion_id}/replies`
- **方法**: `POST`
- **功能**: 添加对指定讨论的回复
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| discussion_id | integer | 是 | 讨论ID |

#### 请求体

```json
{
  "content": "回复内容"
}
```

#### 成功响应

```json
{
  "id": 2,
  "course_id": 1,
  "user_id": 2,
  "user_name": "李四",
  "content": "回复内容",
  "parent_id": 1,
  "created_at": "2024-01-16T10:30:00Z",
  "updated_at": "2024-01-16T10:30:00Z",
  "author": "李四",
  "likes_count": 0,
  "is_liked": false
}
```

#### 错误响应

```json
{
  "message": "缺少内容"
}
```

### 6. 点赞/取消点赞讨论

#### 请求信息

- **URL**: `/api/discussions/{discussion_id}/like`
- **方法**: `POST`
- **功能**: 点赞或取消点赞讨论
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| discussion_id | integer | 是 | 讨论ID |

#### 成功响应

```json
{
  "message": "操作成功",
  "likes_count": 6,
  "is_liked": true
}
```

## 评论相关API

### 1. 获取评论列表

#### 请求信息

- **URL**: `/api/comments`
- **方法**: `GET`
- **功能**: 获取评论列表，支持分页和筛选
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，兼容per_page参数 |
| course_id | integer | 否 | 课程ID筛选 |
| parent_id | integer | 否 | 父评论ID筛选（用于获取回复） |

#### 示例请求

```
GET /api/comments?course_id=1&page=1&page_size=10
```

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "comments": [
      {
        "id": 1,
        "course_id": 1,
        "user": {
          "id": 1,
          "nickname": "张三",
          "avatar_url": "https://thirdwx.qlogo.cn/..."
        },
        "content": "请问这门课难不难？",
        "likes": 5,
        "created_at": "2024-01-15T10:30:00Z",
        "replies_count": 2
      }
    ],
    "total": 30,
    "page": 1,
    "page_size": 10
  }
}
```

### 2. 添加评论

#### 请求信息

- **URL**: `/api/comments`
- **方法**: `POST`
- **功能**: 添加新评论或回复
- **是否需要认证**: 是

#### 请求体

```json
{
  "course_id": 1,
  "content": "请问这门课难不难？",
  "parent_id": null  // 回复时填写父评论ID
}
```

#### 示例请求

```
POST /api/comments
Content-Type: application/json

{
  "course_id": 1,
  "content": "请问这门课难不难？",
  "parent_id": null
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "创建成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": 1,
    "content": "请问这门课难不难？",
    "likes": 0,
    "created_at": "2024-01-15T10:30:00Z"
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

### 3. 更新评论

#### 请求信息

- **URL**: `/api/comments/{comment_id}`
- **方法**: `PUT`
- **功能**: 更新评论内容
- **是否需要认证**: 是

#### 请求体

```json
{
  "content": "更新后的评论内容"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "course_id": 1,
    "user_id": 1,
    "content": "更新后的评论内容",
    "likes": 5,
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 4. 删除评论

#### 请求信息

- **URL**: `/api/comments/{comment_id}`
- **方法**: `DELETE`
- **功能**: 删除评论
- **是否需要认证**: 是

#### 成功响应

```json
{
  "success": true,
  "message": "删除成功"
}

### 5. 获取评论的回复列表

#### 请求信息

- **URL**: `/api/comments/{comment_id}/replies`
- **方法**: `GET`
- **功能**: 获取指定评论的所有回复
- **是否需要认证**: 否

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| comment_id | integer | 是 | 评论ID |

#### 成功响应

```json
[
  {
    "id": 2,
    "course_id": 1,
    "user": {
      "id": 2,
      "nickname": "李四",
      "avatar_url": "https://thirdwx.qlogo.cn/..."
    },
    "content": "谢谢分享！",
    "parent_id": 1,
    "likes": 3,
    "created_at": "2024-01-16T10:30:00Z",
    "updated_at": "2024-01-16T10:30:00Z"
  }
]
```

### 6. 点赞/取消点赞评论

#### 请求信息

- **URL**: `/api/comments/{comment_id}/like`
- **方法**: `POST`
- **功能**: 点赞或取消点赞评论
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| comment_id | integer | 是 | 评论ID |

#### 成功响应

```json
{
  "message": "操作成功",
  "likes_count": 6,
  "is_liked": true
}
```

#### 错误响应

```json
{
  "error": "请先登录",
  "message": "操作失败"
}
```

### 7. 点赞/取消点赞回复

#### 请求信息

- **URL**: `/api/replies/{reply_id}/like`
- **方法**: `POST`
- **功能**: 点赞或取消点赞回复
- **是否需要认证**: 是

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| reply_id | integer | 是 | 回复ID |

#### 成功响应

```json
{
  "message": "操作成功",
  "likes_count": 6,
  "is_liked": true
}
```

#### 错误响应

```json
{
  "error": "请先登录",
  "message": "操作失败"
}
```

## 排行榜相关API

### 1. 获取统一排行榜接口

#### 请求信息

- **URL**: `/api/rankings`
- **方法**: `GET`
- **功能**: 根据type参数获取不同类型的排行榜数据（课程、教师、标签、学院）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| type | string | 否 | 排行榜类型（courses/teachers/tags/departments），默认courses |
| semester | string | 否 | 学期筛选（仅courses类型有效） |
| department | string | 否 | 学院筛选 |
| limit | integer | 否 | 返回数量，默认10 |

#### 示例请求

```
GET /api/rankings?type=courses&limit=10
GET /api/rankings?type=tags&limit=20
```

#### 成功响应（courses类型）

```json
{
  "list": [
    {
      "id": 1,
      "name": "计算机基础",
      "code": "CS101",
      "teacher": "张教授",
      "score": 4.8,
      "count": 50
    },
    // 更多排名...
  ]
}
```

#### 成功响应（teachers类型）

```json
{
  "list": [
    {
      "id": 1,
      "name": "张教授",
      "department": "计算机学院",
      "score": 4.8,
      "count": 120
    },
    // 更多排名...
  ]
}
```

#### 成功响应（tags类型）

```json
{
  "list": [
    {
      "name": "给分好",
      "count": 156
    },
    {
      "name": "教学认真",
      "count": 145
    },
    // 更多排名...
  ]
}
```

#### 成功响应（departments类型）

```json
{
  "list": [
    {
      "name": "计算机学院",
      "score": 4.5,
      "count": 50
    },
    // 更多排名...
  ]
}
```

#### 错误响应

```json
{
  "message": "无效的排行榜类型"
}
```

### 2. 获取课程排行榜（详细版）

#### 请求信息

- **URL**: `/api/rankings/courses`
- **方法**: `GET`
- **功能**: 获取详细的课程排行榜数据
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| semester | string | 否 | 学期筛选 |
| department | string | 否 | 学院筛选 |
| limit | integer | 否 | 返回数量，默认10 |
| time_range | string | 否 | 时间范围（week/month/year/all），默认all |

#### 示例请求

```
GET /api/rankings/courses?department=计算机学院&limit=20&time_range=month
```

#### 成功响应

```json
{
  "rankings": [
    {
      "course_id": 1,
      "course_name": "计算机基础",
      "course_code": "CS101",
      "teacher_name": "张教授",
      "avg_score": 4.8,
      "evaluation_count": 50,
      "rank": 1
    },
    // 更多排名...
  ]
}
```

### 3. 获取教师排行榜

#### 请求信息

- **URL**: `/api/rankings/teachers`
- **方法**: `GET`
- **功能**: 获取教师排行榜
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| department | string | 否 | 学院筛选 |
| limit | integer | 否 | 返回数量，默认10 |
| time_range | string | 否 | 时间范围（week/month/year/all），默认all |

#### 成功响应

```json
{
  "rankings": [
    {
      "teacher_id": 1,
      "teacher_name": "张教授",
      "department": "计算机学院",
      "title": "教授",
      "avg_score": 4.8,
      "evaluation_count": 120,
      "course_count": 5,
      "rank": 1
    },
    // 更多排名...
  ]
}
```

### 4. 获取标签排行榜

#### 请求信息

- **URL**: `/api/rankings/tags`
- **方法**: `GET`
- **功能**: 获取热门标签排行榜
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认20 |

#### 示例请求

```
GET /api/rankings/tags?limit=10
```

#### 成功响应

```json
{
  "rankings": [
    {
      "tag": "给分好",
      "count": 156,
      "rank": 1
    },
    {
      "tag": "教学认真",
      "count": 145,
      "rank": 2
    },
    // 更多排名...
  ]
}
```

### 5. 获取学院排行榜

#### 请求信息

- **URL**: `/api/rankings/departments`
- **方法**: `GET`
- **功能**: 获取各学院课程平均评分排行榜
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认10 |

#### 成功响应

```json
{
  "rankings": [
    {
      "department": "计算机学院",
      "avg_score": 4.5,
      "course_count": 50,
      "evaluation_count": 1200,
      "rank": 1
    },
    // 更多排名...
  ]
}
```

### 6. 获取课程排行榜（旧版 - 已废弃）

#### 请求信息

- **URL**: `/api/rankings/score`
- **方法**: `GET`
- **功能**: 获取按综合评分排序的课程排行榜（旧版API，已废弃）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认10 |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher": {
          "id": 1,
          "name": "张三",
          "department": "计算机学院"
        },
        "average_score": 4.9,
        "evaluation_count": 50
      }
    ]
  }
}
```

### 7. 获取热度排行榜（旧版 - 已废弃）

#### 请求信息

- **URL**: `/api/rankings/hot`
- **方法**: `GET`
- **功能**: 获取按热度排序的课程排行榜（旧版API，已废弃）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认10 |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher": {
          "id": 1,
          "name": "张三",
          "department": "计算机学院"
        },
        "average_score": 4.5,
        "evaluation_count": 100,
        "hot_score": 1200
      }
    ]
  }
}
```

### 8. 获取 workload 评分排行榜（旧版 - 已废弃）

#### 请求信息

- **URL**: `/api/rankings/workload`
- **方法**: `GET`
- **功能**: 获取按 workload 评分排序的课程排行榜（最低workload在前，旧版API，已废弃）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认10 |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher": {
          "id": 1,
          "name": "张三",
          "department": "计算机学院"
        },
        "average_score": 4.5,
        "workload_score": 2.1,
        "evaluation_count": 30
      }
    ]
  }
}
```

### 9. 获取内容质量排行榜（旧版 - 已废弃）

#### 请求信息

- **URL**: `/api/rankings/content`
- **方法**: `GET`
- **功能**: 获取按内容质量评分排序的课程排行榜（旧版API，已废弃）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认10 |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher": {
          "id": 1,
          "name": "张三",
          "department": "计算机学院"
        },
        "average_score": 4.8,
        "content_score": 4.9,
        "evaluation_count": 45
      }
    ]
  }
}
```

### 10. 获取教学评分排行榜（旧版 - 已废弃）

#### 请求信息

- **URL**: `/api/rankings/teaching`
- **方法**: `GET`
- **功能**: 获取按教学评分排序的课程排行榜（旧版API，已废弃）
- **是否需要认证**: 否

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认10 |

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher": {
          "id": 1,
          "name": "张三",
          "department": "计算机学院"
        },
        "average_score": 4.7,
        "teaching_score": 4.9,
        "evaluation_count": 40
      }
    ]
  }
}
```

### 11. 获取所有排行榜（前端专用 - 已废弃）

#### 请求信息

- **URL**: `/api/rankings-frontend`
- **方法**: `GET`
- **功能**: 获取所有类型的排行榜数据，专为前端页面设计（旧版API，已废弃）
- **是否需要认证**: 否

#### 成功响应

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "score_rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher_name": "张三",
        "teacher_department": "计算机学院",
        "average_score": 4.9,
        "evaluation_count": 50
      }
    ],
    "hot_rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher_name": "张三",
        "teacher_department": "计算机学院",
        "average_score": 4.5,
        "evaluation_count": 100,
        "hot_score": 1200
      }
    ],
    "workload_rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher_name": "张三",
        "teacher_department": "计算机学院",
        "average_score": 4.5,
        "workload_score": 2.1,
        "evaluation_count": 30
      }
    ],
    "content_rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher_name": "张三",
        "teacher_department": "计算机学院",
        "average_score": 4.8,
        "content_score": 4.9,
        "evaluation_count": 45
      }
    ],
    "teaching_rankings": [
      {
        "id": 1,
        "course_code": "CS101",
        "name": "数据结构",
        "teacher_name": "张三",
        "teacher_department": "计算机学院",
        "average_score": 4.7,
        "teaching_score": 4.9,
        "evaluation_count": 40
      }
    ]
  }
}
```

## 错误码说明

系统使用标准HTTP状态码表示请求结果：

- `200`: 请求成功
- `400`: 请求参数错误或验证失败
  - 示例错误消息：`"缺少code参数"`, `"昵称不能为空"`, `"内容不能为空"`, `"You have already evaluated this course"`
- `401`: 未授权，需要登录
  - 示例错误消息：`"请先登录"`
- `403`: 禁止访问，权限不足
  - 示例错误消息：`"Unauthorized to update this comment"`, `"Unauthorized to delete this evaluation"`
- `404`: 资源不存在
  - 示例错误消息：`"Course not found"`, `"User not found"`, `"Evaluation not found"`
- `500`: 服务器内部错误

## 数据模型

### 1. 用户模型 (User)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 用户唯一标识 |
| openid | string | 微信openid，唯一 |
| nickname | string | 用户昵称 |
| avatar_url | string | 用户头像URL |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2. 课程模型 (Course)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 课程唯一标识 |
| course_code | string | 课程代码，唯一 |
| name | string | 课程名称 |
| description | string | 课程描述 |
| credit | float | 学分 |
| semester | string | 学期 |
| teacher_id | integer | 教师ID，关联teachers表 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 3. 教师模型 (Teacher)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 教师唯一标识 |
| name | string | 教师姓名 |
| department | string | 所属学院 |
| title | string | 职称 |
| introduction | text | 教师介绍 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 4. 评价模型 (Evaluation)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 评价唯一标识 |
| course_id | integer | 课程ID，关联courses表 |
| user_id | integer | 用户ID，关联users表 |
| score | float | 综合评分（1-5分） |
| workload_score | float | 工作量评分（1-5分） |
| content_score | float | 内容评分（1-5分） |
| teaching_score | float | 教学评分（1-5分） |
| tags | string | 标签，逗号分隔 |
| comment | text | 评价内容 |
| is_anonymous | boolean | 是否匿名评价 |
| user_name | string | 用户昵称或"匿名用户" |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 5. 评论模型 (Comment)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 评论唯一标识 |
| course_id | integer | 课程ID，关联courses表 |
| user_id | integer | 用户ID，关联users表 |
| user_name | string | 用户昵称，用于兼容旧数据 |
| content | text | 评论内容 |
| parent_id | integer | 父评论ID（用于回复），可为空 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 6. 点赞模型 (Like)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 点赞唯一标识 |
| user_id | integer | 用户ID，关联users表 |
| target_type | string | 目标类型（comment或evaluation） |
| target_id | integer | 目标ID |
| created_at | datetime | 创建时间 |

---

**版本信息：**
- 文档版本：1.0.0
- 发布日期：2025-11-11

**版权声明：**
本文档版权归评课系统开发团队所有，未经授权，不得复制或传播。