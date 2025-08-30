#!/usr/bin/env python3
"""
最终完整集成测试脚本
验证见缝插针游戏排行榜功能的完整逻辑链路
"""

import requests
import json
import time
import os
from datetime import datetime

# 设置不使用代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

class LeaderboardIntegrationTest:
    def __init__(self):
        self.base_url = "http://8089.dachaonet.com"
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            呢
            "message": messageda yi xie
            "message": messageda yi xie
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_backend_api_structure(self):
        """测试后端API结构"""
        print("🔧 测试后端API结构...")
        
        try:
            response = requests.get(f"{self.base_url}/api/game/leaderboard")
            
            if response.status_code != 200:
                self.log_test("后端API可访问性", False, f"HTTP状态码: {response.status_code}")
                return False
            
            data = response.json()
            
            # 验证BaseResponse结构
            if not all(key in data for key in ['code', 'message', 'data']):
                self.log_test("BaseResponse结构", False, "缺少必需字段")
                return False
            
            self.log_test("BaseResponse结构", True)
            
            if data['code'] != 200:
                self.log_test("API响应代码", False, f"返回代码: {data['code']}")
                return False
            
            self.log_test("API响应代码", True)
            
            # 验证LeaderboardResponse结构
            leaderboard_data = data.get('data', {})
            if not all(key in leaderboard_data for key in ['leaderboard', 'period', 'total']):
                self.log_test("LeaderboardResponse结构", False, "缺少必需字段")
                return False
            
            self.log_test("LeaderboardResponse结构", True)
            
            return True
            
        except Exception as e:
            self.log_test("后端API连接", False, str(e))
            return False
    
    def test_leaderboard_data_integrity(self):
        """测试排行榜数据完整性"""
        print("\n📊 测试排行榜数据完整性...")
        
        try:
            response = requests.get(f"{self.base_url}/api/game/leaderboard")
            data = response.json()
            
            if data['code'] != 200:
                self.log_test("获取排行榜数据", False, "API调用失败")
                return False
            
            leaderboard = data['data']['leaderboard']
            
            if not leaderboard:
                self.log_test("排行榜数据存在性", False, "排行榜为空")
                return False
            
            self.log_test("排行榜数据存在性", True, f"包含 {len(leaderboard)} 个玩家")
            
            # 验证第一个玩家的数据结构
            first_player = leaderboard[0]
            required_fields = [
                'rank', 'user_id', 'nickname', 'best_score', 
                'latest_play', 'level', 'game_count', 'coins'
            ]
            
            missing_fields = [field for field in required_fields if field not in first_player]
            if missing_fields:
                self.log_test("玩家数据字段完整性", False, f"缺少字段: {missing_fields}")
                return False
            
            self.log_test("玩家数据字段完整性", True)
            
            # 验证数据类型
            type_validations = [
                ('rank', int, first_player['rank']),
                ('user_id', int, first_player['user_id']),
                ('nickname', str, first_player['nickname']),
                ('best_score', int, first_player['best_score']),
                ('level', int, first_player['level']),
                ('game_count', int, first_player['game_count']),
                ('coins', (int, float), first_player['coins'])
            ]
            
            for field_name, expected_type, value in type_validations:
                if not isinstance(value, expected_type):
                    self.log_test(f"字段类型验证: {field_name}", False, 
                                f"期望 {expected_type}, 实际 {type(value)}")
                    return False
            
            self.log_test("玩家数据类型正确", True)
            
            # 验证排序正确性
            scores = [player['best_score'] for player in leaderboard]
            if scores != sorted(scores, reverse=True):
                self.log_test("排行榜排序", False, "分数未按降序排列")
                return False
            
            self.log_test("排行榜排序", True, "按分数降序排列正确")
            
            # 验证排名连续性
            ranks = [player['rank'] for player in leaderboard]
            expected_ranks = list(range(1, len(leaderboard) + 1))
            if ranks != expected_ranks:
                self.log_test("排名连续性", False, f"排名不连续: {ranks}")
                return False
            
            self.log_test("排名连续性", True)
            
            return True
            
        except Exception as e:
            self.log_test("数据完整性测试", False, str(e))
            return False
    
    def test_time_period_functionality(self):
        """测试时间范围功能"""
        print("\n📅 测试时间范围功能...")
        
        periods = ['all', 'today', 'week', 'month']
        
        for period in periods:
            try:
                response = requests.get(f"{self.base_url}/api/game/leaderboard?period={period}")
                
                if response.status_code != 200:
                    self.log_test(f"时间范围: {period}", False, f"HTTP错误: {response.status_code}")
                    continue
                
                data = response.json()
                
                if data['code'] != 200:
                    self.log_test(f"时间范围: {period}", False, f"API错误: {data['message']}")
                    continue
                
                # 验证返回的period字段
                returned_period = data['data']['period']
                if returned_period != period:
                    self.log_test(f"时间范围: {period}", False, 
                                f"返回period不匹配: 期望{period}, 实际{returned_period}")
                    continue
                
                leaderboard = data['data']['leaderboard']
                self.log_test(f"时间范围: {period}", True, f"{len(leaderboard)} 条记录")
                
            except Exception as e:
                self.log_test(f"时间范围: {period}", False, str(e))
        
        return True
    
    def test_parameter_validation(self):
        """测试参数验证"""
        print("\n🔍 测试参数验证...")
        
        test_cases = [
            {
                "name": "负数limit",
                "params": "?limit=-1",
                "should_work": True  # 应该被修正为有效值
            },
            {
                "name": "过大limit",
                "params": "?limit=999999",
                "should_work": True  # 应该被限制到最大值
            },
            {
                "name": "无效period",
                "params": "?period=invalid",
                "should_work": True  # 应该默认为'all'
            },
            {
                "name": "SQL注入尝试",
                "params": "?period=' OR 1=1--",
                "should_work": True  # 应该被安全处理
            }
        ]
        
        for case in test_cases:
            try:
                url = f"{self.base_url}/api/game/leaderboard{case['params']}"
                response = requests.get(url)
                
                success = (response.status_code == 200) == case['should_work']
                
                if success and response.status_code == 200:
                    data = response.json()
                    success = data.get('code') == 200
                
                self.log_test(f"参数验证: {case['name']}", success)
                
            except Exception as e:
                self.log_test(f"参数验证: {case['name']}", False, str(e))
        
        return True
    
    def test_android_client_compatibility(self):
        """测试Android客户端兼容性"""
        print("\n📱 测试Android客户端兼容性...")
        
        try:
            response = requests.get(f"{self.base_url}/api/game/leaderboard")
            
            if response.status_code != 200:
                self.log_test("Android兼容性 - API访问", False, f"无法访问API: {response.status_code}")
                return False
            
            data = response.json()
            
            # 模拟Android Gson解析
            try:
                # 验证能否成功解析为Android期望的结构
                base_response = {
                    'code': data['code'],
                    'message': data['message'],
                    'data': data['data']
                }
                
                leaderboard_response = data['data']
                leaderboard_data = {
                    'leaderboard': leaderboard_response['leaderboard'],
                    'period': leaderboard_response['period'],
                    'total': leaderboard_response['total']
                }
                
                # 验证每个玩家数据
                for player in leaderboard_response['leaderboard']:
                    player_data = {
                        'rank': player['rank'],
                        'userId': player['user_id'],
                        'nickname': player['nickname'],
                        'bestScore': player['best_score'],
                        'latestPlay': player.get('latest_play'),
                        'level': player['level'],
                        'gameCount': player['game_count'],
                        'coins': player['coins']
                    }
                
                self.log_test("Android兼容性 - JSON解析", True, "数据结构兼容")
                
            except KeyError as e:
                self.log_test("Android兼容性 - JSON解析", False, f"缺少必需字段: {e}")
                return False
            
            # 测试网络请求头兼容性
            headers = {
                'Authorization': 'Bearer dummy_token',
                'User-Agent': 'Android/NeedleInsert/1.0',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/api/game/leaderboard", headers=headers)
            
            if response.status_code == 200:
                self.log_test("Android兼容性 - 请求头", True, "请求头兼容")
            else:
                self.log_test("Android兼容性 - 请求头", False, f"请求头问题: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Android兼容性测试", False, str(e))
            return False
    
    def test_performance_and_scalability(self):
        """测试性能和可扩展性"""
        print("\n⚡ 测试性能和可扩展性...")
        
        # 测试响应时间
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/game/leaderboard", timeout=5)
            response_time = time.time() - start_time
            
            if response_time < 3.0:  # 期望3秒内响应（移动网络环境）
                self.log_test("响应时间", True, f"{response_time:.2f}秒")
            else:
                self.log_test("响应时间", False, f"{response_time:.2f}秒（超时）")
            
        except requests.exceptions.Timeout:
            self.log_test("响应时间", False, "请求超时")
        except Exception as e:
            self.log_test("响应时间", False, str(e))
        
        # 测试并发请求
        try:
            import concurrent.futures
            
            def make_request():
                return requests.get(f"{self.base_url}/api/game/leaderboard", timeout=10)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_count = sum(1 for r in results if r.status_code == 200)
            
            if success_count == 5:
                self.log_test("并发请求", True, f"5/5 请求成功")
            else:
                self.log_test("并发请求", False, f"{success_count}/5 请求成功")
                
        except Exception as e:
            self.log_test("并发请求", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🎯 见缝插针游戏 - 排行榜完整集成测试")
        print("=" * 70)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标服务器: {self.base_url}")
        print()
        
        # 执行所有测试
        tests = [
            self.test_backend_api_structure,
            self.test_leaderboard_data_integrity,
            self.test_time_period_functionality,
            self.test_parameter_validation,
            self.test_android_client_compatibility,
            self.test_performance_and_scalability
        ]
        
        for test in tests:
            test()
            print()  # 添加空行分隔
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("📋 测试报告")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n🎉 总结:")
        if failed_tests == 0:
            print("   所有测试通过！排行榜功能完全正常。")
            print("   ✅ 后端API工作正常")
            print("   ✅ 数据结构完整且兼容Android客户端")
            print("   ✅ 时间范围功能正常")
            print("   ✅ 参数验证和错误处理完善")
            print("   ✅ 性能表现良好")
            print("\n🚀 Android应用可以正常使用排行榜功能!")
        else:
            print("   部分测试失败，需要修复相关问题。")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = LeaderboardIntegrationTest()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)