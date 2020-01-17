## redis数据库说明


| 主键  | 字段说明  | 备注  |数据类型|
| ------------ | ------------ | ------------ | ------------ |
| mid+comment  | 对应帖子评论数  | mid与comment之间无空格|string|
| mid+retweeted  | 对应帖子转发数  | mid与retweeted之间无空格|string|
| Originalmid_hot  | 帖子的集合  | 分数为评论数与转发数之和|有序集合|
| mid  | 热帖的uid集合  | 只有热帖才存在这样的集合|无序集合|