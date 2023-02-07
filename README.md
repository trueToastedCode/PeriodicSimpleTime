# PeriodicSimpleTime

This package helps to manage periodic events.

### Calculate next periodic datetime
```
from periodic_simpletime import *

# for this example, current utc time is 2023-01-01 11:56:02
period = PeriodicSimpleTime(minute=5)
next_end_dt = get_next_periodic_dt(period)
> 2023-01-01 12:00:00 (utc)
```