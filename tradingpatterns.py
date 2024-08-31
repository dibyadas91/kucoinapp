import time
import pdb
import numpy as np
import pandas as pd
from kucoin_futures.client import Market

# Initialize KuCoin API client
api_key = '66d37d103adcd3000179b1fe'
api_secret = '1065c68d-8ecb-410b-88ba-941a28d4d180'
api_passphrase = 'Gofuckyourmom23'

client = Market(api_key, api_secret, api_passphrase)


# Function to get historical data
def get_klines(symbol, interval):
    klines = client.get_kline_data(symbol, interval)
    df = pd.DataFrame(klines[:20], columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
    df.set_index('timestamp', inplace=True)
    return df


# Function to detect Head and Shoulders pattern
def is_head_and_shoulders(df):
    closes = df['close'].values

    if len(closes) < 5:
        return False

    # Find peaks and troughs
    peaks = []
    troughs = []

    for i in range(1, len(closes) - 1):
        if closes[i - 1] < closes[i] > closes[i + 1]:
            peaks.append(i)
        if closes[i - 1] > closes[i] < closes[i + 1]:
            troughs.append(i)

    # Basic Head and Shoulders logic:
    # - We should have at least two peaks and one trough in between
    if len(peaks) < 2 or len(troughs) < 1:
        return False

    # Validate the Head and Shoulders pattern:
    # Left Shoulder < Head > Right Shoulder
    left_shoulder = peaks[0]
    head = peaks[1]

    if len(peaks) > 2:
        right_shoulder = peaks[2]
    else:
        right_shoulder = len(closes) - 1

    if closes[left_shoulder] < closes[head] and closes[right_shoulder] < closes[head]:
        if troughs[0] > left_shoulder and troughs[0] < head:
            return True

    return False


def is_double_top(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False

    peaks = [i for i in range(1, len(closes) - 1) if closes[i - 1] < closes[i] > closes[i + 1]]
    if len(peaks) < 2:
        return False

    if abs(closes[peaks[0]] - closes[peaks[1]]) / closes[peaks[0]] < 0.02:  # Allow small variation
        return closes[peaks[1]:].min() < closes[peaks[0]]  # Check for a dip after the second peak

    return False


def is_double_bottom(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False

    troughs = [i for i in range(1, len(closes) - 1) if closes[i - 1] > closes[i] < closes[i + 1]]
    if len(troughs) < 2:
        return False

    if abs(closes[troughs[0]] - closes[troughs[1]]) / closes[troughs[0]] < 0.02:  # Allow small variation
        return closes[troughs[1]:].max() > closes[troughs[0]]  # Check for a rise after the second trough

    return False


def is_cup_and_handle(df):
    closes = df['close'].values
    if len(closes) < 10:
        return False

    cup_start = np.argmin(closes)
    cup_end = cup_start + np.argmax(closes[cup_start:])

    if cup_start == 0 or cup_end == len(closes) - 1:
        return False

    handle_start = cup_end + 1
    handle_end = handle_start + len(closes[handle_start:]) // 2

    if handle_end >= len(closes):
        handle_end = len(closes) - 1

    if closes[cup_start] < closes[cup_end] and closes[handle_end] > closes[handle_start]:
        return True

    return False


def is_triangle(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False

    lower_highs = all(closes[i] < closes[i - 1] for i in range(1, len(closes)))
    higher_lows = all(closes[i] > closes[i - 1] for i in range(1, len(closes)))

    if lower_highs or higher_lows:
        return True

    return False


def is_flag_or_pennant(df):
    closes = df['close'].values
    if len(closes) < 6:
        return False

    flagpole = closes[:3]
    consolidation = closes[3:]

    if all(flagpole[i] < flagpole[i + 1] for i in range(len(flagpole) - 1)) and \
            all(abs(consolidation[i] - consolidation[i + 1]) < abs(flagpole[-1] - flagpole[0]) / 2 for i in
                range(len(consolidation) - 1)):
        return True

    return False


def is_engulfing(df):
    closes = df['close'].values
    opens = df['open'].values
    if len(closes) < 2:
        return False

    if closes[-2] < opens[-2] and closes[-1] > opens[-1] and closes[-1] > opens[-2] and opens[-1] < closes[-2]:
        return True  # Bullish engulfing
    elif closes[-2] > opens[-2] and closes[-1] < opens[-1] and closes[-1] < opens[-2] and opens[-1] > closes[-2]:
        return True  # Bearish engulfing

    return False


def is_wedge(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False

    falling_wedge = all(closes[i] < closes[i - 1] for i in range(1, len(closes)))
    rising_wedge = all(closes[i] > closes[i - 1] for i in range(1, len(closes)))

    if falling_wedge or rising_wedge:
        return True

    return False


def is_rounding_bottom(df):
    closes = df['close'].values
    if len(closes) < 10:
        return False

    middle = len(closes) // 2
    left_side = closes[:middle]
    right_side = closes[middle:]

    if all(left_side[i] > left_side[i + 1] for i in range(len(left_side) - 1)) and \
            all(right_side[i] < right_side[i + 1] for i in range(len(right_side) - 1)):
        return True

    return False


def is_morning_star(df):
    closes = df['close'].values
    opens = df['open'].values
    if len(closes) < 3:
        return False

    if closes[-3] < opens[-3] and closes[-2] < opens[-2] and closes[-2] < closes[-3] and closes[-1] > opens[-1] and \
            closes[-1] > closes[-2]:
        return True  # Morning star

    return False


def is_evening_star(df):
    closes = df['close'].values
    opens = df['open'].values
    if len(closes) < 3:
        return False

    if closes[-3] > opens[-3] and closes[-2] > opens[-2] and closes[-2] > closes[-3] and closes[-1] < opens[-1] and \
            closes[-1] < closes[-2]:
        return True  # Evening star

    return False


# Fetch all futures trading pairs
futures_pairs = client.get_contracts_list()

# Define the time interval for checking the pattern (e.g., 1-hour candles)
interval = '1hour'

# Iterate over each futures pair and check for Head and Shoulders pattern
for pair in futures_pairs:
    symbol = pair['symbol']
    try:
        df = get_klines(symbol, 240)
        if df is not None:
            try:
                if is_head_and_shoulders(df):
                    print(f"Head and Shoulders pattern detected on {symbol}")
                elif is_double_top(df):
                    print(f"Double Top pattern detected on {symbol}")
                elif is_double_bottom(df):
                    print(f"Double Bottom pattern detected on {symbol}")
                elif is_cup_and_handle(df):
                    print(f"Cup and Handle pattern detected on {symbol}")
                elif is_triangle(df):
                    print(f"Triangle pattern detected on {symbol}")
                elif is_flag_or_pennant(df):
                    print(f"Flag or Pennant pattern detected on {symbol}")
                elif is_engulfing(df):
                    print(f"Engulfing pattern detected on {symbol}")
                elif is_wedge(df):
                    print(f"Wedge pattern detected on {symbol}")
                elif is_rounding_bottom(df):
                    print(f"Rounding Bottom pattern detected on {symbol}")
                elif is_morning_star(df):
                    print(f"Morning Star pattern detected on {symbol}")
                elif is_evening_star(df):
                    print(f"Evening Star pattern detected on {symbol}")
            except Exception as e:
                print(f"Error processing {symbol}: {e}")

            # Sleep between requests to avoid rate limits
        time.sleep(1)
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

    # Sleep between requests to avoid rate limits
    time.sleep(1)
