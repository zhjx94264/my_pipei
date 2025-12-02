# 测试优化后的匹配算法
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qualification_matcher import merge_qualifications, get_qualification_by_name, calculate_total_staff
from fuzzy_search import load_qualification_data

def test_three_qualifications():
    """测试三个资质的匹配结果：机电总包二级、矿山总包二级、石油总包二级"""
    print("\n" + "="*60)
    print("测试优化后的匹配算法")
    print("="*60)
    
    # 加载数据
    data = load_qualification_data()
    
    # 获取三个资质
    qual1 = get_qualification_by_name("机电总包二级", data)
    qual2 = get_qualification_by_name("矿山总包二级", data)
    qual3 = get_qualification_by_name("石油总包二级", data)
    
    if not all([qual1, qual2, qual3]):
        print("错误：无法找到指定的资质")
        return
    
    qualifications = [qual1, qual2, qual3]
    
    print(f"测试资质：{qual1['name']}、{qual2['name']}、{qual3['name']}")
    print(f"\n各资质要求：")
    for qual in qualifications:
        print(f"- {qual['name']}: 总人数{qual['total_count']}，要求齐全：{qual['require_all_types']}，职称类型：{qual['types']}")
    
    # 使用优化后的算法计算
    final_counts, type_attributes = merge_qualifications(qualifications)
    total_staff = calculate_total_staff(final_counts)
    
    print(f"\n" + "="*40)
    print("优化后算法结果")
    print("="*40)
    print(f"最终所需职称数量：")
    for type_name, count in sorted(final_counts.items()):
        print(f"  {type_name}: {count} 人")
    print(f"\n总人数：{total_staff} 人")
    print(f"\n职称属性：")
    for type_name, attrs in sorted(type_attributes.items()):
        print(f"  {type_name}: 共享次数{attrs['is_red']}，颜色{'红色' if attrs['is_red'] else '绿色'}")
    
    # 验证每个资质是否满足要求
    print(f"\n" + "="*40)
    print("资质要求验证")
    print("="*40)
    all_satisfied = True
    for qual in qualifications:
        current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
        all_types_ok = all(final_counts.get(type_name, 0) >= 1 for type_name in qual['types'])
        
        if qual['require_all_types']:
            satisfied = all_types_ok and current_total >= qual['total_count']
            print(f"- {qual['name']}: {'✓ 满足' if satisfied else '✗ 不满足'}")
            print(f"  要求：总人数≥{qual['total_count']}，所有职称类型≥1人")
            print(f"  实际：总人数={current_total}，所有职称类型≥1人：{all_types_ok}")
        else:
            satisfied = current_total >= qual['total_count']
            print(f"- {qual['name']}: {'✓ 满足' if satisfied else '✗ 不满足'}")
            print(f"  要求：总人数≥{qual['total_count']}")
            print(f"  实际：总人数={current_total}")
        
        if not satisfied:
            all_satisfied = False
    
    if all_satisfied:
        print(f"\n✓ 所有资质要求都已满足！")
    else:
        print(f"\n✗ 部分资质要求未满足，请检查算法！")
    
    return final_counts, total_staff

def test_other_combinations():
    """测试其他资质组合，验证算法的通用性"""
    print("\n" + "="*60)
    print("测试其他资质组合")
    print("="*60)
    
    # 加载数据
    data = load_qualification_data()
    
    # 测试组合1：建筑总包二级 + 市政总包二级
    print(f"\n测试组合1：建筑总包二级 + 市政总包二级")
    qual1 = get_qualification_by_name("建筑总包二级", data)
    qual2 = get_qualification_by_name("市政总包二级", data)
    if qual1 and qual2:
        final_counts, _ = merge_qualifications([qual1, qual2])
        total_staff = calculate_total_staff(final_counts)
        print(f"  结果：总人数={total_staff} 人，职称分布：{final_counts}")
    
    # 测试组合2：建筑总包二级 + 机电总包二级 + 市政总包二级 + 电力总包二级
    print(f"\n测试组合2：建筑总包二级 + 机电总包二级 + 市政总包二级 + 电力总包二级")
    qual1 = get_qualification_by_name("建筑总包二级", data)
    qual2 = get_qualification_by_name("机电总包二级", data)
    qual3 = get_qualification_by_name("市政总包二级", data)
    qual4 = get_qualification_by_name("电力总包二级", data)
    if all([qual1, qual2, qual3, qual4]):
        final_counts, _ = merge_qualifications([qual1, qual2, qual3, qual4])
        total_staff = calculate_total_staff(final_counts)
        print(f"  结果：总人数={total_staff} 人")
        print(f"  职称分布：{final_counts}")
    
    # 测试组合3：市政总包二级 + 电力总包二级（两个无齐全要求的资质）
    print(f"\n测试组合3：市政总包二级 + 电力总包二级")
    qual1 = get_qualification_by_name("市政总包二级", data)
    qual2 = get_qualification_by_name("电力总包二级", data)
    if qual1 and qual2:
        final_counts, _ = merge_qualifications([qual1, qual2])
        total_staff = calculate_total_staff(final_counts)
        print(f"  结果：总人数={total_staff} 人，职称分布：{final_counts}")

if __name__ == "__main__":
    # 测试三个资质的匹配结果
    test_three_qualifications()
    
    # 测试其他资质组合
    test_other_combinations()
