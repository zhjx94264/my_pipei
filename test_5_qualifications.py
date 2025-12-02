from qualification_matcher import merge_qualifications, calculate_total_staff, get_qualification_by_name
from fuzzy_search import load_qualification_data

# 加载资质数据
data = load_qualification_data()

# 测试5个资质：石油总包二级、机电总包二级、建筑总包二级、矿山总包二级、市政总包二级
qual_names = ["石油总包二级", "机电总包二级", "建筑总包二级", "矿山总包二级", "市政总包二级"]

# 获取资质详情
qualifications = []
for name in qual_names:
    qual = get_qualification_by_name(name, data)
    if qual:
        qualifications.append(qual)
        print(f"加载资质: {name}")
    else:
        print(f"未找到资质: {name}")

print(f"\n共加载 {len(qualifications)} 个资质")

# 合并计算
final_counts, type_attributes = merge_qualifications(qualifications)

# 计算总人数
total_staff = calculate_total_staff(final_counts)

# 打印结果
print(f"\n总人数: {total_staff}")
print("\n最终所需职称数量:")
for type_name, count in sorted(final_counts.items()):
    print(f"{type_name}: {count} 人")

# 验证每个资质是否满足要求
print("\n验证每个资质是否满足要求:")
for qual in qualifications:
    current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
    all_types_ok = all(final_counts.get(type_name, 0) >= 1 for type_name in qual['types'])
    
    if qual['require_all_types']:
        satisfied = all_types_ok and current_total >= qual['total_count']
        print(f"{qual['name']}: 总人数={current_total}/{qual['total_count']}, 类型齐全={all_types_ok}, 满足要求={satisfied}")
    else:
        satisfied = current_total >= qual['total_count']
        print(f"{qual['name']}: 总人数={current_total}/{qual['total_count']}, 满足要求={satisfied}")
