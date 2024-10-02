import asyncio
from msf.startup import startup

# Setup or import any devices, settings, etc. For example:
#
# from msf.device import Device, Setting
# duty_u16 = Setting(name="duty_u16", value=8192, description="For use in PWM of pump.")
# water_pump = Device(device_name="water_pump", settings=[duty_u16])
#
# @duty_u16.on_update()
# def pump_change_duty_cycle(new_value):
#     print(f"Adjusted PWM value: {new_value}")


async def main():
    await startup()
    while True:
        await asyncio.sleep(10)


def set_global_exception():
    """
    Debug aid. See Peter Hinch's documentation in micropython-async on github.
    https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md#224-a-typical-firmware-app
    """
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


try:
    set_global_exception()
    asyncio.run(main())
finally:
    asyncio.new_event_loop()