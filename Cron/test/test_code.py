import sys
sys.path.append("../../")

from Config.db_utils import es, pi_cur, conn, get_global_senwords, get_event_senwords

print(get_event_senwords("xianggangshijian_1581919160"))
print(get_global_senwords())