## 功能名称：找到热帖及评论与转发的用户uid
#### 操作逻辑
- 代码位置：PoliticalInfiltration/Cron/main_cal/event_percept
- 运行方法：运行find_hot_ralated_uid.py
- 运行频率：无

#### 功能说明
1）从redis中找到热帖（评论和转发之和大于1000的帖子）的mid
2）在es中根据root_mid找到所有符合条件的uid
3）以热贴的mid为键，将所有在热贴下评论和转发热帖的用户的uid存放在集合中
4）将发出热帖的用户uid集合存入另一个集合中

#### 流程图
流程图链接：https://github.com/GGXXLL/PoliticalInfiltration/blob/master/Cron/main_cal/event_percept/find_hot_related_uid.png