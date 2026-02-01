"""
MyAnime Cafe 自動訂位機器人
使用 Playwright 自動化預約 inline.app 訂位系統
"""

import logging
import os
import time
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field

# 設置日誌
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


class BookingConfig(BaseModel):
    """訂位配置模型"""

    url: str = Field(description="訂位網址")
    name: str = Field(min_length=2, description="預約人姓名（需與證件相符）")
    phone: str = Field(pattern=r"^09\d{8}$", description="預約電話")
    email: Optional[str] = Field(description="預約信箱")
    party_size: int = Field(ge=1, le=4, description="用餐人數 (1-4)")
    times: list[str] = Field(
        min_length=1, description="偏好時段列表，如 ['14:30', '16:00']"
    )
    date: Optional[str] = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}$", description="目標日期 (YYYY-MM-DD)"
    )
    headless: bool = Field(default=False, description="是否以無頭模式運行瀏覽器")


class InlineBookingBot:
    """Inline 訂位機器人"""

    def __init__(self, config: BookingConfig):
        self.config = config
        self.url = config.url
        self.name = config.name
        self.phone = config.phone
        self.email = config.email or ""
        self.party_size = config.party_size
        self.times = config.times
        self.date = config.date
        self.headless = config.headless

    def run(self) -> bool:
        """
        執行訂位流程

        Returns:
            bool: 訂位是否成功
        """
        logger.info("=" * 60)
        logger.info("開始執行訂位機器人")
        logger.info(f"目標餐廳: {self.url}")
        logger.info(f"預約人數: {self.party_size} 人")
        logger.info(f"偏好時段: {', '.join(self.times)}")
        logger.info("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            # browser = p.chromium.connect_over_cdp(self.url)
            context = browser.new_context(
                viewport={"width": 1000, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                locale="en,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,zh-CN;q=0.6",
                timezone_id="Asia/Taipei",
                permissions=["geolocation"],
                has_touch=False,  # 桌面環境
                is_mobile=False,
                java_script_enabled=True,
                color_scheme="light",
            )

            page = context.new_page()

            try:
                # 步驟 1: 載入訂位頁面
                logger.info("正在載入訂位頁面...")
                page.goto(self.url)
                self._random_delay(1.0, 2.0)

                # 步驟 2: 選擇用餐人數
                success = self._select_party_size(page)
                if not success:
                    return False

                # 步驟 3: 選擇日期
                success = self._select_date(page)
                if not success:
                    return False

                # 步驟 4: 選擇時段
                success = self._select_time_slot(page)
                if not success:
                    return False

                # 步驟 5: 填寫預約資料
                success = self._fill_booking_form(page)
                if not success:
                    return False

                # 步驟 6: 確認送出
                success = self._confirm_booking(page)
                if not success:
                    return False

                logger.info("✅ 訂位成功！")
                time.sleep(3)  # 讓用戶看到結果
                return True

            except Exception as e:
                logger.error(f"❌ 發生錯誤: {e}")
                page.screenshot(
                    path=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                return False

            finally:
                browser.close()

    def _random_delay(self, min_seconds: float, max_seconds: float):
        """隨機延遲模擬人類行為"""
        delay = min_seconds + (max_seconds - min_seconds) * 0.5
        time.sleep(delay)

    def _select_party_size(self, page) -> bool:
        """選擇用餐人數"""
        try:
            logger.info(f"選擇用餐人數: {self.party_size} 人")

            # 等待人數選擇器出現
            dropdown = page.locator("#adult-picker")
            dropdown.wait_for(state="visible")

            # 選擇人數
            dropdown.select_option(str(self.party_size))

            logger.info(f"✓ 已選擇 {self.party_size} 人")
            self._random_delay(0.8, 1.5)

            return True

        except Exception as e:
            logger.error(f"❌ 無法選擇人數: {e}")
            return False

    def _select_date(self, page) -> bool:
        """選擇用餐日期"""
        try:
            if self.date:
                target = datetime.strptime(self.date, "%Y-%m-%d")
            else:
                target = datetime.now()
            logger.info(f"選擇日期: {target.strftime('%Y-%m-%d')}")

            # 日期下拉選單
            dropdown = page.locator("#date-picker")
            dropdown.wait_for(state="visible")
            self._random_delay(0.3, 0.8)
            dropdown.click()
            self._random_delay(0.5, 1.0)

            # 日曆選擇器
            calendar = page.locator("#calendar-picker")
            calendar.wait_for(state="visible")

            # 找到包含目標日期的按鈕: 使用 data-cy 屬性配合文字內容篩選
            day_str = str(target.day)
            day_button = page.locator(
                f'[data-cy="bt-cal-day"]:has-text("{day_str}")'
            ).first

            self._random_delay(0.3, 0.7)
            day_button.click()
            self._random_delay(0.8, 1.5)

            return True

        except Exception as e:
            logger.error(f"❌ 無法選擇日期: {e}")
            return False

    def _select_time_slot(self, page) -> bool:
        """選擇用餐時段"""
        try:
            logger.info(f"尋找可用時段: {', '.join(self.times)}")

            # 檢查每個偏好時段
            for preferred_time in self.times:
                # 檢查該時段是否可用（不是"登記候補"）
                time_button = page.locator(f'text="{preferred_time}"').first

                # breakpoint()  # Debugging breakpoint
                if time_button.is_visible():
                    # 檢查是否包含"登記候補"文字
                    parent = time_button.locator("..").first
                    text_content = parent.text_content()

                    if "登記候補" not in text_content:
                        self._random_delay(0.3, 0.8)
                        time_button.click()
                        logger.info(f"✓ 已選擇時段: {preferred_time}")
                        self._random_delay(1.0, 2.0)
                        return True
                    else:
                        logger.warning(f"時段 {preferred_time} 需要登記候補，跳過")
                        self._random_delay(0.3, 0.6)

            logger.error("❌ 所有偏好時段都不可用")
            return False

        except Exception as e:
            logger.error(f"❌ 無法選擇時段: {e}")
            return False

    def _fill_booking_form(self, page) -> bool:
        """填寫預約表單"""
        try:
            logger.info("填寫預約資料...")

            # 點擊「完成預訂」或類似按鈕進入表單頁面
            self._random_delay(0.5, 1.0)
            page.click('text="完成預訂"', timeout=5000)
            self._random_delay(1.5, 2.5)

            # 填寫姓名
            self._random_delay(0.3, 0.7)
            page.locator("#name").fill(self.name)
            logger.info(f"✓ 已填寫姓名: {self.name}")
            self._random_delay(0.5, 1.0)

            # 填寫電話
            self._random_delay(0.3, 0.7)
            page.locator("#phone").fill(self.phone)
            logger.info(f"✓ 已填寫電話: {self.phone}")
            self._random_delay(0.5, 1.0)

            # 填寫 Email（如果有）
            self._random_delay(0.3, 0.7)
            page.locator("#email").fill(self.email)
            logger.info(f"✓ 已填寫 Email: {self.email}")

            self._random_delay(0.8, 1.5)
            return True

        except Exception as e:
            logger.error(f"❌ 填寫表單失敗: {e}")
            return False

    def _confirm_booking(self, page) -> bool:
        """確認並送出訂位"""
        try:
            logger.info("準備送出訂位...")

            # 尋找送出按鈕
            self._random_delay(0.8, 1.5)
            page.get_by_role("button", name="確認訂位").click()
            self._random_delay(2.0, 3.0)
            return True

        except Exception as e:
            logger.error(f"❌ 確認訂位失敗: {e}")
            return False


def main():
    config = BookingConfig(
        url=os.getenv("BOOKING_URL"),
        name=os.getenv("NAME"),
        phone=os.getenv("PHONE"),
        email=os.getenv("EMAIL"),
        party_size=int(os.getenv("PARTY_SIZE", "2")),
        times=os.getenv("TIMES").split(","),
        date=os.getenv("DATE"),  # None = 當日
        headless=os.getenv("HEADLESS", "false").lower() == "true",
    )

    # 創建並執行機器人
    bot = InlineBookingBot(config)
    success = bot.run()

    if success:
        logger.info("🎉 訂位流程完成！")
    else:
        logger.error("💔 訂位失敗，請檢查日誌或截圖")


if __name__ == "__main__":
    main()
