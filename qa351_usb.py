import hid
import struct

# Constants
USB_VID = 0x2047  # Replace with actual Vendor ID
USB_PID = 0x0301  # Replace with actual Product ID
TIMEOUT = 50

# Commands
CMD_KICK_LED = 0x00
CMD_READ_ADC = 0x01
CMD_SET_PGA = 0x02
CMD_SET_ATTEN = 0x03
CMD_STREAM_DATA = 0x04
CMD_QUERY_FIFO_COUNT = 0x05
CMD_SET_SAMPLE_RATE = 0x06
CMD_SET_MODE = 0x0C
CMD_START_RMS_CONVERSION = 0x0D
CMD_RETRIEVE_RMS_READING = 0x0E
CMD_READ_TEMP_SENSOR = 0x33
CMD_RESET = 0xFB
CMD_READ_SERIAL_NUMBER = 0xFD
CMD_READ_FIRMWARE_VERSION = 0xFE
CMD_ENTER_BSL = 0xFF

class QA351USB:
    INVALID_VALUE = 0x80FFFFFF

    def __init__(self):
        self.device = None
        self.timeout = TIMEOUT
        self.mode = 0  # Default to DC mode

    def open(self):
        for dev in hid.enumerate(USB_VID, USB_PID):
            if dev['vendor_id'] == USB_VID and dev['product_id'] == USB_PID:
                self.device = hid.Device(path=dev['path'])
                break

        if self.device is None:
            raise ValueError("Device not found")

        self.device.nonblocking = True
        self.reset()
        return True

    def close(self):
        if self.device:
            self.device.close()
            self.device = None

    def send_recv(self, command):
        self.usb_send_data([command, 0x00])
        return self.usb_recv_data()

    def get_firmware_version(self):
        return self.send_recv(CMD_READ_FIRMWARE_VERSION)

    def get_product_id(self):
        return self.send_recv(CMD_READ_SERIAL_NUMBER)

    def get_msp_temp(self):
        return self.send_recv(CMD_READ_TEMP_SENSOR)

    def read_voltage_counts(self):
        if self.get_mode() != 0:  # Mode.DC
            raise ValueError("Invalid mode operation in ReadVoltageCounts()")

        raw_val = self.send_recv(CMD_READ_ADC)
        if raw_val == self.INVALID_VALUE:
            return self.INVALID_VALUE

        val = struct.unpack('>I', bytes(raw_val))[0]
        if ((val >> 16) & 0xFF) > 0x80:
            val |= 0xFF000000
        else:
            val &= 0x00FFFFFF

        return val

    def get_fifo_depth(self):
        return self.send_recv(CMD_QUERY_FIFO_COUNT)

    def read_voltage_stream(self):
        samples = []
        self.usb_send_data([CMD_STREAM_DATA, 0x00])
        word_buf = self.usb_recv_data()

        for i in range(0, len(word_buf), 4):
            seq_id = word_buf[i]
            data = struct.unpack('>i', bytes([word_buf[i], word_buf[i+1], word_buf[i+2], word_buf[i+3]]))[0]
            samples.append((seq_id, data))

        return samples

    def set_atten(self, atten):
        self.usb_send_data([CMD_SET_ATTEN, atten])

    def set_sample_rate(self, sample_rate):
        val = 0 if sample_rate == 'Slow' else 1
        self.usb_send_data([CMD_SET_SAMPLE_RATE, val])

    def reset(self):
        self.usb_send_data([CMD_RESET, 0x00])

    def set_mode(self, mode):
        self.usb_send_data([CMD_SET_MODE, mode])
        self.mode = mode

    def get_mode(self):
        return self.mode

    def start_rms_conversion(self):
        self.usb_send_data([CMD_START_RMS_CONVERSION, 0x00])

    def read_rms_counts(self):
        if self.get_mode() != 1:  # Mode.RMS
            raise ValueError("Invalid mode operation in ReadRmsCounts()")

        raw_val = self.send_recv(CMD_RETRIEVE_RMS_READING)
        if raw_val == self.INVALID_VALUE:
            return self.INVALID_VALUE

        val = struct.unpack('>I', bytes(raw_val))[0]
        if ((val >> 16) & 0xFF) > 0x80:
            val |= 0xFF000000
        else:
            val &= 0x00FFFFFF

        return val

    def kick_led(self):
        self.usb_send_data([CMD_KICK_LED, 0x00])

    def enter_bsl(self):
        self.usb_send_data([CMD_ENTER_BSL, 0x00])

    def usb_send_data(self, data):
        if len(data) > 62:
            raise ValueError("Data cannot be longer than 62 bytes in length")
        frame = [0x3F, len(data)] + data
        self.device.write(bytes(frame))

    def usb_recv_data(self):
        response = self.device.read(64)
        if response[0] == 0x3F:
            return response[2:2 + response[1]]
        else:
            raise ValueError("USB receive failed")

