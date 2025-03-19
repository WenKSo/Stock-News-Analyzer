import requests
import json
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DingTalkBot")

class DingTalkBot:
    def __init__(self, webhook_url: str, secret: str):
        """
        初始化钉钉机器人
        
        参数:
        webhook_url: 钉钉机器人的Webhook地址
        secret: 加签密钥
        """
        self.webhook_url = webhook_url
        self.secret = secret
    
    def _get_signed_url(self) -> str:
        """
        生成加签后的URL
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        # 构建完整的URL
        signed_url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        return signed_url
    
    def send_text(self, content: str, at_mobiles: Optional[List[str]] = None, at_all: bool = False) -> bool:
        """
        发送文本消息
        
        参数:
        content: 消息内容
        at_mobiles: 要@的手机号列表
        at_all: 是否@所有人
        
        返回:
        bool: 是否发送成功
        """
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            if at_mobiles or at_all:
                data["at"] = {
                    "atMobiles": at_mobiles if at_mobiles else [],
                    "isAtAll": at_all
                }
            
            signed_url = self._get_signed_url()
            response = requests.post(
                signed_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("钉钉消息发送成功")
                    return True
                else:
                    logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                logger.error(f"钉钉消息发送失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"钉钉消息发送异常: {str(e)}")
            return False
    
    def send_markdown(self, title: str, content: str, at_mobiles: Optional[List[str]] = None, at_all: bool = False) -> bool:
        """
        发送Markdown消息
        
        参数:
        title: 消息标题
        content: Markdown格式的消息内容
        at_mobiles: 要@的手机号列表
        at_all: 是否@所有人
        
        返回:
        bool: 是否发送成功
        """
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                }
            }
            
            if at_mobiles or at_all:
                data["at"] = {
                    "atMobiles": at_mobiles if at_mobiles else [],
                    "isAtAll": at_all
                }
            
            signed_url = self._get_signed_url()
            response = requests.post(
                signed_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("钉钉消息发送成功")
                    return True
                else:
                    logger.error(f"钉钉消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                logger.error(f"钉钉消息发送失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"钉钉消息发送异常: {str(e)}")
            return False 