import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import akshare as ak
import numpy as np
import pandas as pd

logger = logging.getLogger("qtf_mcp")

stock_sector_data = os.environ.get("STOCK_TO_SECTOR_DATA", "confs/stock_sector.json")

STOCK_SECTOR: Dict[str, List[str]] | None = None


def get_stock_sector() -> Dict[str, List[str]]:
    global STOCK_SECTOR
    if STOCK_SECTOR is None:
        try:
            with open(stock_sector_data, "r", encoding="utf-8") as f:
                STOCK_SECTOR = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load stock sector data: {e}")
            STOCK_SECTOR = {}
    return STOCK_SECTOR if STOCK_SECTOR is not None else {}


def convert_symbol_format(symbol: str) -> str:
    """转换股票代码格式以适应akshare"""
    if symbol.startswith("SH"):
        return f"sh{symbol[2:]}"
    elif symbol.startswith("SZ"):
        return f"sz{symbol[2:]}"
    else:
        return symbol.lower()


def get_stock_type(symbol: str) -> str:
    """判断股票类型"""
    if symbol.startswith("SH6") or symbol.startswith("sz6"):
        return "stock"
    elif symbol.startswith("SZ00") or symbol.startswith("sz00"):
        return "stock"
    elif symbol.startswith("SZ30") or symbol.startswith("sz30"):
        return "stock"
    else:
        return "index"


async def load_data_akshare(
    symbol: str, start_date: str, end_date: str, n: int = 0, who: str = ""
) -> Dict[str, np.ndarray]:
    """使用akshare获取单个股票数据"""
    datas = await load_data_akshare_batch([symbol], start_date, end_date, n, who)
    return datas.get(symbol, {})


async def load_data_akshare_batch(
    symbols: List[str], start_date: str, end_date: str, n: int = 0, who: str = ""
) -> Dict[str, Dict[str, np.ndarray]]:
    """使用akshare批量获取股票数据"""
    t1 = time.time()
    datas = {}
    
    for symbol in symbols:
        try:
            symbol_data = fetch_single_stock_data(symbol, start_date, end_date)
            if symbol_data:
                datas[symbol] = symbol_data
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
    
    t2 = time.time()
    logger.info(f"{who} fetch data cost {t2 - t1} seconds, symbols: {','.join(symbols)}")
    return datas


def fetch_single_stock_data(symbol: str, start_date: str, end_date: str) -> Dict[str, np.ndarray]:
    """获取单个股票的完整数据"""
    symbol_data = {}
    
    # 获取K线数据
    kline_data = fetch_kline_data(symbol, start_date, end_date)
    if kline_data is None or kline_data.empty:
        return {}
    
    # 基础K线数据
    date_base = kline_data['date'].values.astype('datetime64[ns]').astype('int64') // 10**9
    symbol_data['DATE'] = date_base
    symbol_data['OPEN'] = kline_data['open'].values.astype('float64')
    symbol_data['HIGH'] = kline_data['high'].values.astype('float64')
    symbol_data['LOW'] = kline_data['low'].values.astype('float64')
    symbol_data['CLOSE'] = kline_data['close'].values.astype('float64')
    symbol_data['VOLUME'] = kline_data['volume'].values.astype('float64')
    symbol_data['AMOUNT'] = kline_data['amount'].values.astype('float64') if 'amount' in kline_data.columns else symbol_data['VOLUME'] * symbol_data['CLOSE']
    
    # 复权价格计算
    symbol_data['CLOSE2'] = symbol_data['CLOSE']
    symbol_data['PRICE'] = symbol_data['CLOSE']
    
    # 初始化分红数据
    symbol_data['GCASH'] = np.zeros_like(date_base, dtype=np.float64)
    symbol_data['GSHARE'] = np.zeros_like(date_base, dtype=np.float64)
    
    # 获取财务数据
    finance_data = fetch_finance_data(symbol)
    if finance_data:
        symbol_data.update(finance_data)
    
    # 获取资金流向数据
    fundflow_data = fetch_fundflow_data(symbol, start_date, end_date)
    if fundflow_data:
        symbol_data.update(fundflow_data)
    
    # 行业信息
    symbol_data['SECTOR'] = get_stock_sector().get(symbol, [])
    
    return symbol_data


def fetch_kline_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取K线数据"""
    try:
        stock_type = get_stock_type(symbol)
        ak_symbol = convert_symbol_format(symbol)
        
        if stock_type == "stock":
            # 获取股票历史数据
            if ak_symbol.startswith("sh"):
                df = ak.stock_zh_a_hist(symbol=ak_symbol[2:], period="daily", start_date=start_date.replace("-", ""), end_date=end_date.replace("-", ""), adjust="")
            else:
                df = ak.stock_zh_a_hist(symbol=ak_symbol[2:], period="daily", start_date=start_date.replace("-", ""), end_date=end_date.replace("-", ""), adjust="")
        else:
            # 获取指数数据
            if ak_symbol.startswith("sh"):
                df = ak.stock_zh_index_daily(symbol=f"sh{ak_symbol[2:]}")
            else:
                df = ak.stock_zh_index_daily(symbol=f"sz{ak_symbol[2:]}")
        
        if df is None or df.empty:
            return None
            
        # 重命名列以匹配原有格式
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        })
        
        # 转换日期格式
        df['date'] = pd.to_datetime(df['date'])
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
        df = df.sort_values('date')
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch kline data for {symbol}: {e}")
        return None


def fetch_minute_data(symbol: str, start_datetime: str, end_datetime: str, period: str = "1") -> pd.DataFrame:
    """获取分钟级数据
    
    Args:
        symbol (str): 股票代码，格式如 "SH000001" 或 "SZ000001"
        start_datetime (str): 开始时间，格式如 "2023-12-11 09:30:00"
        end_datetime (str): 结束时间，格式如 "2023-12-11 15:00:00"
        period (str): 时间间隔，支持 "1", "5", "15", "30", "60" 分钟
    
    Returns:
        pd.DataFrame: 分钟级数据，包含时间、开盘、收盘、最高、最低、成交量等字段
    """
    try:
        stock_type = get_stock_type(symbol)
        ak_symbol = convert_symbol_format(symbol)
        
        logger.info(f"Fetching minute data for {symbol}, type: {stock_type}, ak_symbol: {ak_symbol}")
        
        df = None
        if stock_type == "stock":
            # 获取股票分钟级数据
            try:
                # 首先尝试指定日期范围
                df = ak.stock_zh_a_hist_min_em(
                    symbol=ak_symbol[2:],  # 去掉sh/sz前缀
                    period=period,
                    start_date=start_datetime,
                    end_date=end_datetime,
                )
                logger.info(f"Stock minute data API returned: {type(df)}, shape: {df.shape if df is not None else 'None'}")
                
                # 如果指定日期范围返回空数据，尝试获取默认最新数据
                if df is not None and df.empty:
                    logger.warning(f"No data for specified date range, trying default data for {symbol}")
                    df = ak.stock_zh_a_hist_min_em(
                        symbol=ak_symbol[2:],
                        period=period,
                    )
                    logger.info(f"Stock minute data (default) API returned: {type(df)}, shape: {df.shape if df is not None else 'None'}")
            except Exception as stock_e:
                logger.error(f"Stock minute data API failed: {stock_e}")
                return None
        else:
            # 获取指数分钟级数据
            try:
                # 对于指数，使用不带前缀的代码，如"000001"
                index_code = ak_symbol[2:] if len(ak_symbol) > 2 else ak_symbol
                # 首先尝试指定日期范围
                df = ak.index_zh_a_hist_min_em(
                    symbol=index_code,  # 使用不带前缀的代码如"000001"
                    period=period,
                    start_date=start_datetime,
                    end_date=end_datetime
                )
                logger.info(f"Index minute data API returned: {type(df)}, shape: {df.shape if df is not None else 'None'}")
                
                # 如果指定日期范围返回空数据，尝试获取默认最新数据
                if df is not None and df.empty:
                    logger.warning(f"No data for specified date range, trying default data for {symbol}")
                    df = ak.index_zh_a_hist_min_em(
                        symbol=index_code,
                        period=period
                    )
                    logger.info(f"Index minute data (default) API returned: {type(df)}, shape: {df.shape if df is not None else 'None'}")
            except Exception as index_e:
                logger.error(f"Index minute data API failed: {index_e}")
                return None
        
        if df is None:
            logger.warning(f"No data returned from akshare API for {symbol}")
            return None
            
        if df.empty:
            logger.warning(f"Empty dataframe returned for {symbol}")
            return None
            
        logger.info(f"Original columns: {list(df.columns)}")
        
        # 重命名列以匹配原有格式
        column_mapping = {
            '时间': 'datetime',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        
        # 只重命名存在的列
        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_mapping)
        
        # 转换时间格式
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime')
        
        logger.info(f"Successfully processed {len(df)} rows of minute data for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch minute data for {symbol}: {e}")
        return None


def fetch_finance_data(symbol: str) -> Dict[str, np.ndarray]:
    """获取财务数据"""
    try:
        ak_symbol = convert_symbol_format(symbol)
        stock_code = ak_symbol[2:]
        
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if stock_info is None or stock_info.empty:
            return {}
        
        # 获取最新财务数据
        finance_df = ak.stock_financial_abstract(symbol=stock_code)
        if finance_df is None or finance_df.empty:
            return {}
        
        # 提取关键财务指标
        result = {}
        
        # 总市值 (转换为万元)
        try:
            total_market_value = stock_info[stock_info['item'] == '总市值']['value'].values[0]
            if isinstance(total_market_value, str):
                total_market_value = float(total_market_value.replace('亿', '')) * 10000
            else:
                total_market_value = float(total_market_value) / 10000
            result['TCAP'] = np.array([total_market_value], dtype=np.float64)
        except:
            result['TCAP'] = np.array([0.0], dtype=np.float64)
        
        # 其他财务指标使用默认值
        result['AS'] = np.array([0.0], dtype=np.float64)
        result['BS'] = np.array([0.0], dtype=np.float64)
        result['GOS'] = np.array([0.0], dtype=np.float64)
        result['FIS'] = np.array([0.0], dtype=np.float64)
        result['FCS'] = np.array([0.0], dtype=np.float64)
        result['NP'] = np.array([0.0], dtype=np.float64)
        result['NAVPS'] = np.array([1.0], dtype=np.float64)
        result['ROE'] = np.array([0.0], dtype=np.float64)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to fetch finance data for {symbol}: {e}")
        return {}


def fetch_fundflow_data(symbol: str, start_date: str, end_date: str) -> Dict[str, np.ndarray]:
    """获取资金流向数据"""
    try:
        ak_symbol = convert_symbol_format(symbol)
        stock_code = ak_symbol[2:]
        
        # 获取资金流向数据 - 使用正确的参数名
        fundflow_df = ak.stock_individual_fund_flow_rank()
        if fundflow_df is None or fundflow_df.empty:
            return {}
            
        # 筛选特定股票的数据
        stock_data = fundflow_df[fundflow_df['代码'] == stock_code]
        if stock_data.empty:
            return {}
        
        # 重命名列以匹配原有格式
        result = {}
        
        # 主力净流入
        if '主力净流入-净额' in stock_data.columns:
            result['A_A'] = np.array([float(stock_data['主力净流入-净额'].values[0])], dtype=np.float64)
            result['A_R'] = np.array([float(stock_data['主力净流入-净占比'].values[0])], dtype=np.float64)
        
        # 超大单净流入
        if '超大单净流入-净额' in stock_data.columns:
            result['XL_A'] = np.array([float(stock_data['超大单净流入-净额'].values[0])], dtype=np.float64)
            result['XL_R'] = np.array([float(stock_data['超大单净流入-净占比'].values[0])], dtype=np.float64)
        
        # 大单净流入
        if '大单净流入-净额' in stock_data.columns:
            result['L_A'] = np.array([float(stock_data['大单净流入-净额'].values[0])], dtype=np.float64)
            result['L_R'] = np.array([float(stock_data['大单净流入-净占比'].values[0])], dtype=np.float64)
        
        # 中单净流入
        if '中单净流入-净额' in stock_data.columns:
            result['M_A'] = np.array([float(stock_data['中单净流入-净额'].values[0])], dtype=np.float64)
            result['M_R'] = np.array([float(stock_data['中单净流入-净占比'].values[0])], dtype=np.float64)
        
        # 小单净流入
        if '小单净流入-净额' in stock_data.columns:
            result['S_A'] = np.array([float(stock_data['小单净流入-净额'].values[0])], dtype=np.float64)
            result['S_R'] = np.array([float(stock_data['小单净流入-净占比'].values[0])], dtype=np.float64)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to fetch fundflow data for {symbol}: {e}")
        return {}


# 保持向后兼容性
load_data_msd = load_data_akshare
load_data_msd_batch = load_data_akshare_batch
