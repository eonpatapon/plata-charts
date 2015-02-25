import logging
import random
from itertools import tee, islice, chain, izip

from dateutil.rrule import rrule, MONTHLY, WEEKLY, YEARLY
from dateutil.parser import parse as parse_date
from datetime import datetime
import calendar

from plata.shop.models import OrderItem, Order

from plata_charts.models import ChartCache, ChartQuery


calendar.setfirstweekday(calendar.MONDAY)
cal = calendar.Calendar()
logger = logging.getLogger(__name__)


class NoProductOrders(Exception):
    pass


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def _random_color():
    rgb = []
    rand_int = [random.randint(0, 1) for i in range(48)]
    for index, bits in enumerate(chunks(rand_int, 8)):
        if not index % 2:
            continue
        color = bits[:4] + [0] * 4
        rgb.append(int("".join([str(b) for b in color]), 2))
    return rgb


def random_colors(n):
    """
    Yields 'n' random tuples of integers
    representing an RGB color.
    """
    for c in xrange(0, n):
        yield _random_color()


def previous_and_next(iterable):
    """
    From an iterable return a list of
    (prev, current, next) values tuples

    @type iterable: iterable

    @return: list of tuples
    """
    prevs, items, nexts = tee(iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)


def find_closest_ts(range, date):
    """
    From the date, find the closest date in the range list

    @return: date
    """
    for p, c, n in previous_and_next(range):
        if date >= c and date <= (n or date):
            return c

    # should not happen
    raise Exception("Cannot map date %s" % date)


def _find_week_first_date(date):
    for week in cal.monthdatescalendar(date.year, date.month):
        for day in week:
            if day.day == date.day:
                for week_day in week:
                    if week_day.month == date.month:
                        return datetime.combine(week_day, date.timetz())


def _find_month_first_date(date):
    for week in cal.monthdatescalendar(date.year, date.month):
        for day in week:
            if day.month == date.month:
                return datetime.combine(day, date.timetz())


def date_range(step, start_date, end_date):
    if step == YEARLY:
        # first day of year
        start_date = start_date.replace(month=1, day=1)
    elif step == MONTHLY:
        # get first day of the month
        start_date = _find_month_first_date(start_date)
    elif step == WEEKLY:
        # get first day of the week
        start_date = _find_week_first_date(start_date)
    return list(rrule(step, dtstart=start_date, until=end_date))


def range_order_items_query(filter_dict, start_date=None, end_date=None):
    query = OrderItem.objects.filter(**filter_dict) \
                             .filter(order__status__gte=Order.PAID) \
                             .order_by('order__confirmed')

    if start_date is not None:
        query = query.filter(order__confirmed__gte=start_date)
    if end_date is not None:
        query = query.filter(order__confirmed__lte=end_date)

    return query


def range_order_items(filter_dict, range):
    # list of (OrderItem, Order confirmed date)
    def _serialize_items(item):
        return (str(item.product),
                float(item.discounted_subtotal_excl_tax),
                find_closest_ts(range, item.order.confirmed))
    return map(_serialize_items, range_order_items_query(filter_dict, range[0], range[-1]))


def product_orders(uuid,
                   filter_dict,
                   start_date=None,
                   end_date=None,
                   step=MONTHLY,
                   count_type=0):
    """
    Return the count of product orders between start_date and end_date.

    The step range can be YEARLY, MONTHLY, WEEKLY or DAILY. Theses are integers
    from the rrule module (0, 1, 2, 3).

    If no start_date or end_date is specified we take the first (and/or last) date
    we found in the query result.

    To query product pass a dictionnary to filter on OrderItem.product model. Ex:

      {'product__slug': 'foo'}

    The query can match many products.

    @type filter_dict: dict
    @type start_date: datetime
    @type end_date: datetime
    @type step: int

    @return: list of dates range and product orders counts for that range
    """

    if start_date is None:
        try:
            start_date = range_order_items_query(filter_dict)[0].order.confirmed
        except IndexError:
            # no orders found
            raise NoProductOrders()

    if end_date is None:
        end_date = range_order_items_query(filter_dict).last().order.confirmed

    # sanitize dates, we don't need hours, minutes, etc..
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    ranges = []
    orders = []

    # the range we want to compute orders for
    final_range = date_range(step, start_date, end_date)
    start_date = final_range[0]
    end_date = final_range[-1]

    chart_cache, created = ChartCache.objects.get_or_create(uuid=uuid, step=step)
    chart_cache.uuid = uuid
    chart_cache.step = step

    if not created:
        logger.debug("Retrieving cache data...")
        # convert isoformat dates to datetime
        cache_range = map(lambda d: parse_date(d), chart_cache.cache['range'])
        cache_orders = map(lambda (i, t, d): (i, float(t), parse_date(d)),
                           chart_cache.cache['orders'])

        if cache_range and cache_orders:
            ranges = [cache_range]
            orders = [cache_orders]
        # expand the cache range if needed
        if start_date not in cache_range:
            logger.debug("Expand the cache range at the end")
            ranges.insert(0, date_range(step, start_date, cache_range[0]))
            orders.insert(0, None)
        if end_date not in cache_range:
            logger.debug("Expand the cache range at the beggining")
            ranges.append(date_range(step, cache_range[-1], end_date))
            orders.append(None)
    else:
        # no cache available, just compute the full range
        ranges = [final_range]
        orders = [None]

    # count orders for new ranges
    for index, (order, range) in enumerate(zip(orders, ranges)):
        if order is None:
            logger.debug("Getting orders for new range")
            orders[index] = range_order_items(filter_dict, range)

    logger.debug("Count orders")
    # for each date in the range, count orders
    final_counts = {}
    for index, date in enumerate(final_range):
        for order in orders:
            for item, item_price, item_date in order:
                if item_date == date:
                    if item not in final_counts:
                        final_counts[item] = [0] * len(final_range)
                    if count_type == ChartQuery.COUNT_INCOME:
                        final_counts[item][index] += item_price
                    elif count_type == ChartQuery.COUNT_ORDERS:
                        final_counts[item][index] += 1
    logger.debug("Done")

    logger.debug("Saving cache")
    chart_cache.cache = {'range': list(chain(*ranges)), 'orders': list(chain(*orders))}
    chart_cache.save()

    return (final_range, final_counts)
