from qualification_matcher import merge_qualifications, calculate_total_staff, get_qualification_by_name
from fuzzy_search import load_qualification_data

# 加载资质数据
data = load_qualification_data()

# 测试3个资质：机电总包二级、石油总包二级、矿山总包二级
qual_names = ["机电总包二级", "石油总包二级", "矿山总包二级"]

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
