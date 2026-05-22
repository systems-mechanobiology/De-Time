from zipline.api import order_target_percent, record, symbol

# Precompute De-Time signals outside Zipline, store them in a calendar-safe
# bundle/CSV/Pipeline field, and align them to the Zipline trading calendar.

def initialize(context):
    context.asset = symbol('AAPL')


def handle_data(context, data):
    sig = 0  # Replace with a date-indexed De-Time signal lookup.
    if sig > 0:
        order_target_percent(context.asset, 1.0)
    elif sig < 0:
        order_target_percent(context.asset, -1.0)
    else:
        order_target_percent(context.asset, 0.0)
    record(detime_signal=sig)
