import pywinusb.hid as hid

# List all connected HID devices (usually USB devices)
devices = hid.HidDeviceFilter().get_devices()

# Print connected devices
for device in devices:
    print(f"Device found: {device.product_name}, Vendor ID: {device.vendor_id}, Product ID: {device.product_id}")
