from datetime import datetime
from typing import Optional, Any, Dict

import httpx

from app.core.event import EventManager
from app.plugins import PluginBase
from app.schemas.types import SystemEventType


class HDHive(PluginBase):
    """影巢 HDHive 签到插件"""

    plugin_name = "影巢签到"
    plugin_desc = "自动完成影巢站点签到，支持定时任务"
    plugin_ver = "1.0.0"
    plugin_author = "kingbb2001"
    plugin_icon = "https://www.hdhive.com/favicon.ico"

    sign_url = "https://hdhive.com/user/sign"

    def __init__(self, event_manager: EventManager, settings=None):
        super().__init__(event_manager, settings)
        self._cookie = None

    def get_schema(self) -> list:
        return [
            {
                "component": "VAlert",
                "props": {
                    "type": "info",
                    "text": True,
                    "children": [
                        "签到前请确保已在影巢网页端登录，",
                        "然后在浏览器开发者工具(F12)中复制 Cookie 填入下方。"
                    ]
                }
            },
            {
                "component": "VTextField",
                "props": {
                    "label": "Cookie",
                    "model": "cookie",
                    "type": "password",
                    "hint": "填入影巢登录后的完整 Cookie",
                    "persistent_hint": True,
                }
            },
            {
                "component": "VSwitch",
                "props": {
                    "label": "开启自动签到",
                    "model": "auto_sign",
                }
            },
        ]

    def init_plugin(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config:
            self._cookie = config.get("cookie")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://hdhive.com",
            "Referer": "https://hdhive.com/",
            "Cookie": self._cookie or "",
        }

    async def _do_signin(self) -> tuple[bool, str]:
        if not self._cookie:
            return False, "未配置 Cookie，请先在插件设置中填入 Cookie"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.sign_url,
                    headers=self._get_headers(),
                )
                result = response.json()

                if response.status_code == 200:
                    if result.get("code") == 0 or result.get("success") is True:
                        return True, f"签到成功：{result.get('msg', '已完成签到')}"
                    else:
                        msg = result.get("msg") or result.get("message") or "签到失败"
                        if "已签到" in msg or "已领取" in msg:
                            return True, f"今日已签到：{msg}"
                        return False, f"签到失败：{msg}"
                else:
                    return False, f"HTTP错误：{response.status_code}"

        except httpx.TimeoutException:
            return False, "请求超时，请检查网络"
        except httpx.RequestError as e:
            return False, f"网络错误：{str(e)}"
        except Exception as e:
            return False, f"未知错误：{str(e)}"

    def get_commands(self) -> list:
        return [
            {
                "cmd": "/hdhive_sign",
                "event": SystemEventType.PluginAction,
                "desc": "影巢签到",
                "category": "站点签到",
                "data": {
                    "action": "hdhive_sign"
                }
            }
        ]

    async def sign_handler(self, event_data: Dict[str, Any]) -> None:
        action = event_data.get("action")
        if action != "hdhive_sign":
            return

        success, message = await self._do_signin()
        await self.post_message(
            title="影巢签到",
            text=message,
            success=success
        )

    def get_services(self) -> list:
        return [
            {
                "id": "hdhive_daily_sign",
                "name": "影巢每日签到",
                "trigger": "cron",
                "func": self._daily_sign_task,
                "kwargs": {
                    "hour": 8,
                    "minute": 0,
                }
            }
        ]

    async def _daily_sign_task(self) -> None:
        if not self._settings.get("auto_sign"):
            return

        success, message = await self._do_signin()
        await self.post_message(
            title="影巢定时签到",
            text=message,
            success=success
        )
