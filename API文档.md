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

开发环境：`http://localhost:5001`

生产环境：`https://api.pingke.edu.cn`

**注意：** 前端代码中通过request.js自动添加了`/api`前缀，因此实际API调用路径会被转换为`http://localhost:5001/api/{endpoint}`或`https://api.pingke.edu.cn/api/{endpoint}`

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
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "openid": "oXz8R5XXXXXXXXXXXXXXXX",
      "nickname": "微信用户",
      "avatar_url": "https://thirdwx.qlogo.cn/...",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}```

#### 2. 更新用户信息

- **URL**: `/api/users/{user_id}`
- **方法**: `PUT`
- **功能**: 更新用户信息
- **是否需要认证**: 是

#### 请求体

```json
{
  "nickname": "张三",
  "avatar_url": "https://thirdwx.qlogo.cn/...",
  "gender": 1,
  "student_id": "20200001",
  "department": "计算机学院"
}
```

#### 成功响应

```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 1,
    "openid": "oXz8R5XXXXXXXXXXXXXXXX",
    "nickname": "张三",
    "avatar_url": "https://thirdwx.qlogo.cn/...",
    "gender": 1,
    "student_id": "20200001",
    "department": "计算机学院",
    "updated_at": "2024-01-15T10:30:00Z"
  }
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
| limit | integer | 否 | 每页数量，默认10 |
| search | string | 否 | 搜索关键词 |
| sort | string | 否 | 排序方式，可选值：`score`（按评分）, `created_at`（按创建时间）, `hot`（按热度） |
| teacher_id | integer | 否 | 教师ID筛选 |
| department | string | 否 | 学院筛选条件 |

#### 示例请求

```
GET /api/courses?search=计算机&sort=score&page=1&limit=10
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
    "limit": 10
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

- **URL**: `/api/courses/popular-tags`
- **方法**: `GET`
- **功能**: 获取课程相关的热门标签
- **是否需要认证**: 否
- **参数**:
  - `limit`: 返回数量，默认10

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

- **URL**: `/api/courses/{course_id}/rating-distribution`
- **方法**: `GET`
- **功能**: 获取课程评分分布
- **是否需要认证**: 否

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
| limit | integer | 否 | 每页数量，默认10 |
| course_id | integer | 否 | 课程ID筛选 |
| user_id | integer | 否 | 用户ID筛选 |
| sort | string | 否 | 排序方式，可选值：`score`（按评分）, `created_at`（按创建时间）, `likes`（按点赞数） |
| min_score | integer | 否 | 最低评分筛选 |
| max_score | integer | 否 | 最高评分筛选 |
| tags | string | 否 | 标签筛选（逗号分隔） |

#### 示例请求

```
GET /api/evaluations?course_id=1&sort=likes&page=1&limit=10
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
    "limit": 10
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
| limit | integer | 否 | 每页数量，默认10 |
| course_id | integer | 否 | 课程ID筛选 |
| parent_id | integer | 否 | 父评论ID筛选（用于获取回复） |

#### 示例请求

```
GET /api/comments?course_id=1&page=1&limit=10
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
    "limit": 10
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

#### 错误响应

```json
{
  "message": "无效的排行榜类型"
}

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

## 数据模型

### 用户表 (users)
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(50)` | `PRIMARY KEY` | 用户唯一标识，使用微信openid |
| `nickname` | `VARCHAR(100)` | `NOT NULL` | 用户昵称 |
| `avatar_url` | `VARCHAR(255)` | | 用户头像URL |
| `gender` | `INTEGER` | | 性别 (0:未知, 1:男, 2:女) |
| `student_id` | `VARCHAR(20)` | | 学号 |
| `department` | `VARCHAR(100)` | | 学院 |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP, INDEX` | 创建时间 |
| `updated_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

### 教师表 (teachers)
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 教师ID |
| `name` | `VARCHAR(50)` | `NOT NULL` | 教师姓名 |
| `department` | `VARCHAR(100)` | `NOT NULL, INDEX` | 所属学院 |
| `title` | `VARCHAR(50)` | | 职称 |
| `bio` | `TEXT` | | 简介 |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP, INDEX` | 创建时间 |
| `updated_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

### 用户表 (User)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| id | INTEGER | 主键，自增 | 用户ID |
| openid | VARCHAR(100) | 唯一，非空，索引 | 微信openid |
| nickname | VARCHAR(100) | 可选 | 用户昵称 |
| avatar_url | VARCHAR(500) | 可选 | 用户头像URL |
| created_at | TIMESTAMP | 默认CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 默认CURRENT_TIMESTAMP | 更新时间 |

### 教师表 (Teacher)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| id | INTEGER | 主键，自增 | 教师ID |
| name | VARCHAR(100) | 非空 | 教师姓名 |
| department | VARCHAR(100) | 可选 | 所属学院 |
| title | VARCHAR(100) | 可选 | 职称 |
| introduction | TEXT | 可选 | 教师介绍 |
| created_at | TIMESTAMP | 默认CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 默认CURRENT_TIMESTAMP | 更新时间 |

### 课程表 (courses)
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 课程ID |
| `course_code` | `VARCHAR(20)` | `NOT NULL, UNIQUE, INDEX` | 课程代码 |
| `name` | `VARCHAR(100)` | `NOT NULL` | 课程名称 |
| `description` | `TEXT` | | 课程描述 |
| `credit` | `FLOAT` | `NOT NULL` | 学分 |
| `semester` | `VARCHAR(20)` | | 学期 |
| `teacher_id` | `INTEGER` | `NOT NULL, INDEX, FOREIGN KEY REFERENCES teachers(id)` | 教师ID |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP, INDEX` | 创建时间 |
| `updated_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

### 评价表 (evaluations)
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 评价ID |
| `course_id` | `INTEGER` | `NOT NULL, INDEX, FOREIGN KEY REFERENCES courses(id)` | 课程ID |
| `user_id` | `VARCHAR(50)` | `NOT NULL, INDEX, FOREIGN KEY REFERENCES users(id)` | 用户ID |
| `score` | `FLOAT` | `NOT NULL, INDEX` | 总体评分 |
| `workload_score` | `FLOAT` | `NOT NULL` | 工作量评分 |
| `content_score` | `FLOAT` | `NOT NULL` | 内容评分 |
| `teaching_score` | `FLOAT` | `NOT NULL` | 教学评分 |
| `tags` | `VARCHAR(255)` | | 评价标签 |
| `comment` | `TEXT` | | 评价内容 |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP, INDEX` | 创建时间 |
| `updated_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |
| | | `UNIQUE(course_id, user_id)` | 确保每个用户对每门课程只能评价一次 |

### 评论表 (Comment)

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| id | INTEGER | 主键，自增 | 评论ID |
| course_id | INTEGER | 外键，关联Course表，非空 | 课程ID |
| user_id | INTEGER | 外键，关联User表，非空 | 用户ID |
| user_name | VARCHAR(100) | 可选 | 用户昵称（兼容旧数据） |
| content | TEXT | 非空 | 评论内容 |
| parent_id | INTEGER | 外键，自关联Comment表，可选 | 父评论ID（用于回复） |
| created_at | TIMESTAMP | 默认CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 默认CURRENT_TIMESTAMP | 更新时间 |

### 点赞表 (likes)
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 点赞ID |
| `target_id` | `INTEGER` | `NOT NULL, INDEX` | 目标ID（评价或评论ID） |
| `target_type` | `VARCHAR(20)` | `NOT NULL, INDEX` | 目标类型（'evaluation'或'comment'） |
| `user_id` | `VARCHAR(50)` | `NOT NULL, INDEX, FOREIGN KEY REFERENCES users(id)` | 用户ID |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP, INDEX` | 创建时间 |
| | | `UNIQUE(target_id, target_type, user_id)` | 确保每个用户对每个目标只能点赞一次

---

**版本信息：**
- 文档版本：1.0.0
- 发布日期：2025-11-11

**版权声明：**
本文档版权归评课系统开发团队所有，未经授权，不得复制或传播。