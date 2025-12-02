# 导入模块
import json
from fuzzy_search import load_qualification_data, fuzzy_search

def calculate_single_qualification(qualification):
    """计算单个资质所需的职称数量"""
    职称_counts = {}
    
    if qualification['require_all_types']:
        # 要求齐全：每个职称类型至少1人
        for type_name in qualification['types']:
            职称_counts[type_name] = 1
        # 确保总人数满足要求
        current_total = sum(职称_counts.values())
        if current_total < qualification['total_count']:
            # 需要增加人数，优先加到共享次数多的职称上
            # 这里先简单处理，后续在合并计算时会优化
            diff = qualification['total_count'] - current_total
            for type_name in qualification['types'][:diff]:
                职称_counts[type_name] += 1
    else:
        # 不要求齐全：职称总数满足要求即可
        # 这里只记录需要的职称类型，具体数量在合并计算时处理
        for type_name in qualification['types']:
            职称_counts[type_name] = 0
    
    return 职称_counts

def merge_qualifications(qualifications):
    """合并多个资质的职称要求，计算最终所需职称数量"""
    # 步骤1：初始化职称计数字典
    final_counts = {}
    
    # 步骤2：初始化资质满足状态字典，标记是否已满足要求
    satisfied = {}
    for qual in qualifications:
        satisfied[qual['name']] = False
    
    # 步骤3：统计每个职称在所有资质中出现的次数（共享次数）
    def count_shared_types():
        """统计每个职称在未满足的资质中出现的次数"""
        shared_counts = {}
        for qual in qualifications:
            if not satisfied[qual['name']]:  # 只考虑未满足的资质
                for type_name in qual['types']:
                    shared_counts[type_name] = shared_counts.get(type_name, 0) + 1
        return shared_counts
    
    # 步骤4：对有职称齐全要求的资质，为其每个职称设置至少1人
    for qual in qualifications:
        if qual['require_all_types']:
            for type_name in qual['types']:
                if type_name not in final_counts:
                    final_counts[type_name] = 1
    
    # 步骤5：检查并标记已满足的资质
    def check_satisfied():
        """检查资质是否已满足要求"""
        for qual in qualifications:
            if satisfied[qual['name']]:
                continue  # 已满足的跳过
                
            # 检查是否满足要求
            if qual['require_all_types']:
                # 检查每个职称至少1人
                all_types_ok = all(final_counts.get(type_name, 0) >= 1 for type_name in qual['types'])
                # 检查总人数满足要求
                current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
                total_ok = current_total >= qual['total_count']
                if all_types_ok and total_ok:
                    satisfied[qual['name']] = True
            else:
                # 只检查总人数
                current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
                if current_total >= qual['total_count']:
                    satisfied[qual['name']] = True
    
    # 初始检查满足情况
    check_satisfied()
    
    # 步骤6：循环处理，直到所有资质都满足要求
    while not all(satisfied.values()):
        # 步骤6.1：统计当前未满足资质的职称共享次数
        shared_counts = count_shared_types()
        
        # 步骤6.2：选择下一个要处理的资质
        # 选择标准：当前缺口最小的资质优先
        candidates = []
        for qual in qualifications:
            if not satisfied[qual['name']]:
                current_total = sum(final_counts.get(type_name, 0) for type_name in qual['types'])
                needed = qual['total_count'] - current_total
                if needed > 0:  # 只处理还需要增加人数的资质
                    candidates.append((needed, qual))
        
        if not candidates:
            break  # 没有需要处理的资质了
        
        # 按缺口从小到大排序，优先处理缺口小的资质
        candidates.sort(key=lambda x: x[0])
        selected_qual = candidates[0][1]
        
        # 步骤6.3：计算还需要多少人
        current_total = sum(final_counts.get(type_name, 0) for type_name in selected_qual['types'])
        needed = selected_qual['total_count'] - current_total
        
        # 步骤6.4：分配所需人数，优先分配到共享次数最多的职称
        while needed > 0:
            # 对当前资质的职称按共享次数排序，共享次数多的优先
            qual_types = selected_qual['types']
            sorted_types = sorted(
                qual_types,
                key=lambda x: (-shared_counts.get(x, 0), final_counts.get(x, 0))
            )
            
            # 分配1人到优先级最高的职称
            top_type = sorted_types[0]
            final_counts[top_type] = final_counts.get(top_type, 0) + 1
            needed -= 1
            
            # 重新检查是否满足要求
            check_satisfied()
            
            # 如果已经满足，就不需要再分配了
            if satisfied[selected_qual['name']]:
                break
    
    # 步骤7：优化结果，移除不必要的分配
    # 统计每个职称的使用情况
    def optimize_counts(counts, quals):
        optimized = counts.copy()
        # 按当前数量从多到少排序职称
        sorted_types = sorted(optimized.keys(), key=lambda x: -optimized[x])
        
        for type_name in sorted_types:
            if optimized[type_name] <= 1:
                continue  # 至少保留1人
            
            # 尝试减少1人，检查是否仍满足所有资质要求
            optimized[type_name] -= 1
            
            # 检查所有资质是否仍满足要求
            all_satisfied = True
            for qual in quals:
                current_total = sum(optimized.get(t, 0) for t in qual['types'])
                if qual['require_all_types']:
                    all_types_ok = all(optimized.get(t, 0) >= 1 for t in qual['types'])
                    if not (all_types_ok and current_total >= qual['total_count']):
                        all_satisfied = False
                        break
                else:
                    if current_total < qual['total_count']:
                        all_satisfied = False
                        break
            
            if not all_satisfied:
                # 恢复减少的人数
                optimized[type_name] += 1
        
        return optimized
    
    # 优化结果
    final_counts = optimize_counts(final_counts, qualifications)
    
    # 步骤8：验证并调整结果
    final_counts = validate_and_adjust(final_counts, qualifications)
    
    # 再次优化，确保总人数最少
    final_counts = optimize_counts(final_counts, qualifications)
    
    # 步骤9：创建职称属性字典
    type_attributes = {}
    # 重新统计所有职称的共享情况
    all_shared_counts = {}
    for qual in qualifications:
        for type_name in qual['types']:
            all_shared_counts[type_name] = all_shared_counts.get(type_name, 0) + 1
    
    # 找出所有有齐全要求的职称类型
    all_required_types = set()
    for qual in qualifications:
        if qual['require_all_types']:
            for type_name in qual['types']:
                all_required_types.add(type_name)
    
    for type_name in final_counts:
        # 检查是否来自有齐全要求的资质
        is_from_all_types = type_name in all_required_types
        # 检查是否是共享的（出现次数大于1）
        is_shared = all_shared_counts.get(type_name, 0) > 1
        # 确定背景颜色：淡红色（有齐全要求或共享）或淡绿色（仅无齐全要求且不共享）
        is_red = is_from_all_types or is_shared
        type_attributes[type_name] = {
            'count': final_counts[type_name],
            'is_red': is_red
        }
    
    return final_counts, type_attributes

def validate_and_adjust(counts, qualifications):
    """验证并调整职称数量，确保所有资质要求都被满足"""
    adjusted_counts = counts.copy()
    
    # 统计职称类型出现次数（共享次数）
    type_counts = {}
    for qual in qualifications:
        for type_name in qual['types']:
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    # 分离有齐全要求和没有齐全要求的资质
    all_types_qualifications = []
    partial_types_qualifications = []
    
    for qual in qualifications:
        if qual['require_all_types']:
            all_types_qualifications.append(qual)
        else:
            partial_types_qualifications.append(qual)
    
    # 按单个要求人数从小到大排序有齐全要求的资质
    all_types_qualifications.sort(key=lambda x: x['total_count'])
    
    # 处理有齐全要求的资质
    for qual in all_types_qualifications:
        # 验证1：每个职称类型至少1人
        for type_name in qual['types']:
            if adjusted_counts.get(type_name, 0) < 1:
                adjusted_counts[type_name] = 1
        
        # 验证2：职称总数满足要求
        current_total = sum(adjusted_counts.get(type_name, 0) for type_name in qual['types'])
        if current_total < qual['total_count']:
            # 需要增加人数
            need_more = qual['total_count'] - current_total
            
            # 循环分配，直到满足人数要求
            while need_more > 0:
                # 对该资质的职称类型进行排序：
                # 1. 共享次数多的优先
                # 2. 当前数量少的优先
                sorted_types = sorted(
                    qual['types'],
                    key=lambda x: (-type_counts.get(x, 0), adjusted_counts.get(x, 0))
                )
                
                # 分配1人到优先级最高的职称类型
                top_type = sorted_types[0]
                adjusted_counts[top_type] = adjusted_counts.get(top_type, 0) + 1
                need_more -= 1
                
                # 重新计算当前总数
                current_total = sum(adjusted_counts.get(type_name, 0) for type_name in qual['types'])
                if current_total >= qual['total_count']:
                    break
    
    # 处理没有齐全要求的资质
    for qual in partial_types_qualifications:
        # 验证职称总数满足要求
        current_total = sum(adjusted_counts.get(type_name, 0) for type_name in qual['types'])
        if current_total < qual['total_count']:
            # 需要增加人数
            need_more = qual['total_count'] - current_total
            
            # 循环分配，直到满足人数要求
            while need_more > 0:
                # 对该资质的职称类型进行排序：
                # 1. 共享次数多的优先
                # 2. 当前数量少的优先
                sorted_types = sorted(
                    qual['types'],
                    key=lambda x: (-type_counts.get(x, 0), adjusted_counts.get(x, 0))
                )
                
                # 分配1人到优先级最高的职称类型
                top_type = sorted_types[0]
                adjusted_counts[top_type] = adjusted_counts.get(top_type, 0) + 1
                need_more -= 1
                
                # 重新计算当前总数
                current_total = sum(adjusted_counts.get(type_name, 0) for type_name in qual['types'])
                if current_total >= qual['total_count']:
                    break
    
    # 最终验证：确保所有资质的要求都被满足
    for qual in qualifications:
        if qual['require_all_types']:
            # 验证每个职称类型至少1人
            for type_name in qual['types']:
                assert adjusted_counts.get(type_name, 0) >= 1, f"资质 {qual['name']} 的职称 {type_name} 人数不足1人"
            # 验证总人数满足要求
            current_total = sum(adjusted_counts.get(type_name, 0) for type_name in qual['types'])
            assert current_total >= qual['total_count'], f"资质 {qual['name']} 的总人数不足，当前 {current_total} 人，需要 {qual['total_count']} 人"
        else:
            # 验证总人数满足要求
            current_total = sum(adjusted_counts.get(type_name, 0) for type_name in qual['types'])
            assert current_total >= qual['total_count'], f"资质 {qual['name']} 的总人数不足，当前 {current_total} 人，需要 {qual['total_count']} 人"
    
    return adjusted_counts

def get_qualification_by_name(name, data):
    """根据名称获取资质信息"""
    for item in data:
        if item['name'] == name:
            return item
    return None

def calculate_total_staff(counts):
    """计算总人数"""
    return sum(counts.values())

def match_qualifications(input_queries):
    """匹配用户输入的资质，计算所需职称数量"""
    # 加载数据
    data = load_qualification_data()
    
    # 解析用户输入，支持逗号分隔
    queries = [q.strip() for q in input_queries.split(',') if q.strip()]
    
    # 匹配资质
    matched_qualifications = []
    for query in queries:
        # 模糊搜索匹配资质
        matches = fuzzy_search(query, data)
        if matches:
            # 使用匹配度最高的结果
            qual_name = matches[0]
            qual = get_qualification_by_name(qual_name, data)
            if qual:
                matched_qualifications.append(qual)
                print(f"匹配到资质: {qual_name}")
        else:
            print(f"未匹配到资质: {query}")
    
    if not matched_qualifications:
        print("未匹配到任何资质，请检查输入")
        return None
    
    # 合并计算
    final_counts, type_attributes = merge_qualifications(matched_qualifications)
    
    # 计算总人数
    total_staff = calculate_total_staff(final_counts)
    
    # 打印结果
    print("\n" + "="*50)
    print("最终所需职称数量")
    print("="*50)
    for type_name, count in sorted(final_counts.items()):
        print(f"{type_name}: {count} 人")
    print("="*50)
    print(f"总人数: {total_staff} 人")
    print("="*50)
    
    # 返回结果
    return {
        "matched_qualifications": [q['name'] for q in matched_qualifications],
        "final_counts": final_counts,
        "total_staff": total_staff
    }
'''
def test_merge_qualifications():
    """测试合并资质功能"""
    data = load_qualification_data()
    
    # 测试用例1：单个资质
    print("测试用例1：单个资质 - 建筑总包二级")
    qual1 = get_qualification_by_name("建筑总包二级", data)
    final_counts1, type_attributes1 = merge_qualifications([qual1])
    print(f"结果: {final_counts1}")
    print(f"总人数: {calculate_total_staff(final_counts1)}")
    # 验证结果
    current_total = sum(final_counts1.get(type_name, 0) for type_name in qual1['types'])
    assert current_total >= qual1['total_count'], f"建筑总包二级的总人数不足，当前 {current_total} 人，需要 {qual1['total_count']} 人"
    if qual1['require_all_types']:
        for type_name in qual1['types']:
            assert final_counts1.get(type_name, 0) >= 1, f"建筑总包二级的职称 {type_name} 人数不足1人"
    print("✓ 测试通过")
    print()
    
    # 测试用例2：两个有齐全要求的资质
    print("测试用例2：两个有齐全要求的资质 - 建筑总包二级 + 机电总包二级")
    qual2 = get_qualification_by_name("机电总包二级", data)
    final_counts2, type_attributes2 = merge_qualifications([qual1, qual2])
    print(f"结果: {final_counts2}")
    print(f"总人数: {calculate_total_staff(final_counts2)}")
    # 验证结果
    for qual in [qual1, qual2]:
        current_total = sum(final_counts2.get(type_name, 0) for type_name in qual['types'])
        assert current_total >= qual['total_count'], f"{qual['name']} 的总人数不足，当前 {current_total} 人，需要 {qual['total_count']} 人"
        if qual['require_all_types']:
            for type_name in qual['types']:
                assert final_counts2.get(type_name, 0) >= 1, f"{qual['name']} 的职称 {type_name} 人数不足1人"
    print("✓ 测试通过")
    print()
    
    # 测试用例3：混合资质（有齐全要求和无齐全要求）
    print("测试用例3：混合资质 - 建筑总包二级 + 市政总包二级")
    qual3 = get_qualification_by_name("市政总包二级", data)
    final_counts3, type_attributes3 = merge_qualifications([qual1, qual3])
    print(f"结果: {final_counts3}")
    print(f"总人数: {calculate_total_staff(final_counts3)}")
    # 验证结果
    for qual in [qual1, qual3]:
        current_total = sum(final_counts3.get(type_name, 0) for type_name in qual['types'])
        assert current_total >= qual['total_count'], f"{qual['name']} 的总人数不足，当前 {current_total} 人，需要 {qual['total_count']} 人"
        if qual['require_all_types']:
            for type_name in qual['types']:
                assert final_counts3.get(type_name, 0) >= 1, f"{qual['name']} 的职称 {type_name} 人数不足1人"
    print("✓ 测试通过")
    print()
    
    # 测试用例4：多个资质
    print("测试用例4：多个资质 - 建筑总包二级 + 机电总包二级 + 市政总包二级 + 电力总包二级")
    qual4 = get_qualification_by_name("电力总包二级", data)
    final_counts4, type_attributes4 = merge_qualifications([qual1, qual2, qual3, qual4])
    print(f"结果: {final_counts4}")
    print(f"总人数: {calculate_total_staff(final_counts4)}")
    # 验证结果
    for qual in [qual1, qual2, qual3, qual4]:
        current_total = sum(final_counts4.get(type_name, 0) for type_name in qual['types'])
        assert current_total >= qual['total_count'], f"{qual['name']} 的总人数不足，当前 {current_total} 人，需要 {qual['total_count']} 人"
        if qual['require_all_types']:
            for type_name in qual['types']:
                assert final_counts4.get(type_name, 0) >= 1, f"{qual['name']} 的职称 {type_name} 人数不足1人"
    print("✓ 测试通过")
    print()
    
    # 测试用例5：单个无齐全要求的资质
    print("测试用例5：单个无齐全要求的资质 - 市政总包二级")
    final_counts5, type_attributes5 = merge_qualifications([qual3])
    print(f"结果: {final_counts5}")
    print(f"总人数: {calculate_total_staff(final_counts5)}")
    # 验证结果
    current_total = sum(final_counts5.get(type_name, 0) for type_name in qual3['types'])
    assert current_total >= qual3['total_count'], f"{qual3['name']} 的总人数不足，当前 {current_total} 人，需要 {qual3['total_count']} 人"
    print("✓ 测试通过")
    print()
    
    # 测试用例6：多个无齐全要求的资质
    print("测试用例6：多个无齐全要求的资质 - 市政总包二级 + 电力总包二级")
    final_counts6, type_attributes6 = merge_qualifications([qual3, qual4])
    print(f"结果: {final_counts6}")
    print(f"总人数: {calculate_total_staff(final_counts6)}")
    # 验证结果
    for qual in [qual3, qual4]:
        current_total = sum(final_counts6.get(type_name, 0) for type_name in qual['types'])
        assert current_total >= qual['total_count'], f"{qual['name']} 的总人数不足，当前 {current_total} 人，需要 {qual['total_count']} 人"
    print("✓ 测试通过")
    print()
    
    print("所有测试用例通过！")
'''
if __name__ == "__main__":
    # 测试合并资质功能
    # test_merge_qualifications()
    
    # 测试用户输入匹配
    print("\n" + "="*50)
    print("用户输入匹配测试")
    print("="*50)
    match_qualifications("建筑二, 市政二, 机电")
    
