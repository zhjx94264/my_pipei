#!/usr/bin/env python3
# 测试新的优化算法

from qualification_matcher import merge_qualifications, calculate_total_staff, get_qualification_by_name
from fuzzy_search import load_qualification_data

def test_new_algorithm():
    """测试新的优化算法"""
    # 加载资质数据
    data = load_qualification_data()
    
    # 测试用例1：单个资质 - 建筑总包二级（预期总人数17）
    print("测试用例1：单个资质 - 建筑总包二级")
    qual1 = get_qualification_by_name("建筑总包二级", data)
    final_counts1, type_attributes1 = merge_qualifications([qual1])
    total1 = calculate_total_staff(final_counts1)
    print(f"结果: {final_counts1}")
    print(f"总人数: {total1}")
    print(f"预期: 17, 实际: {total1}, {'✓' if total1 == 17 else '✗'}")
    print()
    
    # 测试用例2：三个资质 - 机电总包二级、矿山总包二级、石油总包二级（预期总人数23）
    print("测试用例2：三个资质 - 机电总包二级、矿山总包二级、石油总包二级")
    qual2 = get_qualification_by_name("机电总包二级", data)
    qual3 = get_qualification_by_name("矿山总包二级", data)
    qual4 = get_qualification_by_name("石油总包二级", data)
    final_counts2, type_attributes2 = merge_qualifications([qual2, qual3, qual4])
    total2 = calculate_total_staff(final_counts2)
    print(f"结果: {final_counts2}")
    print(f"总人数: {total2}")
    print(f"预期: 23, 实际: {total2}, {'✓' if total2 == 23 else '✗'}")
    print()

if __name__ == "__main__":
    test_new_algorithm()
