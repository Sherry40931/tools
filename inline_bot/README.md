# MyAnime Cafe 自動訂位機器人

使用 Playwright 自動化預約 inline.app 訂位系統。

## 功能特色

- ✅ 自動選擇用餐人數、日期、時段
- ✅ 自動填寫預約資料
- ✅ 支援多個偏好時段（依序嘗試）
- ✅ 詳細的執行日誌
- ✅ 失敗時自動截圖
- ✅ 可顯示瀏覽器或背景執行

## 安裝步驟

### 1. 安裝 uv（如果尚未安裝）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安裝依賴套件

```bash
uv sync
```

### 3. 安裝 Playwright 瀏覽器

```bash
uv run playwright install chromium
```

### 3. 配置設定

編輯 `inline-bot.py` 中的 `config` 字典，填入你的資料：

```python
config = {
    'url': 'https://inline.app/booking/...',
    'name': '王小明',  # ⚠️ 必須與證件相符
    'phone': '0912345678',
    'email': 'example@email.com',
    'party_size': 2,
    'preferred_times': ['14:30', '16:00', '17:50'],
    'target_date': None,  # None = 當日
    'headless': False,
}
```

## 使用方法

### 基本執行

```bash
uv run python inline-bot.py
```

### 參數說明

- **name**: 預約人姓名（必須與證件相符）
- **phone**: 聯絡電話
- **email**: 電子郵件（選填）
- **party_size**: 用餐人數 (1-4)
- **preferred_times**: 偏好時段列表，會依序嘗試
- **target_date**: 目標日期 (格式: YYYY-MM-DD)，None 表示當日
- **headless**: False 顯示瀏覽器，True 背景執行

## 注意事項

⚠️ **重要提醒**

1. **實名認證**: 必須填寫與證件相符的全名
2. **訂位限制**: 每組電話最多預約 2 場次，每次上限 4 人
3. **開放時間**: 僅開放未來七天（含當日）
4. **保留時間**: 每組訂位僅保留 10 分鐘
5. **入場證件**: 需出示有照片的證件（身分證、健保卡、護照、駕照）

## 常見問題

### Q: 如何知道訂位成功？

A: 機器人會在日誌中顯示 "✅ 訂位成功"，並且會暫停 3 秒讓你看到結果頁面。

### Q: 如果失敗會怎樣？

A: 會自動截圖並儲存為 `error_YYYYMMDD_HHMMSS.png`，方便除錯。

### Q: 可以定時自動執行嗎？

A: 可以，使用 cron (Linux/Mac) 或工作排程器 (Windows)，或在程式中加入 `schedule` 套件。

### Q: 如何偵測新放出的時段？

A: 可以設定 cron 在每日換日時（通常是凌晨）自動執行。

## 授權聲明

本工具僅供學習交流使用，請遵守餐廳訂位規範，不要濫用自動化工具。
