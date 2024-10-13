from time import sleep
import httpx
from .base import CaptchaSolver
from twocaptcha import TwoCaptcha as TwoCaptchaSolver

class TwoCaptcha(CaptchaSolver):
    def __init__(
        self,
        api_key: str,
        max_attempts: int = 3,
        get_result_interval: float = 1.0,
        use_blob_data: bool = False
    ) -> None:
        self.api_key = api_key
        self.get_result_interval = get_result_interval
        self.max_attempts = max_attempts
        self.use_blob_data = use_blob_data

    def create_task(self, task_data: dict) -> dict:
        data = {
            'clientKey': self.api_key,
            'task': task_data
        }
        response = httpx.post(
            'https://api.2captcha.com/createTask',
            json=data,
            headers={'content-type': 'application/json'}
        ).json()
        return response

    def get_task_result(self, task_id: str) -> dict:
        data = {
            'clientKey': self.api_key,
            'taskId': task_id
        }
        response = httpx.post(
            'https://api.2captcha.com/getTaskResult',
            json=data,
            headers={'content-type': 'application/json'}
        ).json()
        return response

    def solve_funcaptcha(self, blob: str) -> dict:
        if self.client.proxy is None:
            captcha_type = 'FunCaptchaTaskProxyLess'
        else:
            captcha_type = 'FunCaptchaTask'

        task_data = {
            'type': captcha_type,
            'websiteURL': 'https://iframe.arkoselabs.com',
            'websitePublicKey': self.CAPTCHA_SITE_KEY,
            'funcaptchaApiJSSubdomain': 'https://client-api.arkoselabs.com',
            'proxy': self.client.proxy
        }
        if self.use_blob_data:
            task_data['data'] = '{"blob":"%s"}' % blob
            task_data['userAgent'] = self.client._user_agent
        task = self.create_task(task_data)
        while True:
            sleep(self.get_result_interval)
            result = self.get_task_result(task['taskId'])
            if result['status'] in ('ready', 'failed'):
                return result
