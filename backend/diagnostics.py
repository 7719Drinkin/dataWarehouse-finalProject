#!/usr/bin/env python3
"""
数据库连接诊断脚本
"""
import socket
import time
from config.database import DatabaseConfig

def check_port_connectivity(host: str, port: int, timeout: int = 5) -> dict:
    """检查端口连通性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()

        sock.close()

        return {
            'host': host,
            'port': port,
            'connected': result == 0,
            'response_time': round((end_time - start_time) * 1000, 2),  # ms
            'error': None if result == 0 else f"Connection failed (code: {result})"
        }
    except Exception as e:
        return {
            'host': host,
            'port': port,
            'connected': False,
            'response_time': None,
            'error': str(e)
        }

def diagnose_database_connections():
    """诊断数据库连接"""
    config = DatabaseConfig()

    print("🔍 数据库连接诊断")
    print("=" * 50)

    # 检查OpenGauss连接
    print("\n📊 OpenGauss 连接诊断:")
    og_result = check_port_connectivity(config.OPENGAUSS_HOST, config.OPENGAUSS_PORT)
    print(f"  主机: {og_result['host']}:{og_result['port']}")
    print(f"  状态: {'✅ 连接成功' if og_result['connected'] else '❌ 连接失败'}")
    if og_result['response_time']:
        print(f"  响应时间: {og_result['response_time']}ms")
    if og_result['error']:
        print(f"  错误: {og_result['error']}")

    # 检查Hive连接
    print("\n🐝 Hive 连接诊断:")
    hive_result = check_port_connectivity(config.HIVE_HOST, config.HIVE_PORT)
    print(f"  主机: {hive_result['host']}:{hive_result['port']}")
    print(f"  状态: {'✅ 连接成功' if hive_result['connected'] else '❌ 连接失败'}")
    if hive_result['response_time']:
        print(f"  响应时间: {hive_result['response_time']}ms")
    if hive_result['error']:
        print(f"  错误: {hive_result['error']}")

    # 检查Neo4j连接
    print("\n🕸️  Neo4j 连接诊断:")
    neo4j_uri = config.NEO4J_URI.replace('bolt://', '')
    if ':' in neo4j_uri:
        host, port_str = neo4j_uri.split(':')
        port = int(port_str)
    else:
        host = neo4j_uri
        port = 7687

    neo4j_result = check_port_connectivity(host, port)
    print(f"  主机: {neo4j_result['host']}:{neo4j_result['port']}")
    print(f"  状态: {'✅ 连接成功' if neo4j_result['connected'] else '❌ 连接失败'}")
    if neo4j_result['response_time']:
        print(f"  响应时间: {neo4j_result['response_time']}ms")
    if neo4j_result['error']:
        print(f"  错误: {neo4j_result['error']}")

    print("\n" + "=" * 50)
    print("💡 诊断建议:")
    print("  - 如果连接失败，请检查:")
    print("    1. 服务器防火墙设置")
    print("    2. 数据库服务是否启动")
    print("    3. 网络连接和VPN设置")
    print("    4. 安全组规则配置")

    # 返回连接状态摘要
    all_connected = all([
        og_result['connected'],
        hive_result['connected'],
        neo4j_result['connected']
    ])

    return {
        'all_connected': all_connected,
        'opengauss': og_result,
        'hive': hive_result,
        'neo4j': neo4j_result
    }

if __name__ == '__main__':
    result = diagnose_database_connections()
    print(f"\n🎯 总体状态: {'✅ 所有数据库均可连接' if result['all_connected'] else '❌ 部分数据库连接失败'}")

