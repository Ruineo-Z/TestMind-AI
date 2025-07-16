"""
测试服务器连接
"""
import asyncio
import httpx


async def test_connection():
    """测试连接"""
    base_url = "http://127.0.0.1:8001"
    
    print(f"测试连接到: {base_url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(f"{base_url}/api/v1/documents/formats")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            return response.status_code == 200
    except Exception as e:
        print(f"连接失败: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    print(f"连接结果: {result}")
