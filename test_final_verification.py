#!/usr/bin/env python3
# 最终验证测试

from qualification_matcher import merge_qualifications, calculate_total_staff, get_qualification_by_name
from fuzzy_search import load_qualification_data

def test_final_verification():
    """最终验证测试"""
    # 加载资质数据
    data = load_qualification_data()
    
    print("="*60)
    print("最终验证测试")
    print("="*60)
    
    # 测试用例1：单个资质 - 建筑总包二级
    print("\n测试用例1：单个资质 - 建筑总包二级")
    qual1 = get_qualification_by_name("建筑总包二级", data)
    final_counts1, type_attributes1 = merge_qualifications([qual1])
    total1 = calculate_total_staff(final_counts1)
    print(f"资质要求: 总人数 {qual1['total_count']}, 要求齐全: {qual1['require_all_types']}")
    print(f"计算结果: 总人数 {total1}, 职称分布: {final_counts1}")
    print(f"验证: {'✓' if total1 >= qual1['total_count'] else '✗'} 满足要求")
    
    # 测试用例2：三个资质 - 机电总包二级、矿山总包二级、石油总包二级
    print("\n测试用例2：三个资质 - 机电总包二级、矿山总包二级、石油总包二级")
    qual2 = get_qualification_by_name("机电总包二级", data)
    qual3 = get_qualification_by_name("矿山总包二级", data)
    qual4 = get_qualification_by_name("石油总包二级", data)
    
    # 计算
    final_counts2, type_attributes2 = merge_qualifications([qual2, qual3, qual4])
    total2 = calculate_total_staff(final_counts2)
    
    # 输出结果
    print(f"资质要求:")
    print(f"  - {qual2['name']}: 总人数 {qual2['total_count']}, 要求齐全: {qual2['require_all_types']}")
    print(f"  - {qual3['name']}: 总人数 {qual3['total_count']}, 要求齐全: {qual3['require_all_types']}")
    print(f"  - {qual4['name']}: 总人数 {qual4['total_count']}, 要求齐全: {qual4['require_all_types']}")
    print(f"计算结果: 总人数 {total2}")
    print(f"预期结果: 23 人")
    print(f"匹配结果: {'✓' if total2 == 23 else '✗'} {'符合预期' if total2 == 23 else '不符合预期'}")
    
    # 详细输出职称分布
    print(f"\n职称分布:")
    for type_name, count in sorted(final_counts2.items()):
        print(f"  {type_name}: {count} 人")
    
    # 验证每个资质是否满足要求
    print(f"\n资质验证:")
    for qual in [qual2, qual3, qual4]:
        current_total = sum(final_counts2.get(type_name, 0) for type_name in qual['types'])
        all_types_ok = all(final_counts2.get(type_name, 0) >= 1 for type_name in qual['types']) if qual['require_all_types'] else True
        if qual['require_all_types']:
            print(f"  - {qual['name']}: 总人数 {current_total}/{qual['total_count']}, 类型齐全 {'✓' if all_types_ok else '✗'}, {'✓' if current_total >= qual['total_count'] and all_types_ok else '✗'} 满足要求")
        else:
            print(f"  - {qual['name']}: 总人数 {current_total}/{qual['total_count']}, {'✓' if current_total >= qual['total_count'] else '✗'} 满足要求")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_final_verification()
