#!/usr/bin/env python3
# 测试用户输入职称人数的匹配结果

from qualification_matcher import get_qualification_by_name, calculate_total_staff
from fuzzy_search import load_qualification_data

def test_user_input():
    """测试用户输入职称人数的匹配结果"""
    # 加载资质数据
    data = load_qualification_data()
    
    # 测试的资质列表（来自test_optimization.py）
    selected_qualifications = [
        "石油总包二级",
        "消防设施工程施工专业承包二级",
        "建筑幕墙工程施工专业承包二级",
        "古建筑工程施工专业承包二级",
        "模板脚手架施工专业承包不分等级",
        "地基基础工程施工专业承包二级",
        "钢结构工程施工专业承包二级",
        "建筑总包二级",
        "市政总包二级"
    ]
    
    # 获取匹配的资质信息
    matched_qualifications = []
    for qual_name in selected_qualifications:
        qual = get_qualification_by_name(qual_name, data)
        if qual:
            matched_qualifications.append(qual)
    
    print("匹配到的资质:")
    for qual in matched_qualifications:
        print(f"- {qual['name']} (要求齐全: {qual['require_all_types']}, 总人数: {qual['total_count']})")
    
    # 收集所有需要的职称类型
    all_required_types = set()
    for qual in matched_qualifications:
        for type_name in qual['types']:
            all_required_types.add(type_name)
    
    print("\n" + "="*50)
    print("请输入每个职称的人数")
    print("="*50)
    
    # 让用户输入每个职称的人数
    user_input_counts = {}
    for type_name in sorted(all_required_types):
        while True:
            try:
                count = input(f"请输入 {type_name} 的人数: ")
                count = int(count)
                user_input_counts[type_name] = count
                break
            except ValueError:
                print("输入无效，请输入一个整数")
    
    # 计算总人数
    total_staff = calculate_total_staff(user_input_counts)
    
    print("\n" + "="*50)
    print("用户输入的计算结果")
    print("="*50)
    for type_name, count in sorted(user_input_counts.items()):
        print(f"{type_name}: {count} 人")
    print("="*50)
    print(f"总人数: {total_staff} 人")
    print("="*50)
    
    # 判断是否满足所有资质要求
    print("\n" + "="*50)
    print("判断结果")
    print("="*50)
    all_satisfied = True
    for qual in matched_qualifications:
        if qual['require_all_types']:
            # 检查每个职称类型至少1人
            all_types_ok = all(user_input_counts.get(type_name, 0) >= 1 for type_name in qual['types'])
            # 检查总人数满足要求
            current_total = sum(user_input_counts.get(type_name, 0) for type_name in qual['types'])
            total_ok = current_total >= qual['total_count']
            if all_types_ok and total_ok:
                print(f"{qual['name']}: ✓ 满足要求 (当前: {current_total} 人, 需要: {qual['total_count']} 人)")
            else:
                print(f"{qual['name']}: ✗ 不满足要求 (当前: {current_total} 人, 需要: {qual['total_count']} 人)")
                all_satisfied = False
        else:
            # 检查总人数满足要求
            current_total = sum(user_input_counts.get(type_name, 0) for type_name in qual['types'])
            total_ok = current_total >= qual['total_count']
            if total_ok:
                print(f"{qual['name']}: ✓ 满足要求 (当前: {current_total} 人, 需要: {qual['total_count']} 人)")
            else:
                print(f"{qual['name']}: ✗ 不满足要求 (当前: {current_total} 人, 需要: {qual['total_count']} 人)")
                all_satisfied = False
    
    print("\n" + "="*50)
    print("最终结果")
    print("="*50)
    if all_satisfied:
        print("✓ 所有资质要求都被满足！")
    else:
        print("✗ 部分资质要求未被满足，请调整职称人数！")
    
    return all_satisfied

if __name__ == "__main__":
    test_user_input()
