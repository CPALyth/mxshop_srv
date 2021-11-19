import requests

headers = {
    "contentType": "application/json"
}

BASE_URL = "http://127.0.0.1:8500"


def register_http(name, id, address, port, *tags):
    url = f"{BASE_URL}/v1/agent/service/register"
    rsp = requests.put(url=url, headers=headers, json={
        "Name": name,
        "ID": id,
        "Address": address,
        "Port": port,
        "Tags": tags,
        "Check": { # 健康检查
            "HTTP": f"http://{address}:{port}/health",
            "Timeout": "5s",
            "Interval": "5s",
            "DeregisterCriticalServiceAfter": "15s",
        }
    })
    if rsp.status_code == 200:
        print("注册成功")
    else:
        print(f"注册失败: {rsp.status_code}")


def register_grpc(name, id, address, port, *tags):
    url = f"{BASE_URL}/v1/agent/service/register"
    rsp = requests.put(url=url, headers=headers, json={
        "Name": name,
        "ID": id,
        "Address": address,
        "Port": port,
        "Tags": tags,
        "Check": { # 健康检查
            "GRPC": f"{address}:{port}",
            "GRPCUseTLS": False,
            "Timeout": "5s",
            "Interval": "5s",
            "DeregisterCriticalServiceAfter": "15s",
        }
    })
    if rsp.status_code == 200:
        print("注册成功")
    else:
        print(f"注册失败: {rsp.status_code}")


def deregister(id):
    url = f"{BASE_URL}/v1/agent/service/deregister/{id}"
    rsp = requests.put(url, headers=headers)
    if rsp.status_code == 200:
        print("注销成功")
    else:
        print(f"注销失败: {rsp.status_code}")


def filter_service(name):
    url = f"{BASE_URL}/v1/agent/services"
    params = {
        "filter": f'Service == "{name}"'
    }
    rsp = requests.get(url, params=params).json()
    for key, value in rsp.items():
        print(key)
    print(rsp)


if __name__ == '__main__':
    register_http("user_api", "user_api", "192.168.1.103", 8021)
    # deregister("mxshop_srv")
    # filter_service("mxshop_srv")