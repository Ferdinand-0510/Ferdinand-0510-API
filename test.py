def convert_market_data_to_react(raw_data):
    """將原始市集數據轉換為 React 組件代碼"""
    regions = raw_data.split('📌')[1:]  # 去掉第一個空字符串
    
    # 生成基本組件結構
    react_code = '''import React, { useEffect, useRef } from 'react';
import './MarketEvent.css'

function MarketEvent() {
    const sectionRefs = useRef([]);
    
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            },
            {
                threshold: 0.1,
                rootMargin: '50px'
            }
        );

        const sections = document.querySelectorAll('.market-section');
        sections.forEach((section) => {
            observer.observe(section);
        });

        return () => {
            sections.forEach((section) => {
                observer.unobserve(section);
            });
        };
    }, []);

    return (
        <div>
            <div className='market-title'> 
                <img src="/images/marketTitle1.png" alt="Title Image" className="market-Titleimg" />
                <h1>市集內容</h1>
            </div>

            <div className='market-container1'>
                <img src="/images/1206.jpg" alt="Title Image" className="market-img" />
                <div className='market-context'>
'''

    # 處理每個區域
    for region in regions:
        lines = region.strip().split('\n')
        region_name = lines[0].strip()
        
        # 添加區域標題
        react_code += f'''                    <div className="market-section">
                        <h2>📌{region_name}📌</h2>
                    </div>

                    <div className="market-section">
'''
        
        # 處理市集項目
        current_market = []
        current_url = ""
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('網址:'):
                if line != '網址:':
                    current_url = line.replace('網址:', '').strip()
            elif line.startswith('🏝️'):
                if current_market:
                    react_code += generate_market_item(current_market, current_url)
                current_market = [line]
                current_url = ""
            elif line:
                current_market.append(line)
        
        # 處理最後一個市集
        if current_market:
            react_code += generate_market_item(current_market, current_url)
        
        react_code += '                    </div>\n\n'

    # 添加組件結尾
    react_code += '''                </div>
                <div className='market-space'></div>
            </div>
            
            <div className='market-title'> 
                <img src="/images/marketbow.png" alt="Title Image" className="market-Titleimg" />
            </div>
        </div>
    )
}

export default MarketEvent;'''

    return react_code

def generate_market_item(market_data, url):
    """生成單個市集項目的 JSX 代碼"""
    jsx = '''                        <div className="market-item">
                            <a href="{}" target="_blank" rel="noopener noreferrer">{}</a><br/>\n'''.format(
        url or "#",
        market_data[0]
    )
    
    # 添加其他詳細信息
    for detail in market_data[1:]:
        jsx += f'                            {detail}<br/>\n'
    
    jsx += '                        </div>\n\n'
    return jsx

# 使用示例
raw_data = """📌雙北📌
網址:
🏝️ 信義地球村 - 耶誕微光
📅 𝟭𝟮/𝟭𝟯㊄ ➜ 𝟭𝟮/𝟭𝟱㊐ 𝟭𝟯:𝟬𝟬-𝟮𝟭:𝟬𝟬
📍信義香堤大道𝗔𝟴-𝗔𝟭𝟬間
網址:https://www.facebook.com/story.php/?story_fbid=561496489971291&id=100083328333173&_rdr

🏝️ ◤2024 北流耶誕小鎮◢
📅  12/14 ㊅ - 12/15 ㊐
📍臺北流行音樂中心
網址:https://www.tmc.taipei/tw/lastest-event/323D0fcBb23F
#活動免費入場

🏝️ 淡水捷運2號出口廣場
📅 12/13~15（五六日）
📍淡水捷運站2號出口(8號廣場)
網址:https://www.twmarket.tw/?p=51110

🏝️ 牌卡協會年會市集
📅 12/14（六）13:00-17:00
📍臺北市許昌街42號8樓
網址:https://www.twmarket.tw/?p=50284

🏝️ 冬季的祝福 聖誕市集-天母SOGO
📅 12/14(六)12/15(日) 11:00~19:30
📍台北市士林區中山北路六段77號 中山北大門
網址:https://www.twmarket.tw/?p=51090

🏝️ 小精靈聖誔村 安森町市集
📅 12/14(六)12/15(日)11:00-18:00
📍大安森林公園捷運站-陽光大廳+下凹庭園
網址:https://www.twmarket.tw/?p=50986

🏝️ 花博聖誕祝福市集
📅 12.14(週六）-12.15(週日）11:00-19:00
📍花博公園花海廣場
網址:https://www.twmarket.tw/?p=50901

📌新竹📌
網址:
🏝️ 欣慰到興食集
📅 12.14-15 10:00 – 18:00
📍中興文創園區 光合屋＆戲棚下
網址:https://chccp.e-land.gov.tw/%E6%96%B0%E5%91%B3%E9%81%93%E8%88%88%E9%A3%9F%E9%9B%86-%E9%96%8B%E5%B8%82%E5%9B%89/

📌桃園📌
網址:
🏝️ 十二籃X夏都行館繽紛星空社區市集
📅 12/13(五)12/14(六)
12/13(五)15：00-21：00
12/14(六)11：00-20：00
📍夏都行館-百福街口
網址:https://www.twmarket.tw/?p=51252

🏝️ 聖誕好咖市集
📅 12月14日(六)11:00-16:00
📍中壢區大崙農會前空地 & 2樓主會場
網址:https://www.twmarket.tw/?p=51292

🏝️ 桃園總圖
📅 12/14~15 13:00-20:00
📍桃園市圖書館總館-桃知道文創生活廣場
網址:https://www.twmarket.tw/?p=51112

🏝️ 療癒市集【聖誕暖心聚】-2檔
📅 12/14㊅—12/15㊐ ❚ 11:00~18:00
📍桃園77藝文町 草地旁平台與草地區域
網址:https://www.twmarket.tw/?p=51431

📌台中📌
網址:
🏝️ 聯悅建設×小椿日和市集
📅 12/14-12/15
📍台中市梧棲區大仁路二段四維路口
網址:https://www.facebook.com/chunhemarket/photos/%E8%81%AF%E6%82%85%E5%BB%BA%E8%A8%AD%E5%B0%8F%E6%A4%BF%E6%97%A5%E5%92%8C%E5%AE%98%E6%96%B9%E8%A6%96%E8%A6%BA%E4%BE%86%E5%9B%89%E8%81%AF%E6%82%85fun%E8%81%96%E8%AA%95%E7%8F%BE%E5%A0%B4%E6%9C%89%E5%90%84%E5%BC%8F%E6%96%87%E5%89%B5%E5%A5%BD%E7%89%A9%E5%8F%8A%E8%B3%AA%E6%84%9F%E8%BC%95%E9%A3%9F%E6%89%8B%E4%BD%9C%E6%B4%BB%E5%8B%95%E9%82%84%E6%9C%89%E8%B6%85%E7%BE%8E%E7%A9%BA%E9%96%93%E4%BD%88%E7%BD%AE%E5%8F%8A%E6%82%A0%E9%96%92%E6%88%B6%E5%A4%96%E8%8D%89%E7%9A%AE%E7%AD%89%E4%BD%A0%E5%80%91%E4%BE%86%E7%8E%A9%E4%BE%86%E6%94%BE%E9%AC%86%E4%BE%86%E6%89%93%E5%8D%A1%E6%8B%8D%E7%BE%8E%E7%85%A7%E5%8F%A6%E6%9C%89%E5%AE%A2%E6%88%B6%E9%99%90%E5%AE%9A300%E5%85%83%E5%B8%82%E9%9B%86/574475638499167/?_rdr

🏝️ 甜點派對市集 x 甜蜜滿額贈
📅 12/14、15 13:00 ~ 19:00
📍大里藝術廣場
網址:https://wonder-newland.daliartplaza.com.tw/daliart/news

🏝️ 飛爾市集 × 141巷舊「市」浪慢
📅 11/9 (六) – 11/10 (日) 12:00 – 18:00
📍台中市中區台灣大道一段141巷
網址:https://www.twmarket.tw/?p=51068

📌嘉義📌
網址:
🏝️ 木頭人市集 Wood Market
📅 12/14 ㊅ - 12/15 ㊐
📍山樣子美食基地
網址:https://www.instagram.com/wood201907/

🏝️ 朴子魅力商圈x朴通市集 
📅  12/14 ㊅ - 12/15 ㊐ 11:00~18:00
📍嘉藝點水道頭文創聚落
網址:https://www.facebook.com/Chiayishueidautou/?locale=zh_TW

📌台南📌
網址:
🏝️ 台南神農街
📅 12/14(六)、12/15(日)
📍台南市神農街134號
網址:https://www.facebook.com/photo/?fbid=9165757750110078&set=gm.3948886335356489&idorvanity=2879209795657487

🏝️ 台南國華街商圈
📅 12/14－12/15 12:00－19:00
📍台南國華街淺草地下廣場
網址:https://www.facebook.com/share/p/15L4Jq4nvk/

🏝️ ˗ˏˋ ★叮叮噹｜2024星夜聖誕市集派對 ★ ˎˊ˗
📅 12/14(六) 15:00-21:00
12/15(日) 12:00-18:00
📍台南市善化區成功路252號
網址:https://www.facebook.com/story.php/?story_fbid=1133561918775514&id=100063651505224&_rdr

🏝️ 他人視角 視角嘉年華
📅 12/14-2024/12/15 14:00-20:00
📍台南新光三越中山店
網址:https://www.twmarket.tw/?p=51191

📌高雄📌
網址:
🏝️ SANPOOO 三波轉運站 X TOY COMBOOO
📅 12/14（六）-12/15（日）14:00-20:00 
📍駁二藝術特區｜大義區紅磚廊道
 網址:https://pier2.org/activity/info/1484/

🏝️ 駁二大勇倉庫-動漫祭
📅 𝟙𝟚.𝟙𝟜-𝟙𝟝 時間看IG
📍駁二大勇倉庫
網址:https://www.instagram.com/w.do.market/

🏝️ 🍭2024衛武營聖誕奇境
📅 12/14(六)－12/15(日) 15:00-20:00
📍衛武營國家藝術文化中心
網址:https://www.facebook.com/share/p/14eq64ejHx/

🏝️ ❰感謝岡好有你❱ 聖誕市集⨯愛心派對
📅 12/14(六)－12/15(日)13：00－20：00
📍高雄市岡山區柳橋西路1號
網址:https://www.twmarket.tw/?p=51442

🏝️ 慶餘黏樂黏黏
📅 12/14㊅-12/15㊐ 
📍大統百貨
網址:https://www.twmarket.tw/?p=51238

🏝️ 浪愛集食
📅 12/14㊅-12/15㊐ 14:00-20:00
📍大統百貨 (高雄市新興區五福二路262號)
網址:https://www.twmarket.tw/?p=51521

🏝️ 耶誕時光市集
📅 𝟏𝟮/𝟏𝟒(六）- 𝟏𝟮/𝟏𝟓(日）𝟏𝟒:𝟬𝟬–𝟮𝟏:𝟬𝟬
📍 瘋潮廣場  不會日曬的市集
網址:https://www.twmarket.tw/?p=50944

"""  # 您的完整市集數據

# 生成 React 組件代碼
react_component = convert_market_data_to_react(raw_data)

# 將生成的代碼保存到文件
with open('MarketEvent.txt', 'w', encoding='utf-8') as f:
    f.write(react_component)