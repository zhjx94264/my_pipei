# zhjx-pipei
一个关于对建筑资质职称人员进行匹配: Python + Flask

<!--
**zhjx94264/zhjx94264** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
# 资质匹配动态规划算法实现

## 概述
本文件夹包含使用动态规划算法实现的资质匹配功能，与原项目使用相同的规则和前端显示效果，但采用不同的算法实现。

## 文件结构
```
dp_new/
├── app.py                  # Flask应用，与现有项目兼容
├── dp_qualification_matcher.py  # 动态规划匹配算法实现
├── fuzzy_search.py         # 模糊搜索功能
├── test_dp_algorithm.py    # 测试文件
└── README.md               # 本说明文件
```

## 主要功能
1. 模糊搜索资质名称
2. 匹配用户输入的资质，计算所需职称数量
3. 计算技术负责人
4. 计算安许要求
5. 验证资质匹配情况

## 算法特点
- 使用动态规划算法，通过状态转移寻找最优解
- 优先满足有"require_all_types": true的资质
- 优先选择共享次数多的职称，以最小化总人数
- 使用BFS遍历状态空间，确保找到最优解
- 包含贪婪算法作为备选，防止算法超时

## 与原算法的区别
1. **算法类型**：原算法使用循环迭代，新算法使用动态规划
2. **状态管理**：新算法显式管理每个状态，确保找到最优解
3. **性能优化**：新算法通过优先级排序和状态剪枝，提高计算效率
4. **备选方案**：新算法包含贪婪算法作为备选，提高鲁棒性

## 安装和运行
1. 确保已安装Python 3和Flask
2. 运行以下命令启动服务：
   ```
   python3 app.py
   ```
3. 默认端口为5007，可通过命令行参数或环境变量修改

## 测试
运行测试文件验证算法功能：
```
python3 test_dp_algorithm.py
```

## API接口
与原项目使用相同的API接口，确保前端兼容性：
- `/api/search` - 模糊搜索资质名称
- `/api/match` - 匹配资质，计算所需职称数量
- `/api/qualifications` - 获取所有资质信息
- `/api/qualifications/all` - 获取所有资质的详细信息
- `/api/verify` - 验证资质匹配情况

## 注意事项
1. 动态规划算法在处理大量资质时可能会消耗较多资源
2. 算法包含超时保护机制，当计算时间过长时会自动切换到贪婪算法
3. 新算法与原算法的结果可能会略有不同，但都满足所有资质要求

## 性能优化
- 只处理前3个最高优先级的职称类型，减少状态空间
- 设置最大总人数上限，防止无限循环
- 使用BFS遍历，确保找到最优解
- 包含状态剪枝，跳过不可能的状态
