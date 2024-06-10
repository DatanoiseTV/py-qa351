from qa351_usb import QA351USB

def main():
    qa351 = QA351USB()
    
    try:
        if qa351.open():
            qa351.kick_led()
            firmware_version = qa351.get_firmware_version()
            print(f"Firmware Version: {firmware_version}")
            
            product_id = qa351.get_product_id()
            print(f"Product ID: {product_id}")
            
            msp_temp = qa351.get_msp_temp()
            print(f"MSP Temperature: {msp_temp}")
            
            voltage_counts = qa351.read_voltage_counts()
            print(f"Voltage Counts: {voltage_counts}")
            
            fifo_depth = qa351.get_fifo_depth()
            print(f"FIFO Depth: {fifo_depth}")
            
            voltage_stream = qa351.read_voltage_stream()
            print(f"Voltage Stream: {voltage_stream}")
            
            qa351.set_atten(0)  # Example to set attenuator
            qa351.set_sample_rate('Slow')  # Example to set sample rate
            
            qa351.start_rms_conversion()
            rms_counts = qa351.read_rms_counts()
            print(f"RMS Counts: {rms_counts}")
            
            qa351.close()
        else:
            print("Failed to open the QA351.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

