import requests

headers = {
    "contentType": "application/json"
}

BASE_URL = "http://127.0.0.1:8500"

def register(name, id, address, port):
    url = f"{BASE_URL}/v1/agent/service/register"
    rsp = requests.put(url=url, headers=headers, json={
        "Name": name,
        "ID": id,
        "Tags": ["mxshop", "bobby", "imooc", "web"],
        "Address": address,
        "Port": port,
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


if __name__ == '__main__':
    register("mxshop_srv", "mxshop_srv", "192.168.1.103", 50051)
    # deregister("mxshop_srv")