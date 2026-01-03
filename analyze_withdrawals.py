#!/usr/bin/env python3
"""分析提现数据"""

import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

def parse_sql_file(sql_file_path):
    """解析SQL文件中的提现数据"""
    withdrawals = []

    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找 INSERT INTO `withdraw_requests` 语句
    pattern = r"INSERT INTO `withdraw_requests`.*?VALUES\s+(.*?);"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        # 解析每一行数据
        # 格式: (id, user_id, amount, coins_used, alipay_account, real_name, status, admin_note, request_time, process_time)
        rows = re.findall(r"\(([^)]+)\)", match)

        for row in rows:
            # 分割字段值
            fields = []
            current_field = ""
            in_quotes = False

            for char in row:
                if char == "'" and (not current_field or current_field[-1] != '\\'):
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    fields.append(current_field.strip())
                    current_field = ""
                    continue
                current_field += char

            if current_field:
                fields.append(current_field.strip())

            if len(fields) >= 10:
                try:
                    withdraw_id = fields[0]
                    user_id = fields[1]
                    amount = fields[2].strip("'")
                    coins_used = fields[3].strip("'")
                    alipay_account = fields[4].strip("'")
                    real_name = fields[5].strip("'")
                    status = fields[6].strip("'")
                    admin_note = fields[7].strip("'")
                    request_time = fields[8].strip("'")
                    process_time = fields[9].strip("'")

                    # 只统计已通过(approved)或已完成(completed)的提现
                    if status.lower() in ['approved', 'completed']:
                        withdrawals.append({
                            'id': withdraw_id,
                            'user_id': user_id,
                            'amount': Decimal(amount),
                            'coins_used': Decimal(coins_used),
                            'status': status,
                            'request_time': request_time,
                            'process_time': process_time
                        })
                except Exception as e:
                    # 跳过解析失败的行
                    continue

    return withdrawals

def analyze_withdrawals(withdrawals):
    """分析提现数据"""
    if not withdrawals:
        print("没有找到已通过的提现记录")
        return

    # 统计总金额
    total_amount = sum(w['amount'] for w in withdrawals)
    total_coins = sum(w['coins_used'] for w in withdrawals)
    total_count = len(withdrawals)

    # 按日期统计
    daily_stats = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0, 'coins': Decimal('0')})

    for w in withdrawals:
        # 使用 request_time 提取日期
        date_str = w['request_time']
        if date_str and date_str != 'NULL':
            try:
                date = date_str.split()[0]  # 取日期部分
                daily_stats[date]['amount'] += w['amount']
                daily_stats[date]['count'] += 1
                daily_stats[date]['coins'] += w['coins_used']
            except:
                continue

    # 打印结果
    print("="*80)
    print("提现数据统计（已通过/已完成）")
    print("="*80)
    print(f"\n总计:")
    print(f"  提现总金额: ¥{total_amount:.2f}")
    print(f"  消耗金币总数: {total_coins:.2f}")
    print(f"  提现总笔数: {total_count}")
    print(f"  平均每笔: ¥{total_amount/total_count:.2f}")

    print(f"\n每日明细:")
    print(f"{'日期':<12} {'金额(¥)':<12} {'笔数':<8} {'消耗金币':<12}")
    print("-"*80)

    # 按日期排序
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        print(f"{date:<12} {stats['amount']:>11.2f} {stats['count']:>7} {stats['coins']:>11.2f}")

    print("="*80)

if __name__ == "__main__":
    sql_file = "/Users/yy/Documents/GitHub/jianfengchazhen/game_db_2026-01-02_18-58-45_mysql_data_trQHv.sql"

    print("正在解析SQL文件...")
    withdrawals = parse_sql_file(sql_file)

    print(f"找到 {len(withdrawals)} 条已通过的提现记录\n")

    analyze_withdrawals(withdrawals)
