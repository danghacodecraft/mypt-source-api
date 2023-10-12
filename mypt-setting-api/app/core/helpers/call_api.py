import json
import requests

def call_api(**kwargs):
    try:
        url = kwargs.get('url', None)
        data = kwargs.get('payload', None)
        params = kwargs.get('params', None)
        headers = kwargs.get('headers', None)
        method = kwargs.get('method', None)
        proxies = kwargs.get('proxies', None)

        result = requests.request(
            method=method, 
            url=url, 
            params=params,
            data=json.dumps(data),
            headers=headers,
            proxies=proxies,
            verify=False
        )
        result = result.text
        try:
            result = json.loads(result)
        except Exception as e:
            print(e)
        return result

    except Exception as e:
        print("->", e)
        return {
            "data": str(e),
            "code": "call_api_fail"
        }