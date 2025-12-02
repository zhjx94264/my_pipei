#!/usr/bin/env python3
# 测试优化后的资质匹配算法

from qualification_matcher import merge_qualifications, calculate_total_staff, get_qualification_by_name
from fuzzy_search import load_qualification_data

def test_optimized_algorithm():
    """测试优化后的算法是否能得到更好的结果"""
    # 加载资质数据
    data = load_qualification_data()
    
    # 用户选择的资质列表
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
    
    # 使用优化后的算法计算
    final_counts, type_attributes = merge_qualifications(matched_qualifications)
    total_staff = calculate_total_staff(final_counts)
    
    print("\n" + "="*50)
    print("优化后的计算结果")
    print("="*50)
    for type_name, count in sorted(final_counts.items()):
        print(f"{type_name}: {count} 人")
    print("="*50)
    print(f"总人数: {total_staff} 人")
    print("="*50)
    
    # 验证是否满足所有资质要求
    print("\n" + "="*50)
    print("验证结果")
    print("="*50)
    for qual in matched_qualifications:
        if qual['require_all_types']:
            # 验证每个职称类型至少1人
            all_types_ok = all(final_counts.get(type_name, 0) >= 1 for type_name in qual['types'])
            # 验证总人数满足要求
            current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
            total_ok = current_total >= qual['total_count']
            print(f"{qual['name']}: 类型齐全要求 {'✓' if all_types_ok else '✗'}, 总人数要求 {'✓' if total_ok else '✗'} (当前: {current_total}, 需要: {qual['total_count']})")
        else:
            # 验证总人数满足要求
            current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
            total_ok = current_total >= qual['total_count']
            print(f"{qual['name']}: 总人数要求 {'✓' if total_ok else '✗'} (当前: {current_total}, 需要: {qual['total_count']})")
    
    return total_staff

if __name__ == "__main__":
    test_optimized_algorithm()
