import pandas as pd
import json

# 读取Excel文件中的资质数据
def read_excel_data():
    # 读取Excel文件，使用第一行作为表头
    df = pd.read_excel('zivi_data.xlsx', sheet_name='need', header=0)
    
    # 重命名列名，方便后续处理
    df.columns = ['col0', 'require_all_types', 'name', 'total_count', 'type1', 'type2', 'type3', 'type4', 'type5', 'type6', 'type7', 'type8', 'type9']
    
    excel_data = []
    
    # 遍历每一行数据
    for index, row in df.iterrows():
        # 跳过第一行（表头）
        if index == 0:
            continue
        
        # 提取资质名称
        name = row['name']
        if pd.isna(name) or name.strip() == '':
            continue
        
        # 提取是否要求职称类型齐全
        require_all_types = row['require_all_types']
        require_all_types = require_all_types == '是' if not pd.isna(require_all_types) else False
        
        # 提取总人数要求
        total_count = row['total_count']
        total_count = int(total_count) if not pd.isna(total_count) else 10
        
        # 提取职称类型列表
        types = []
        # 职称类型分布在type1到type9列中
        for col in ['type1', 'type2', 'type3', 'type4', 'type5', 'type6', 'type7', 'type8', 'type9']:
            type_name = row[col]
            if not pd.isna(type_name) and type_name.strip() != '':
                types.append(type_name.strip())
        
        # 创建资质字典
        qualification = {
            'name': name.strip(),
            'require_all_types': require_all_types,
            'types': types,
            'total_count': total_count
        }
        
        excel_data.append(qualification)
    
    return excel_data

# 读取JSON文件中的现有数据
def read_json_data():
    with open('qualification_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存更新后的JSON数据
def save_json_data(data):
    with open('qualification_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 更新资质数据
def update_qualification_data():
    # 读取Excel数据
    excel_data = read_excel_data()
    
    # 创建Excel资质字典，方便根据名称查找资质
    excel_dict = {item['name']: item for item in excel_data}
    
    # 读取JSON数据
    json_data = read_json_data()
    
    # 创建JSON资质字典，方便根据名称查找资质
    json_dict = {item['name']: item for item in json_data}
    
    # 1. 更新或添加资质数据
    for name, excel_qual in excel_dict.items():
        if name in json_dict:
            # 资质已经存在，检查是否需要更新
            json_qual = json_dict[name]
            
            # 检查数据是否一致
            if (json_qual['require_all_types'] != excel_qual['require_all_types'] or
                json_qual['types'] != excel_qual['types'] or
                json_qual['total_count'] != excel_qual['total_count']):
                # 数据不一致，更新JSON数据
                json_dict[name] = excel_qual
                print(f"更新资质: {name}")
        else:
            # 资质不存在，添加到JSON数据中
            json_dict[name] = excel_qual
            print(f"添加资质: {name}")
    
    # 2. 删除Excel中不存在的资质数据
    for name in list(json_dict.keys()):
        if name not in excel_dict:
            # 资质在JSON中存在，但在Excel中不存在，删除该资质
            del json_dict[name]
            print(f"删除资质: {name}")
    
    # 将更新后的字典转换为列表
    updated_data = list(json_dict.values())
    
    # 保存更新后的JSON数据
    save_json_data(updated_data)
    
    # 输出提示信息
    print("已经依据 Excel 中的数据，完成了对 json 文件的更新！")

# 运行主函数
if __name__ == "__main__":
    update_qualification_data()
    
