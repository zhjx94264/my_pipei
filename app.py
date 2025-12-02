from flask import Flask, request, jsonify, render_template
import json
from fuzzy_search import load_qualification_data, fuzzy_search
from qualification_matcher import merge_qualifications, get_qualification_by_name, calculate_total_staff

app = Flask(__name__)

# 动态加载资质数据，每次请求时重新加载
def get_qualification_data():
    return load_qualification_data()

@app.route('/')
def index():
    # 加载资质数据，直接传递给模板
    qualification_data = get_qualification_data()
    return render_template('index.html', qualification_data=qualification_data)

@app.route('/api/search', methods=['GET'])
def search_qualifications():
    """模糊搜索资质名称"""
    # 确保正确处理中文编码
    query = request.args.get('q', '').strip()
    
    # 添加调试信息
    print(f"Received search query: '{query}'")
    
    qualification_data = get_qualification_data()
    
    if not query:
        # 没有查询参数时返回所有资质名称
        matches = [q['name'] for q in qualification_data]
    else:
        # 有查询参数时进行模糊搜索
        matches = fuzzy_search(query, qualification_data)
    
    print(f"Search results: {matches}")
    
    return jsonify(matches)

@app.route('/api/match', methods=['POST'])
def match_qualifications():
    """匹配资质，计算所需职称数量"""
    data = request.json
    qualifications = data.get('qualifications', [])
    
    if not qualifications:
        return jsonify({
            'error': '请至少选择一个资质'
        })
    
    # 获取匹配的资质信息
    qualification_data = get_qualification_data()
    matched_qualifications = []
    for qual_name in qualifications:
        qual = get_qualification_by_name(qual_name, qualification_data)
        if qual:
            matched_qualifications.append(qual)
    
    if not matched_qualifications:
        return jsonify({
            'error': '未匹配到任何有效资质'
        })
    
    # 合并计算
    final_counts, type_attributes = merge_qualifications(matched_qualifications)
    total_staff = calculate_total_staff(final_counts)
    
    return jsonify({
        'matched_qualifications': [q['name'] for q in matched_qualifications],
        'matched_qualifications_details': matched_qualifications,
        'final_counts': final_counts,
        'type_attributes': type_attributes,
        'total_staff': total_staff
    })

@app.route('/api/qualifications', methods=['GET'])
def get_all_qualifications():
    """获取所有资质信息"""
    qualification_data = get_qualification_data()
    return jsonify([q['name'] for q in qualification_data])

@app.route('/api/qualifications/all', methods=['GET'])
def get_all_qualifications_details():
    """获取所有资质的详细信息"""
    qualification_data = get_qualification_data()
    return jsonify(qualification_data)

@app.route('/verify')
def verify_page():
    """渲染资质验证页面"""
    qualification_data = get_qualification_data()
    return render_template('verify.html', qualification_data=qualification_data)

@app.route('/api/verify', methods=['POST'])
def verify_qualifications():
    """验证资质匹配情况"""
    data = request.json
    qualifications = data.get('qualifications', [])
    title_counts = data.get('title_counts', {})
    
    if not qualifications:
        return jsonify({
            'error': '请至少选择一个资质'
        })
    
    # 获取匹配的资质信息
    qualification_data = get_qualification_data()
    matched_qualifications = []
    for qual_name in qualifications:
        qual = get_qualification_by_name(qual_name, qualification_data)
        if qual:
            matched_qualifications.append(qual)
    
    if not matched_qualifications:
        return jsonify({
            'error': '未匹配到任何有效资质'
        })
    
    # 验证每个资质
    verification_results = []
    
    for qual in matched_qualifications:
        # 检查当前资质的职称类型和数量
        current_total = 0
        title_details = []
        missing_types = []
        reasons = []
        
        # 计算当前资质的总人数
        for type_name in qual['types']:
            count = title_counts.get(type_name, 0)
            current_total += count
            title_details.append({
                'title': type_name,
                'count': count,
                'satisfied': count >= 1
            })
            
            if count < 1:
                missing_types.append(type_name)
        
        # 检查是否满足要求
        all_types_ok = len(missing_types) == 0
        total_ok = current_total >= qual['total_count']
        
        if qual['require_all_types']:
            # 需要所有类型齐全
            if not all_types_ok:
                reasons.append(f'缺少以下职称类型：{"、".join(missing_types)}')
            if not total_ok:
                reasons.append(f'总人数不足：当前 {current_total} 人，需要 {qual["total_count"]} 人')
            satisfied = all_types_ok and total_ok
        else:
            # 不需要所有类型齐全，只检查总人数
            if not total_ok:
                reasons.append(f'总人数不足：当前 {current_total} 人，需要 {qual["total_count"]} 人')
            satisfied = total_ok
        
        verification_results.append({
            'qualification_name': qual['name'],
            'satisfied': satisfied,
            'current_total': current_total,
            'required_total': qual['total_count'],
            'require_all_types': qual['require_all_types'],
            'title_details': title_details,
            'reasons': reasons
        })
    
    return jsonify({
        'verification_results': verification_results
    })

if __name__ == '__main__':
    import sys
    import os
    
    # 从命令行参数或环境变量获取端口，默认5006
    port = 5006
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    # 尝试从环境变量获取端口
    env_port = os.environ.get('FLASK_PORT')
    if env_port:
        try:
            port = int(env_port)
        except ValueError:
            pass
    
    app.run(debug=False, host='0.0.0.0', port=port)
    
