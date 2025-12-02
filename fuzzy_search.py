import json
import re

def load_qualification_data():
    """加载资质数据"""
    with open('qualification_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_jaccard_similarity(str1, str2):
    """计算Jaccard相似度"""
    set1 = set(str1)
    set2 = set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def calculate_levenshtein_distance(str1, str2):
    """计算Levenshtein距离"""
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if str1[i-1] == str2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # 删除
                dp[i][j-1] + 1,      # 插入
                dp[i-1][j-1] + cost  # 替换
            )
    
    # 转换为相似度（0-1之间）
    max_len = max(m, n)
    return 1 - (dp[m][n] / max_len) if max_len != 0 else 1

def fuzzy_search(query, data, threshold=0.3):
    """模糊搜索资质名称"""
    results = []
    query = query.strip()
    
    for item in data:
        name = item['name']
        
        # 精确匹配优先
        if query == name:
            results.append((name, 1.0))
            continue
        
        # 1. 检查是否是前缀匹配（如"建筑"匹配"建筑总包二级"）
        if name.startswith(query):
            results.append((name, 0.9))
            continue
        
        # 2. 检查是否是包含关系且关键词与资质类型相关（如"建筑二"匹配"建筑总包二级"）
        # 这里我们只匹配包含关键词且关键词与资质类型相关的情况
        # 例如："建筑二"匹配"建筑总包二级"，但"建筑总包"不匹配"市政总包二级"
        
        # 特殊处理：如果关键词包含"总包"，则只匹配完全包含该关键词的资质
        if "总包" in query:
            if query in name:
                results.append((name, 0.8))
            continue
        
        # 3. 处理"建筑二"这种情况，匹配"建筑总包二级"
        # 检查关键词的字符是否按顺序出现在名称中，且考虑资质类型
        contains_match = True
        last_index = -1
        for char in query:
            index = name.find(char, last_index + 1)
            if index == -1:
                contains_match = False
                break
            last_index = index
        
        if contains_match:
            # 计算匹配得分
            # 得分1：关键词长度占名称长度的比例
            length_score = len(query) / len(name)
            # 得分2：关键词字符在名称中连续出现的程度
            intervals = []
            prev_index = -1
            for char in query:
                curr_index = name.find(char, prev_index + 1)
                if prev_index != -1:
                    intervals.append(curr_index - prev_index - 1)
                prev_index = curr_index
            
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            continuity_score = 1 / (1 + avg_interval)  # 间隔越小，得分越高
            
            # 总得分
            total_score = length_score * 0.6 + continuity_score * 0.4
            results.append((name, total_score))
            continue
        
        # 4. 计算Levenshtein相似度（用于更模糊的匹配）
        levenshtein_sim = calculate_levenshtein_distance(query, name)
        if levenshtein_sim >= threshold:
            results.append((name, levenshtein_sim))
    
    # 按相似度降序排序
    results.sort(key=lambda x: x[1], reverse=True)
    
    # 返回匹配的资质名称列表
    return [result[0] for result in results]

def test_fuzzy_search():
    """测试模糊搜索功能"""
    data = load_qualification_data()
    
    test_queries = [
        "建筑二",
        "市政二",
        "机电",
        "电力",
        "水利",
        "公路",
        "冶金"
    ]
    
    print("模糊搜索测试结果：")
    print("=" * 50)
    
    for query in test_queries:
        matches = fuzzy_search(query, data)
        print(f"查询：'{query}'")
        print(f"匹配结果：{matches}")
        print()

if __name__ == "__main__":
    test_fuzzy_search()