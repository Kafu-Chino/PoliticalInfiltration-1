# 流数据ES数据库
ES_HOST = '219.224.135.12'
ES_PORT = 9211

# REDIS数据库
REDIS_HOST = '219.224.135.12'
REDIS_PORT = 6666

# 主MySQL数据库
DB_HOST = '219.224.135.12'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'mysql3306'
DB_CHARSET = 'utf8mb4'
# DB_DEFAULT_DB = 'portrait'
# DB_DEFAULT_DB = 'itfin'
DB_MIN_CACHED = 3
DB_MAX_CACHED = 10
DB_MAX_CONNECYIONS = 30


# 计算信息传播态势阈值参数
count_threshold = 300
reduce_threshold = 0.5
political_dict = {"right": "右倾", "left": "左倾", "mid": "中立"}
DB_MIN_CACHED=3
DB_MAX_CACHED=10
DB_MAX_CONNECYIONS=30


domain_dict = {
    'university': '高校', 
    'homeadmin': '境内机构', 
    'abroadadmin': '境外机构',
    'homemedia': '媒体', 
    'abroadmedia': '境外媒体',
    'folkorg': '民间组织', 
    'lawyer': '法律机构及人士', 
    'politician': '政府机构及人士', 
    'mediaworker': '媒体人士',
    'activer': '活跃人士', 
    'grassroot': '草根', 
    'other': '其他', 
    'business': '商业人士'
}

topic_dict = {'art': '文体类_娱乐', 
    'computer': '科技类', 
    'economic': '经济类', 
    'education': '教育类', 
    'environment': '民生类_环保',
    'medicine': '民生类_健康', 
    'military': '军事类', 
    'politics': '政治类_外交', 
    'sports': '文体类_体育', 
    'traffic': '民生类_交通',
    'life': '其他类', 
    'anti-corruption': '政治类_反腐', 
    'employment': '民生类_就业', 
    'fear-of-violence': '政治类_暴恐',
    'house': '民生类_住房', 
    'law': '民生类_法律', 
    'peace': '政治类_地区和平', 
    'religion': '政治类_宗教',
    'social-security': '民生类_社会保障', 
    'violence': '政治类_暴恐'
}

MSG_TYPE_DIC = {
    1: "原创",
    2: "评论",
    3: "转发"
}