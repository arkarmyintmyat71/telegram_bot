from . import admin, callback, customer, start

# Order matters: admin router first, so admin replies/commands are handled
# before the generic customer catch-all router gets a chance.
all_routers = [start.router, admin.router, callback.router, customer.router]
