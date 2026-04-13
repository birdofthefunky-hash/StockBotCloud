import discord
from discord.ext import commands, tasks
import yfinance as yf
import pandas as pd
import json
import asyncio
import aiohttp
from datetime import datetime, time
import pytz

# ======================
# CONFIG — FILL THESE IN
# ======================
import os
TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = 1491926390352777289
FINNHUB_API_KEY = os.environ.get("FINNHUB_KEY")

# ======================
# DISCORD SETUP
# ======================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ET = pytz.timezone("America/New_York")
CT = pytz.timezone("America/Chicago")

# ======================
# VERIFIED RUSSELL 1000 TICKERS
# Source: User-provided official list, 978 tickers
# ======================
RUSSELL_1000 = [
    "A","AA","AAL","AAON","AAPL","ABBV","ABNB","ABT","ACGL","ACHC","ACI","ACM",
    "ACN","ADBE","ADC","ADI","ADM","ADP","ADSK","ADT","AEE","AEP","AES","AFG",
    "AFL","AFRM","AGCO","AGNC","AGO","AIG","AIT","AIZ","AJG","AKAM","AL","ALAB",
    "ALB","ALGM","ALGN","ALK","ALL","ALLE","ALLY","ALNY","ALSN","AM","AMAT","AMCR",
    "AMD","AME","AMG","AMGN","AMH","AMKR","AMP","AMT","AMTM","AMZN","AN","ANET",
    "AON","AOS","APA","APD","APG","APH","APLS","APO","APP","APPF","APTV","AR",
    "ARE","ARES","ARMK","ARW","AS","ASH","ASTS","ATI","ATO","ATR","AU","AUR",
    "AVB","AVGO","AVT","AVTR","AVY","AWI","AWK","AXON","AXP","AXS","AXTA","AYI",
    "AZO","BA","BAC","BAH","BALL","BAM","BAX","BBWI","BBY","BC","BDX","BEN",
    "BEPC","BF-A","BF-B","BFAM","BG","BHF","BIIB","BILL","BIO","BIRK","BJ","BK",
    "BKNG","BKR","BLD","BLDR","BLK","BLSH","BMRN","BMY","BOKF","BPOP","BR","BRBR",
    "BRK-B","BRKR","BRO","BROS","BRX","BSX","BSY","BURL","BWA","BWXT","BX","BXP",
    "BYD","C","CACC","CACI","CAG","CAH","CAI","CAR","CARR","CART","CASY","CAT",
    "CAVA","CB","CBC","CBOE","CBRE","CBSH","CCC","CCI","CCK","CCL","CDNS","CDW",
    "CE","CEG","CELH","CERT","CF","CFG","CFR","CG","CGNX","CHD","CHDN","CHE",
    "CHH","CHRD","CHRW","CHTR","CHWY","CI","CIEN","CINF","CL","CLF","CLH","CLVT",
    "CLX","CMCSA","CME","CMG","CMI","CMS","CNA","CNC","CNH","CNM","CNP","CNXC",
    "COF","COHR","COIN","COKE","COLB","COLD","COLM","COO","COP","COR","CORT","COST",
    "COTY","CPAY","CPB","CPNG","CPRT","CPT","CR","CRCL","CRH","CRL","CRM","CROX",
    "CRS","CRUS","CRWD","CSCO","CSGP","CSL","CSX","CTAS","CTRA","CTSH","CTVA","CUBE",
    "CUZ","CVNA","CVS","CVX","CW","CWEN","CXT","CZR","D","DAL","DAR","DASH",
    "DBX","DCI","DD","DDOG","DDS","DE","DECK","DELL","DG","DGX","DHI","DHR",
    "DINO","DIS","DJT","DKNG","DKS","DLB","DLR","DLTR","DOC","DOCS","DOCU","DOV",
    "DOW","DOX","DPZ","DRI","DRS","DT","DTE","DTM","DUK","DUOL","DV","DVA",
    "DVN","DXC","DXCM","EA","EBAY","ECL","ED","EEFT","EFX","EG","EGP","EHC",
    "EIX","EL","ELAN","ELF","ELS","ELV","EME","EMN","EMR","ENPH","ENTG","EOG",
    "EPAM","EPR","EQH","EQIX","EQR","EQT","ES","ESAB","ESI","ESS","ESTC","ETN",
    "ETR","ETSY","EVR","EVRG","EW","EWBC","EXC","EXE","EXEL","EXLS","EXP","EXPD",
    "EXPE","EXR","F","FAF","FANG","FAST","FBIN","FCN","FCNCA","FCX","FDS","FDX",
    "FE","FERG","FFIV","FHB","FHN","FICO","FIGR","FIS","FISV","FITB","FIVE","FIX",
    "FLEX","FLO","FLS","FLUT","FMC","FNB","FND","FNF","FOUR","FOX","FOXA","FR",
    "FRHC","FRPT","FRT","FSLR","FTAI","FTI","FTNT","FTV","FWONA","FWONK","G","GAP",
    "GD","GDDY","GE","GEHC","GEN","GEV","GFS","GGG","GILD","GIS","GL","GLIBA",
    "GLIBK","GLOB","GLPI","GLW","GM","GME","GMED","GNRC","GNTX","GOOG","GOOGL","GPC",
    "GPK","GPN","GRMN","GS","GTES","GTLB","GTM","GWRE","GWW","GXO","H","HAL",
    "HALO","HAS","HAYW","HBAN","HCA","HD","HEI","HHH","HIG","HII","HIW","HLI",
    "HLNE","HLT","HOG","HOLX","HON","HOOD","HPE","HPQ","HR","HRB","HRL","HSIC",
    "HST","HSY","HUBB","HUBS","HUM","HUN","HWM","HXL","IAC","IBKR","IBM","ICE",
    "IDA","IDXX","IEX","IFF","ILMN","INCY","INGM","INGR","INSM","INSP","INTC","INTU",
    "INVH","IONS","IOT","IP","IPGP","IQV","IR","IRDM","IRM","ISRG","IT","ITT",
    "ITW","IVZ","J","JAZZ","JBHT","JBL","JCI","JEF","JHG","JHX","JKHY","JLL",
    "JNJ","JPM","KBR","KD","KDP","KEX","KEY","KEYS","KHC","KIM","KKR","KLAC",
    "KMB","KMI","KMPR","KMX","KNSL","KNX","KO","KR","KRC","KRMN","KVUE","L",
    "LAD","LAMR","LAZ","LBRDA","LBRDK","LBTYA","LBTYK","LCID","LDOS","LEA","LECO","LEN",
    "LFUS","LH","LHX","LII","LIN","LINE","LITE","LKQ","LLY","LMT","LNC","LNG",
    "LNT","LOAR","LOPE","LOW","LPLA","LPX","LRCX","LSCC","LSTR","LULU","LUV","LVS",
    "LW","LYB","LYFT","LYV","M","MA","MAA","MAN","MANH","MAR","MAS","MASI",
    "MAT","MCD","MCHP","MCK","MCO","MDB","MDLZ","MDT","MDU","MEDP","MET","META",
    "MGM","MHK","MIDD","MKC","MKL","MKSI","MKTX","MLI","MLM","MMM","MNST","MO",
    "MOH","MORN","MOS","MP","MPC","MPT","MPWR","MRK","MRNA","MRP","MRSH","MRVL",
    "MS","MSA","MSCI","MSFT","MSI","MSM","MSTR","MTB","MTCH","MTD","MTDR","MTG",
    "MTN","MTSI","MTZ","MU","MUSA","NBIX","NCLH","NCNO","NDAQ","NDSN","NEE","NEM",
    "NET","NEU","NFG","NFLX","NI","NKE","NLY","NNN","NOC","NOV","NOW","NRG",
    "NSA","NSC","NTAP","NTNX","NTRA","NTRS","NU","NUE","NVDA","NVR","NVST","NVT",
    "NWL","NWS","NWSA","NXST","NYT","O","OC","ODFL","OGE","OGN","OHI","OKE",
    "OKTA","OLED","OLLI","OLN","OMC","OMF","ON","ONON","ONTO","ORCL","ORI","ORLY",
    "OSK","OTIS","OVV","OWL","OXY","OZK","PAG","PANW","PATH","PAYC","PAYX","PB",
    "PCAR","PCG","PCOR","PCTY","PEG","PEGA","PEN","PENN","PEP","PFE","PFG","PFGC",
    "PG","PGR","PH","PHM","PINS","PK","PKG","PLD","PLNT","PLTR","PM","PNC",
    "PNFP","PNR","PNW","PODD","POOL","POST","PPC","PPG","PPL","PR","PRGO","PRI",
    "PRMB","PRU","PSA","PSN","PSTG","PSX","PTC","PVH","PWR","PYPL","QCOM","QGEN",
    "QRVO","QSR","R","RBLX","RBRK","RCL","RDDT","REG","REGN","REXR","REYN","RF",
    "RGA","RGEN","RGLD","RH","RHI","RITM","RIVN","RJF","RKLB","RKT","RL","RLI",
    "RMD","RNG","RNR","ROIV","ROK","ROKU","ROL","ROP","ROST","RPM","RPRX","RRC",
    "RRX","RS","RSG","RTX","RVMD","RVTY","RYAN","RYN","S","SAIA","SAIC","SAIL",
    "SAM","SARO","SBAC","SBUX","SCCO","SCHW","SCI","SEE","SEIC","SF","SFD","SFM",
    "SHC","SHW","SIRI","SITE","SJM","SLB","SLGN","SLM","SMCI","SMG","SMMT","SN",
    "SNA","SNDK","SNOW","SNPS","SNX","SO","SOFI","SOLV","SON","SPG","SPGI","SPOT",
    "SRE","SRPT","SSB","SSD","SSNC","ST","STAG","STE","STLD","STT","STWD","STZ",
    "SUI","SW","SWK","SWKS","SYF","SYK","SYY","T","TAP","TDC","TDG","TDY",
    "TEAM","TECH","TEM","TER","TFC","TFX","TGT","THC","THG","THO","TJX","TKO",
    "TKR","TLN","TMO","TMUS","TNL","TOL","TOST","TPG","TPL","TPR","TREX","TRGP",
    "TRMB","TROW","TRU","TRV","TSCO","TSLA","TSN","TT","TTC","TTD","TTEK","TTWO",
    "TW","TWLO","TXN","TXRH","TXT","TYL","U","UA","UAA","UAL","UBER","UDR",
    "UGI","UHS","UI","ULTA","UNH","UNM","UNP","UPS","URI","USB","USFD","UTHR",
    "UWMC","V","VEEV","VFC","VICI","VIK","VIRT","VKTX","VLO","VLTO","VMC","VMI",
    "VNO","VNOM","VNT","VOYA","VRSK","VRSN","VRT","VRTX","VST","VTR","VTRS","VVV",
    "VZ","W","WAB","WAL","WAT","WBD","WBS","WCC","WDAY","WDC","WEC","WELL",
    "WEN","WEX","WFC","WFRD","WH","WHR","WING","WLK","WM","WMB","WMT","WPC",
    "WRB","WSC","WSM","WSO","WST","WTFC","WTM","WTRG","WTW","WU","WWD","WY",
    "WYNN","XEL","XOM","XP","XPO","XRAY","XYL","XYZ","YETI","YUM","Z","ZBH",
    "ZBRA","ZG","ZION","ZM","ZS","ZTS",
]

def get_universe():
    seen = set()
    unique = []
    for t in RUSSELL_1000:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique

# ======================
# PORTFOLIO STORAGE
# ======================
def load_portfolio():
    try:
        with open("portfolio.json", "r") as f:
            raw = json.load(f)
            cleaned = {}
            for ticker, price in raw.items():
                if isinstance(price, dict):
                    for v in price.values():
                        try:
                            cleaned[ticker] = float(v)
                            break
                        except (TypeError, ValueError):
                            pass
                else:
                    try:
                        cleaned[ticker] = float(price)
                    except (TypeError, ValueError):
                        pass
            return cleaned
    except:
        return {}

def save_portfolio(data):
    with open("portfolio.json", "w") as f:
        json.dump(data, f, indent=4)

# ======================
# SAFE PRICE FETCH
# ======================
def get_current_price(ticker: str):
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if hist.empty:
            return None
        price = hist["Close"].iloc[-1]
        if hasattr(price, "item"):
            return float(price.item())
        return float(price)
    except:
        return None

# ======================
# ENTRY SIGNAL SCORING
# ======================

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))

def score_ticker_technical(ticker: str):
    """
    Scores a single ticker independently.
    Uses threads=False to prevent yfinance data cross-contamination.
    Filters out penny stocks (under $5).
    """
    try:
        df = yf.download(
            ticker,
            period="30d",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if df.empty or len(df) < 15:
            return None

        close = df["Close"]
        volume = df["Volume"]

        # Squeeze to 1D Series in case yfinance returns a DataFrame column
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()
        if isinstance(volume, pd.DataFrame):
            volume = volume.squeeze()

        if not isinstance(close, pd.Series) or not isinstance(volume, pd.Series):
            return None

        close = close.dropna()
        volume = volume.dropna()

        if len(close) < 15:
            return None

        current_price = float(close.iloc[-1])

        # Skip penny stocks
        if current_price < 5.0:
            return None

        # --- INTRADAY SURGE CHECK ---
        # If a stock already surged 10%+ today, the easy move is likely over — skip it.
        intraday_surge = 0.0
        try:
            open_col = df["Open"]
            if isinstance(open_col, pd.DataFrame):
                open_col = open_col.squeeze()
            today_open = float(open_col.dropna().iloc[-1])
            if today_open > 0:
                intraday_surge = (current_price - today_open) / today_open * 100
        except Exception:
            intraday_surge = 0.0

        if intraday_surge > 10.0:
            return None  # already too extended today

        # Penalty for stocks up 5-10% today (reduce score, don't skip)
        surge_penalty = 0.6 if intraday_surge > 5.0 else 1.0

        # RSI — reward oversold/recovering, penalize overbought
        rsi_series = compute_rsi(close)
        rsi = float(rsi_series.iloc[-1])
        if pd.isna(rsi):
            return None

        if rsi < 30:
            rsi_score = 90    # deeply oversold = strong entry signal
        elif rsi < 45:
            rsi_score = 75    # oversold recovery zone — ideal entry
        elif rsi < 55:
            rsi_score = 50    # neutral
        elif rsi < 65:
            rsi_score = 30    # slightly overbought
        else:
            rsi_score = max(0, 100 - rsi)  # overbought = penalized

        # Volume spike vs 20-day average
        avg_vol = float(volume.iloc[:-1].mean())
        today_vol = float(volume.iloc[-1])
        vol_ratio = (today_vol / avg_vol) if avg_vol > 0 else 1.0
        vol_score = min(100, max(0, (vol_ratio - 1.0) * 50))

        # Breakout position — reward stocks APPROACHING their high, not already past it
        recent_high = float(close.iloc[-20:].max())
        pct_of_high = current_price / recent_high if recent_high > 0 else 0
        if pct_of_high >= 0.99:
            breakout_score = 70    # at the high — may be extended
            is_breakout = True
        elif pct_of_high >= 0.97:
            breakout_score = 90    # approaching high — best entry zone
            is_breakout = True
        elif pct_of_high >= 0.93:
            breakout_score = 60
            is_breakout = False
        elif pct_of_high >= 0.88:
            breakout_score = 30
            is_breakout = False
        else:
            breakout_score = 0
            is_breakout = False

        # 3-day momentum — reward moderate gains, penalize extreme moves
        if len(close) >= 4:
            mom = (float(close.iloc[-1]) - float(close.iloc[-4])) / float(close.iloc[-4]) * 100
        else:
            mom = 0.0

        if 1.0 <= mom <= 8.0:
            momentum_score = min(100, mom * 12)   # sweet spot
        elif mom > 8.0:
            momentum_score = max(20, 100 - (mom - 8.0) * 8)  # penalize overextension
        else:
            momentum_score = min(50, max(-50, mom * 5))

        # Weighted total — RSI and volume carry more weight now
        raw_total = (
            rsi_score      * 0.35 +
            vol_score      * 0.30 +
            breakout_score * 0.20 +
            momentum_score * 0.15
        )
        total = raw_total * surge_penalty

        return {
            "ticker": ticker,
            "price": round(current_price, 2),
            "rsi": round(rsi, 1),
            "vol_ratio": round(vol_ratio, 2),
            "breakout": is_breakout,
            "momentum_3d": round(mom, 2),
            "score": round(total, 2),
            "sentiment": 0,
            "final_score": round(total, 2),
        }

    except Exception:
        return None

async def get_news_sentiment(ticker: str, session: aiohttp.ClientSession):
    try:
        url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_API_KEY}"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            if resp.status != 200:
                return 0
            data = await resp.json()
            sentiment = data.get("sentiment", {})
            bull = sentiment.get("bullishPercent", 0.5)
            score = (bull - 0.5) * 200
            buzz = data.get("buzz", {})
            article_count = buzz.get("articlesInLastWeek", 0)
            buzz_boost = min(20, article_count * 2)
            return round(score + buzz_boost, 2)
    except:
        return 0

async def scan_and_score():
    """
    Scans tickers one at a time with a small delay between each to prevent
    yfinance from returning shared/cached data across tickers.
    Final dedup pass removes any results with identical prices.
    """
    universe = get_universe()
    results = []
    seen_tickers = set()

    loop = asyncio.get_event_loop()

    async with aiohttp.ClientSession() as session:
        for ticker in universe:
            if ticker in seen_tickers:
                continue

            await asyncio.sleep(0.05)

            result = await loop.run_in_executor(None, score_ticker_technical, ticker)

            if result is None:
                continue

            seen_tickers.add(ticker)

            if result["score"] > 20:
                sentiment = await get_news_sentiment(ticker, session)
                result["sentiment"] = sentiment
                result["final_score"] = round(result["score"] * 0.75 + sentiment * 0.25, 2)
                results.append(result)

    results.sort(key=lambda x: x["final_score"], reverse=True)

    # Dedup by price as a safety net against data bleed
    seen_prices = set()
    deduped = []
    for r in results:
        if r["price"] not in seen_prices:
            seen_prices.add(r["price"])
            deduped.append(r)
        if len(deduped) == 5:
            break

    return deduped

# ======================
# TIME HELPERS
# ======================
def is_weekday():
    return datetime.now(ET).weekday() < 5  # Mon=0 through Fri=4, Sat=5 Sun=6

def market_open():
    now = datetime.now(ET)
    return is_weekday() and time(9, 30) <= now.time() <= time(16, 0)

def signal_window():
    now = datetime.now(ET)
    return is_weekday() and time(8, 30) <= now.time() <= time(14, 30)

# ======================
# BACKGROUND TASKS
# ======================

@tasks.loop(minutes=1)
async def hourly_signal_task():
    if not signal_window():
        return
    now = datetime.now(ET)
    if now.minute not in (0, 30):
        return
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return
    await channel.send("🔍 **Scanning Russell 1000 for top entry signals... this may take a few minutes.**")
    await post_top5(channel)

@tasks.loop(minutes=5)
async def gain_alert_task():
    if not market_open():
        return
    data = load_portfolio()
    if not data:
        return
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return
    for ticker, buy_price in data.items():
        current = get_current_price(ticker)
        if current is None:
            continue
        change = ((current - buy_price) / buy_price) * 100
        if change >= 5.0:
            await channel.send(
                f"🚨 **SELL ALERT — {ticker}** 🚨\n"
                f"Bought at `${buy_price:.2f}`, now at `${current:.2f}` — **+{change:.2f}%**\n"
                f"📊 Consider selling to lock in your gains!"
            )

async def post_top5(channel):
    try:
        top5 = await scan_and_score()
    except Exception as e:
        await channel.send(f"❌ Scan failed: {e}")
        return

    if not top5:
        await channel.send("⚠️ No strong signals found right now.")
        return

    time_str = datetime.now(CT).strftime("%I:%M %p CT")
    lines = [f"📈 **TOP 5 BUY SIGNALS — {time_str}**\n"]

    for i, s in enumerate(top5, 1):
        breakout_tag = " 🚀 *BREAKOUT*" if s.get("breakout") else ""
        sent = s.get("sentiment", 0)
        sentiment_tag = " 📰 *Positive news*" if sent > 20 else (" 📰 *Negative news*" if sent < -20 else "")
        lines.append(
            f"**#{i} {s['ticker']}** — Score: `{s['final_score']}`{breakout_tag}{sentiment_tag}\n"
            f"  💵 Price: `${s['price']:.2f}` | RSI: `{s['rsi']}` | "
            f"Volume: `{s['vol_ratio']}x avg` | 3-Day Momentum: `{s['momentum_3d']:+.2f}%`\n"
        )

    await channel.send("\n".join(lines))

# ======================
# BOT EVENTS
# ======================

@bot.event
async def on_ready():
    print(f"[INFO] Logged in as {bot.user}")
    print(f"[INFO] Russell 1000 loaded: {len(get_universe())} tickers.")
    hourly_signal_task.start()
    gain_alert_task.start()

# ======================
# COMMANDS
# ======================

@bot.command()
async def buy(ctx, ticker: str):
    ticker = ticker.upper()
    try:
        price = get_current_price(ticker)
        if price is None:
            await ctx.send(f"❌ Could not fetch price for **{ticker}**.")
            return
        data = load_portfolio()
        data[ticker] = price
        save_portfolio(data)
        await ctx.send(f"✅ Bought **{ticker}** at `${price:.2f}`")
    except Exception as e:
        await ctx.send(f"❌ Error buying {ticker}: {e}")

@bot.command()
async def sell(ctx, ticker: str):
    ticker = ticker.upper()
    data = load_portfolio()
    if ticker not in data:
        await ctx.send(f"❌ You don't own **{ticker}**.")
        return
    buy_price = data[ticker]
    current = get_current_price(ticker)
    if current is None:
        await ctx.send(f"❌ Could not fetch price for **{ticker}**.")
        return
    change = ((current - buy_price) / buy_price) * 100
    del data[ticker]
    save_portfolio(data)
    await ctx.send(
        f"💰 Sold **{ticker}**\n"
        f"Buy: `${buy_price:.2f}` → Sell: `${current:.2f}`\n"
        f"{'📈' if change >= 0 else '📉'} `{change:+.2f}%`"
    )

@bot.command()
async def check(ctx, ticker: str):
    ticker = ticker.upper()
    data = load_portfolio()
    if ticker not in data:
        await ctx.send("❌ You don't own this stock.")
        return
    buy_price = data[ticker]
    current = get_current_price(ticker)
    if current is None:
        await ctx.send(f"❌ Could not fetch price for **{ticker}**.")
        return
    change = ((current - buy_price) / buy_price) * 100
    if change > 5:
        advice = "🔥 SELL — up 5%+!"
    elif change < -3:
        advice = "⚠️ CUT LOSS"
    else:
        advice = "📊 HOLD"
    await ctx.send(
        f"**{ticker}**\n"
        f"Buy:    `${buy_price:.2f}`\n"
        f"Now:    `${current:.2f}`\n"
        f"Change: `{change:+.2f}%`\n"
        f"Advice: {advice}"
    )

@bot.command()
async def portfolio(ctx):
    data = load_portfolio()
    if not data:
        await ctx.send("📭 No stocks owned.")
        return
    lines = ["**📊 Your Portfolio**\n"]
    for ticker, buy_price in data.items():
        current = get_current_price(ticker)
        if current is not None:
            change = ((current - buy_price) / buy_price) * 100
            emoji = "📈" if change >= 0 else "📉"
            lines.append(f"{emoji} **{ticker}** — bought `${buy_price:.2f}` | now `${current:.2f}` (`{change:+.2f}%`)")
        else:
            lines.append(f"• **{ticker}** — bought `${buy_price:.2f}` | price unavailable")
    await ctx.send("\n".join(lines))

@bot.command()
async def analyze(ctx):
    """Manually trigger the top-5 entry signal scan right now."""
    if not is_weekday():
        await ctx.send("📅 Markets are closed on weekends — no signals to scan!")
        return
    await ctx.send("🔍 **Running scan of Russell 1000... this may take a few minutes.**")
    await post_top5(ctx.channel)

@bot.command()
async def cmds(ctx):
    await ctx.send(
        "**📋 Stock Bot — Full Command List**\n\n"
        "**📈 Trading Commands**\n"
        "`!buy TICKER` — Log a stock purchase at the current live price\n"
        "`!sell TICKER` — Log a sale and see your total gain or loss\n"
        "`!check TICKER` — Check a stock you own with a buy/hold/sell recommendation\n"
        "`!portfolio` — View all your holdings with live prices and P&L\n\n"
        "**🔍 Scan Commands**\n"
        "`!analyze` — Manually trigger the top-5 buy signal scan right now (weekdays only)\n\n"
        "**ℹ️ Info**\n"
        "`!cmds` — Show this command list\n"
        "`!help_stocks` — Same as !cmds\n\n"
        "**⏰ Automatic Alerts (no command needed)**\n"
        "• Top 5 buy signals posted every 30 min, 8:30am–2:30pm ET, weekdays only\n"
        "• 🚨 Sell alert posted if any holding hits +5% gain, checked every 5 min during market hours\n\n"
        "**📊 How Signals Are Scored**\n"
        "Each stock is scored on: RSI (oversold recovery), Volume spike, Breakout position, 3-day momentum, and News sentiment\n"
        "Stocks already up 10%+ today are automatically excluded — the bot looks for stocks *starting* to move, not ones that already ran."
    )

@bot.command()
async def help_stocks(ctx):
    await ctx.invoke(bot.get_command("cmds"))

# ======================
# RUN
# ======================
bot.run(TOKEN)