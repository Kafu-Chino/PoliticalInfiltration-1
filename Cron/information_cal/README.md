# 信息计算
对于所有的敏感信息计算的相关代码放在这里

### 主计算
`information_cal_main.py`

### 数据获取模块
+ 从数据库获取用户和微博：`data_utils.py`
+ 处理获取到的微博文本：`data_process_utils.py`

### 模块计算
+ 地域特征：`user_position.py`
+ 活动特征：`user_msg_type.py`
+ 偏好特征：`user_topic.py`, `user_domain.py`, `user_keywords.py`
+ 影响力特征：`user_influence.py`
+ 社交特征：`user_social.py`
+ 情绪特征：`user_sentiment.py`

### 其他
+ 人物画像计算congfig：`profile_config.py`