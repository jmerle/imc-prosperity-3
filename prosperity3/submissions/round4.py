import json
from abc import abstractmethod
from enum import IntEnum
from math import ceil, floor
from typing import Any

import pandas as pd
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState

type JSON = dict[str, Any] | list[Any] | str | int | float | bool | None


class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(
            self.to_json(
                [
                    self.compress_state(state, self.truncate(state.traderData, max_item_length)),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            [],  # self.compress_trades(state.own_trades),
            [],  # self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing.symbol, listing.product, listing.denomination])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append(
                    [
                        trade.symbol,
                        trade.price,
                        trade.quantity,
                        trade.buyer,
                        trade.seller,
                        trade.timestamp,
                    ]
                )

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sugarPrice,
                observation.sunlightIndex,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        lo, hi = 0, min(len(value), max_length)
        out = ""

        while lo <= hi:
            mid = (lo + hi) // 2

            candidate = value[:mid]
            if len(candidate) < len(value):
                candidate += "..."

            encoded_candidate = json.dumps(candidate)

            if len(encoded_candidate) <= max_length:
                out = candidate
                lo = mid + 1
            else:
                hi = mid - 1

        return out


logger = Logger()


class Strategy[T: JSON]:
    def __init__(self, symbol: str, limit: int) -> None:
        self.symbol = symbol
        self.limit = limit

    @abstractmethod
    def act(self, state: TradingState) -> None:
        raise NotImplementedError()

    def get_required_symbols(self) -> list[Symbol]:
        return [self.symbol]

    def run(self, state: TradingState) -> tuple[list[Order], int]:
        self.orders = list[Order]()
        self.conversions = 0

        if all(
            (
                v in state.order_depths
                and len(state.order_depths[v].buy_orders) > 0
                and len(state.order_depths[v].sell_orders) > 0
            )
            for v in self.get_required_symbols()
        ):
            self.act(state)

        return self.orders, self.conversions

    def buy(self, price: int, quantity: int) -> None:
        self.orders.append(Order(self.symbol, price, quantity))

    def sell(self, price: int, quantity: int) -> None:
        self.orders.append(Order(self.symbol, price, -quantity))

    def convert(self, amount: int) -> None:
        self.conversions += amount

    def get_mid_price(self, state: TradingState, symbol: str) -> float:
        order_depth = state.order_depths[symbol]
        buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
        sell_orders = sorted(order_depth.sell_orders.items())

        popular_buy_price = max(buy_orders, key=lambda tup: tup[1])[0]
        popular_sell_price = min(sell_orders, key=lambda tup: tup[1])[0]

        return (popular_buy_price + popular_sell_price) / 2


class StatefulStrategy[T: JSON](Strategy):
    @abstractmethod
    def save(self) -> T:
        raise NotImplementedError()

    @abstractmethod
    def load(self, data: T) -> None:
        raise NotImplementedError()


class Signal(IntEnum):
    NEUTRAL = 0
    SHORT = 1
    LONG = 2


class SignalStrategy(StatefulStrategy[int]):
    def __init__(self, symbol: Symbol, limit: int) -> None:
        super().__init__(symbol, limit)

        self.signal = Signal.NEUTRAL

    @abstractmethod
    def get_signal(self, state: TradingState) -> Signal | None:
        raise NotImplementedError()

    def act(self, state: TradingState) -> None:
        new_signal = self.get_signal(state)
        if new_signal is not None:
            self.signal = new_signal

        position = state.position.get(self.symbol, 0)
        order_depth = state.order_depths[self.symbol]

        if self.signal == Signal.NEUTRAL:
            if position < 0:
                self.buy(self.get_buy_price(order_depth), -position)
            elif position > 0:
                self.sell(self.get_sell_price(order_depth), position)
        elif self.signal == Signal.SHORT:
            self.sell(self.get_sell_price(order_depth), self.limit + position)
        elif self.signal == Signal.LONG:
            self.buy(self.get_buy_price(order_depth), self.limit - position)

    def get_buy_price(self, order_depth: OrderDepth) -> int:
        return min(order_depth.sell_orders.keys())

    def get_sell_price(self, order_depth: OrderDepth) -> int:
        return max(order_depth.buy_orders.keys())

    def save(self) -> int:
        return self.signal.value

    def load(self, data: int) -> None:
        self.signal = Signal(data)


class InvertedSignalStrategy(SignalStrategy):
    def __init__(self, symbol: Symbol, limit: int, underlying: SignalStrategy) -> None:
        super().__init__(symbol, limit)

        self.underlying = underlying

    def get_required_symbols(self) -> list[Symbol]:
        return [self.symbol, *self.underlying.get_required_symbols()]

    def get_signal(self, state: TradingState) -> Signal | None:
        signal = self.underlying.get_signal(state)

        if signal == Signal.LONG:
            return Signal.SHORT
        elif signal == Signal.SHORT:
            return Signal.LONG
        else:
            return signal


class MarketMakingStrategy(Strategy):
    def __init__(self, symbol: Symbol, limit: int) -> None:
        super().__init__(symbol, limit)

    @abstractmethod
    def get_true_value(self, state: TradingState) -> float:
        raise NotImplementedError()

    def act(self, state: TradingState) -> None:
        true_value = self.get_true_value(state)

        order_depth = state.order_depths[self.symbol]
        buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)
        sell_orders = sorted(order_depth.sell_orders.items())

        position = state.position.get(self.symbol, 0)
        to_buy = self.limit - position
        to_sell = self.limit + position

        max_buy_price = int(true_value) - 1 if true_value % 1 == 0 else floor(true_value)
        min_sell_price = int(true_value) + 1 if true_value % 1 == 0 else ceil(true_value)

        for price, volume in sell_orders:
            if to_buy > 0 and price <= max_buy_price:
                quantity = min(to_buy, -volume)
                self.buy(price, quantity)
                to_buy -= quantity

        if to_buy > 0:
            price = next((price + 1 for price, _ in buy_orders if price < max_buy_price), max_buy_price)
            self.buy(price, to_buy)

        for price, volume in buy_orders:
            if to_sell > 0 and price >= min_sell_price:
                quantity = min(to_sell, volume)
                self.sell(price, quantity)
                to_sell -= quantity

        if to_sell > 0:
            price = next((price - 1 for price, _ in sell_orders if price > min_sell_price), min_sell_price)
            self.sell(price, to_sell)


class RainforestResinStrategy(MarketMakingStrategy):
    def get_true_value(self, state: TradingState) -> float:
        expected_true_value = 10_000
        max_delta = 5

        mid_price = self.get_mid_price(state, self.symbol)
        if (expected_true_value - max_delta) <= mid_price <= (expected_true_value + max_delta):
            return expected_true_value

        return mid_price


class KelpStrategy(MarketMakingStrategy):
    def get_true_value(self, state: TradingState) -> float:
        return self.get_mid_price(state, self.symbol)


class RollingZScoreStrategy(SignalStrategy, StatefulStrategy[dict[str, Any]]):
    def __init__(self, symbol: Symbol, limit: int, zscore_period: int, smoothing_period: int, threshold: float) -> None:
        super().__init__(symbol, limit)

        self.zscore_period = zscore_period
        self.smoothing_period = smoothing_period
        self.threshold = threshold

        self.history: list[float] = []

    def get_signal(self, state: TradingState) -> Signal | None:
        self.history.append(self.get_mid_price(state, self.symbol))

        required_history = self.zscore_period + self.smoothing_period
        if len(self.history) < required_history:
            return None
        if len(self.history) > required_history:
            self.history.pop(0)

        hist = pd.Series(self.history)
        score = (
            ((hist - hist.rolling(self.zscore_period).mean()) / hist.rolling(self.zscore_period).std())
            .rolling(self.smoothing_period)
            .mean()
            .iloc[-1]
        )

        if score < -self.threshold:
            return Signal.LONG

        if score > self.threshold:
            return Signal.SHORT

        return None

    def save(self) -> dict[str, Any]:  # type: ignore
        return {"signal": SignalStrategy.save(self), "history": self.history}

    def load(self, data: dict[str, Any]) -> None:  # type: ignore
        SignalStrategy.load(self, data["signal"])
        self.history = data["history"]


class SquidInkStrategy(RollingZScoreStrategy):
    def __init__(self, symbol: Symbol, limit: int) -> None:
        zscore_period = 150
        smoothing_period = 100
        threshold = 1

        super().__init__(symbol, limit, zscore_period, smoothing_period, threshold)


class JamsStrategy(SignalStrategy):
    def get_required_symbols(self) -> list[Symbol]:
        return ["CROISSANTS", "JAMS", "DJEMBES", "PICNIC_BASKET1", "PICNIC_BASKET2"]

    def get_signal(self, state: TradingState) -> Signal | None:
        croissants = self.get_mid_price(state, "CROISSANTS")
        jams = self.get_mid_price(state, "JAMS")
        djembes = self.get_mid_price(state, "DJEMBES")
        picnic_basket1 = self.get_mid_price(state, "PICNIC_BASKET1")
        picnic_basket2 = self.get_mid_price(state, "PICNIC_BASKET2")

        basket_diff = picnic_basket1 - picnic_basket2
        expected_basket_diff = 2 * croissants + jams + djembes
        diff = basket_diff - expected_basket_diff

        long_threshold = -130
        short_threshold = -60

        if diff < long_threshold:
            return Signal.LONG
        elif diff > short_threshold:
            return Signal.SHORT

        return None


class PicnicBasket1Strategy(SignalStrategy):
    def get_required_symbols(self) -> list[Symbol]:
        return ["CROISSANTS", "JAMS", "DJEMBES", "PICNIC_BASKET1"]

    def get_signal(self, state: TradingState) -> Signal | None:
        croissants = self.get_mid_price(state, "CROISSANTS")
        jams = self.get_mid_price(state, "JAMS")
        djembes = self.get_mid_price(state, "DJEMBES")
        picnic_basket1 = self.get_mid_price(state, "PICNIC_BASKET1")

        diff = picnic_basket1 - 6 * croissants - 3 * jams - djembes

        long_threshold = -10
        short_threshold = 70

        if diff < long_threshold:
            return Signal.LONG
        elif diff > short_threshold:
            return Signal.SHORT

        return None


class PicnicBasket2Strategy(SignalStrategy):
    def get_required_symbols(self) -> list[Symbol]:
        return ["CROISSANTS", "JAMS", "PICNIC_BASKET2"]

    def get_signal(self, state: TradingState) -> Signal | None:
        croissants = self.get_mid_price(state, "CROISSANTS")
        jams = self.get_mid_price(state, "JAMS")
        picnic_basket2 = self.get_mid_price(state, "PICNIC_BASKET2")

        diff = picnic_basket2 - 4 * croissants - 2 * jams

        long_threshold = -100
        short_threshold = 60

        if diff < long_threshold:
            return Signal.LONG
        elif diff > short_threshold:
            return Signal.SHORT

        return None


class InvertedPicnicBasket1Strategy(InvertedSignalStrategy):
    def __init__(self, symbol: Symbol, limit: int) -> None:
        super().__init__(symbol, limit, PicnicBasket1Strategy(symbol, limit))


class InvertedPicnicBasket2Strategy(InvertedSignalStrategy):
    def __init__(self, symbol: Symbol, limit: int) -> None:
        super().__init__(symbol, limit, PicnicBasket2Strategy(symbol, limit))


class VolcanicRockStrategy(RollingZScoreStrategy):
    def __init__(self, symbol: Symbol, limit: int) -> None:
        zscore_period = 100
        smoothing_period = 20
        threshold = 1.8

        super().__init__(symbol, limit, zscore_period, smoothing_period, threshold)


class MagnificentMacaronsStrategy(Strategy):
    def act(self, state: TradingState) -> None:
        position = state.position.get(self.symbol, 0)
        self.convert(-1 * position)

        obs = state.observations.conversionObservations.get(self.symbol, None)
        if obs is None:
            return

        buy_price = obs.askPrice + obs.transportFees + obs.importTariff
        self.sell(max(int(obs.bidPrice - 0.5), int(buy_price + 1)), 10)


class Trader:
    def __init__(self) -> None:
        limits = {
            "RAINFOREST_RESIN": 50,
            "KELP": 50,
            "SQUID_INK": 50,
            "CROISSANTS": 250,
            "JAMS": 350,
            "DJEMBES": 60,
            "PICNIC_BASKET1": 60,
            "PICNIC_BASKET2": 100,
            "VOLCANIC_ROCK": 400,
            "VOLCANIC_ROCK_VOUCHER_9500": 200,
            "VOLCANIC_ROCK_VOUCHER_9750": 200,
            "VOLCANIC_ROCK_VOUCHER_10000": 200,
            "VOLCANIC_ROCK_VOUCHER_10250": 200,
            "VOLCANIC_ROCK_VOUCHER_10500": 200,
            "MAGNIFICENT_MACARONS": 75,
        }

        self.strategies: dict[Symbol, Strategy] = {
            symbol: clazz(symbol, limits[symbol])
            for symbol, clazz in {
                "RAINFOREST_RESIN": RainforestResinStrategy,
                "KELP": KelpStrategy,
                # # "SQUID_INK": SquidInkStrategy,
                # # "CROISSANTS": InvertedPicnicBasket2Strategy,
                # # "JAMS": JamsStrategy,
                # # "DJEMBES": InvertedPicnicBasket1Strategy,
                "PICNIC_BASKET1": PicnicBasket1Strategy,
                # # "PICNIC_BASKET2": PicnicBasket2Strategy,
                "VOLCANIC_ROCK": VolcanicRockStrategy,
                "VOLCANIC_ROCK_VOUCHER_9500": VolcanicRockStrategy,
                "VOLCANIC_ROCK_VOUCHER_9750": VolcanicRockStrategy,
                "VOLCANIC_ROCK_VOUCHER_10000": VolcanicRockStrategy,
                "VOLCANIC_ROCK_VOUCHER_10250": VolcanicRockStrategy,
                "VOLCANIC_ROCK_VOUCHER_10500": VolcanicRockStrategy,
                # "MAGNIFICENT_MACARONS": MagnificentMacaronsStrategy,
            }.items()
        }

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        orders = {}
        conversions = 0

        old_trader_data = json.loads(state.traderData) if state.traderData != "" else {}
        new_trader_data = {}

        for symbol, strategy in self.strategies.items():
            if isinstance(strategy, StatefulStrategy) and symbol in old_trader_data:
                strategy.load(old_trader_data[symbol])

            if (
                symbol in state.order_depths
                and len(state.order_depths[symbol].buy_orders) > 0
                and len(state.order_depths[symbol].sell_orders) > 0
            ):
                strategy_orders, strategy_conversions = strategy.run(state)
                orders[symbol] = strategy_orders
                conversions += strategy_conversions

            if isinstance(strategy, StatefulStrategy):
                new_trader_data[symbol] = strategy.save()

        trader_data = json.dumps(new_trader_data, separators=(",", ":"))

        logger.flush(state, orders, conversions, trader_data)
        return orders, conversions, trader_data
