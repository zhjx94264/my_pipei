from fuzzy_search import load_qualification_data
from qualification_matcher import get_qualification_by_name

# 加载数据
data = load_qualification_data()

# 要检查的资质
quals_to_check = ['建筑总包二级', '市政总包二级', '机电总包二级']

# 检查每个资质的要求
for name in quals_to_check:
    qual = get_qualification_by_name(name, data)
    if qual:
        print(f'资质: {name}')
        print(f'  要求齐全: {qual["require_all_types"]}')
        print(f'  总人数要求: {qual["total_count"]}')
        print(f'  职称要求: {qual["types"]}')
        print()
    else:
        print(f'未找到资质: {name}')
        print()