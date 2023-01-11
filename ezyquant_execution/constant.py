from datetime import time

# https://classic.set.or.th/en/products/trading/equity/tradingsystem_p2.html

# Pre-open session 1
pre_open_session_1_start = time(9, 30)
pre_open_session_1_end = time(10, 0)

# Trading session 1
trading_session_1_start = time(10, 0)
trading_session_1_end = time(12, 30)

# Intermission
intermission_start = time(12, 30)
intermission_end = time(14, 0)

# Pre-open session 2
pre_open_session_2_start = time(14, 0)
pre_open_session_2_end = time(14, 30)

# Trading session 2
trading_session_2_start = time(14, 30)
trading_session_2_end = time(16, 30)

# Pre-close
pre_close_start = time(16, 30)
pre_close_end = time(16, 40)

# Off-hour
off_hour_start = time(16, 40)
off_hour_end = time(17, 0)

# Market close
market_close = time(17, 0)
