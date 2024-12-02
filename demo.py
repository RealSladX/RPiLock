import time
import binascii
from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c
import RPi.GPIO as GPIO

PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)
SOLENOID_PIN = 17

def setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SOLENOID_PIN, GPIO.OUT)
	
	# Initialize the PN532 NFC module
	nfc.begin()

	versiondata = nfc.getFirmwareVersion()
	if not versiondata:
		print("Didn't find PN53x board")
		raise RuntimeError("Didn't find PN53x board")  # halt program if NFC module is not found

	# Display firmware version
	print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
																(versiondata >> 8) & 0xFF))
	# Configure for continuous scanning with passive activation retries
	nfc.setPassiveActivationRetries(0xFF)
	nfc.SAMConfig()  # configure board to read RFID tags
	print("Waiting for an ISO14443A card")

def open_solenoid(open_time):
	GPIO.output(SOLENOID_PIN, GPIO.HIGH)
	time.sleep(open_time)
	GPIO.output(SOLENOID_PIN, GPIO.LOW)

def scan_card():
	success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

	if success:
		# Convert UID to hexadecimal format for comparison
		uid_hex = binascii.hexlify(bytearray(uid)).decode("utf-8").upper()
		print("Found card with UID:", uid_hex)
		return uid_hex
	else:
		print("Timed out waiting for a card")

if __name__ == '__main__':
	setup()
	try:
		active_card = None
		while True:
			# Scan for a card if locker is not assigned one
			while not active_card:
				active_card = scan_card()
			
			print("Opening locker for 5 seconds.")
			open_solenoid(5)

			# Scan for a card and check if it's the one assigned to the locker
			while active_card:
				new_card = scan_card()
				if new_card == active_card:
					print("Correct card found. Unassigning current card.")
					print("Opening locker for 5 seconds.")
					open_solenoid(5)
					active_card = None
				elif new_card is not None:
					print(f"Incorrect card with UID: {new_card}. Try again.")
					time.sleep(1)
	finally:
		GPIO.cleanup()

