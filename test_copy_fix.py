#!/usr/bin/env python3
"""
测试复制表功能的修复
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5990/api"

def test_copy_and_rename():
    """测试复制和重命名功能"""
    print("=" * 60)
    print("测试复制表功能修复")
    print("=" * 60)
    
    # 1. 创建一个测试日期（7月29日）
    test_date = "2025-07-29"
    print(f"1. 测试日期: {test_date}")
    
    # 添加一个测试任务
    response = requests.post(f"{BASE_URL}/todos", json={
        "content": "测试任务",
        "date": test_date
    })
    print(f"   添加测试任务: {response.status_code}")
    
    # 2. 复制这个日期的表
    timestamp = int(time.time() * 1000)
    copy_id = f"copy-20250729-{timestamp}"
    
    response = requests.post(f"{BASE_URL}/copy-date", json={
        "source_date": test_date,
        "target_date": copy_id
    })
    print(f"2. 复制表: {response.status_code}")
    if response.status_code == 200:
        print(f"   复制成功: {response.json()}")
    else:
        print(f"   复制失败: {response.text}")
        return
    
    # 3. 为复制的表设置别名
    alias_name = "7月29日-copy"
    response = requests.post(f"{BASE_URL}/date-aliases", json={
        "date": copy_id,
        "alias": alias_name
    })
    print(f"3. 设置别名 '{alias_name}': {response.status_code}")
    if response.status_code == 200:
        print(f"   别名设置成功: {response.json()}")
    else:
        print(f"   别名设置失败: {response.text}")
        return
    
    # 4. 重命名为"生活"
    new_alias = "生活"
    response = requests.post(f"{BASE_URL}/date-aliases", json={
        "date": copy_id,
        "alias": new_alias
    })
    print(f"4. 重命名为 '{new_alias}': {response.status_code}")
    if response.status_code == 200:
        print(f"   重命名成功: {response.json()}")
    else:
        print(f"   重命名失败: {response.text}")
        return
    
    # 5. 再次复制"生活"表
    timestamp2 = int(time.time() * 1000)
    copy_id2 = f"copy-20250729-{timestamp2}"
    
    response = requests.post(f"{BASE_URL}/copy-date", json={
        "source_date": copy_id,  # 使用第一次复制的ID作为源
        "target_date": copy_id2
    })
    print(f"5. 再次复制 '生活' 表: {response.status_code}")
    if response.status_code == 200:
        print(f"   复制成功: {response.json()}")
    else:
        print(f"   复制失败: {response.text}")
        return
    
    # 6. 为第二次复制设置别名
    alias_name2 = "生活-copy"
    response = requests.post(f"{BASE_URL}/date-aliases", json={
        "date": copy_id2,
        "alias": alias_name2
    })
    print(f"6. 设置别名 '{alias_name2}': {response.status_code}")
    if response.status_code == 200:
        print(f"   别名设置成功: {response.json()}")
    else:
        print(f"   别名设置失败: {response.text}")
        return
    
    print("\n" + "=" * 60)
    print("测试完成！所有步骤都成功执行。")
    print("=" * 60)
    
    # 7. 验证所有表都存在
    print("\n验证创建的表:")
    for date_id, name in [(test_date, "原始表"), (copy_id, "生活"), (copy_id2, "生活-copy")]:
        response = requests.get(f"{BASE_URL}/todos?date={date_id}")
        if response.status_code == 200:
            todos = response.json()
            print(f"   {name} ({date_id}): {len(todos)} 个任务")
        else:
            print(f"   {name} ({date_id}): 获取失败")

if __name__ == "__main__":
    test_copy_and_rename()