from qualification_matcher import get_qualification_by_name
from fuzzy_search import load_qualification_data

# 加载资质数据
data = load_qualification_data()

# 5个资质名称
qual_names = ["建筑总包二级", "市政总包二级", "机电总包二级", "矿山总包二级", "石油总包二级"]

# 打印每个资质的具体要求
print("5个资质的具体要求：")
print("=" * 50)

for name in qual_names:
    qual = get_qualification_by_name(name, data)
    if qual:
        print(f"\n资质名称: {qual['name']}")
        print(f"是否要求所有类型: {qual['require_all_types']}")
        print(f"总人数要求: {qual['total_count']} 人")
        print(f"所需职称类型: {', '.join(qual['types'])}")

print("\n" + "=" * 50)
