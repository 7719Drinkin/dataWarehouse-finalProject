#!/usr/bin/env python3
"""
数据库连接测试脚本
"""
import sys
import time
from app.models.opengauss.models import OpenGaussModel
from app.models.hive.models import HiveModel
from app.models.neo4j.models import Neo4jModel

def test_database_connections():
    """测试数据库连接"""
    print("🧪 数据库连接测试")
    print("=" * 50)

    results = {}

    # 测试OpenGauss连接
    print("\n📊 测试 OpenGauss 连接...")
    try:
        og_model = OpenGaussModel()
        with og_model:
            # 尝试执行一个简单的查询
            result = og_model.execute_query("SELECT 1 as test")
            results['opengauss'] = {'connected': True, 'result': result}
            print("  ✅ OpenGauss 连接成功")
    except Exception as e:
        results['opengauss'] = {'connected': False, 'error': str(e)}
        print(f"  ❌ OpenGauss 连接失败: {e}")

    # 测试Hive连接
    print("\n🐝 测试 Hive 连接...")
    try:
        hive_model = HiveModel()
        with hive_model:
            # 尝试执行一个简单的查询
            result = hive_model.execute_query("SELECT 1 as test")
            results['hive'] = {'connected': True, 'result': result}
            print("  ✅ Hive 连接成功")
    except Exception as e:
        results['hive'] = {'connected': False, 'error': str(e)}
        print(f"  ❌ Hive 连接失败: {e}")

    # 测试Neo4j连接
    print("\n🕸️  测试 Neo4j 连接...")
    try:
        neo4j_model = Neo4jModel()
        with neo4j_model:
            # 尝试执行一个简单的查询
            result = neo4j_model.execute_query("RETURN 1 as test")
            results['neo4j'] = {'connected': True, 'result': result}
            print("  ✅ Neo4j 连接成功")
    except Exception as e:
        results['neo4j'] = {'connected': False, 'error': str(e)}
        print(f"  ❌ Neo4j 连接失败: {e}")

    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")

    all_connected = True
    for db_name, result in results.items():
        status = "✅ 成功" if result['connected'] else "❌ 失败"
        print(f"  {db_name.upper()}: {status}")
        if not result['connected']:
            all_connected = False
            print(f"    错误: {result['error']}")

    if all_connected:
        print("\n🎉 所有数据库连接测试通过！后端可以正常启动。")
        return True
    else:
        print("\n⚠️  部分数据库连接失败，请检查配置和网络连接。")
        print("💡 建议：")
        print("  1. 运行 'python diagnostics.py' 检查网络连通性")
        print("  2. 检查服务器防火墙和安全组设置")
        print("  3. 验证数据库服务是否启动")
        print("  4. 确认用户名、密码和数据库名称")
        return False

if __name__ == '__main__':
    success = test_database_connections()
    sys.exit(0 if success else 1)

