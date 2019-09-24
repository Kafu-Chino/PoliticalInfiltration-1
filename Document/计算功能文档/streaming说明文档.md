## 功能名称：微博流模拟
#### 操作逻辑
- 代码位置：PoliticalInfiltration/Cron/main_cal/event_percept
- 运行方法：运行streaming.py
- 运行频率：无

#### 功能说明
1）从es数据库中获取数据，每次5000条
2）过滤政治相关的微博
3）将相关微博中的原创微博存入resis的Originalmid_hot中，并设置转发数和评论数为0
4）如果新到来微博为评论微博，根据其root_mid给原微博的评论数加一，Originalmid_hot中得分加一；
如果新到来微博为转发微博，根据其root_mid给原微博的转发数加一，Originalmid_hot中得分加一

#### 流程图
流程图链接：https://github.com/GGXXLL/PoliticalInfiltration/blob/master/Cron/main_cal/event_percept/streaming.png