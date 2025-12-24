#!/usr/bin/env python3
"""
测试后端代码语法
"""

def test_imports():
    """测试模块导入"""
    try:
        # 测试基础模块
        import sys
        sys.path.insert(0, '.')

        # 测试各个模块的语法
        modules_to_test = [
            'app.models.base.base_model',
            'config.database',
            'app.utils.response_utils',
            'app.utils.validation_utils',
            'app.services.performance_service',
            'app.controllers.api.query_controller'
        ]

        for module in modules_to_test:
            try:
                __import__(module)
                print(f"✅ {module} - 语法正确")
            except SyntaxError as e:
                print(f"❌ {module} - 语法错误: {e}")
                return False
            except ImportError as e:
                print(f"⚠️  {module} - 依赖缺失: {e}")
            except Exception as e:
                print(f"❌ {module} - 其他错误: {e}")
                return False

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == '__main__':
    print("开始测试后端代码语法...")
    success = test_imports()
    if success:
        print("\n🎉 所有模块语法检查通过！")
    else:
        print("\n💥 发现语法错误！")
        exit(1)

