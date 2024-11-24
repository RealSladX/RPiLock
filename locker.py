
'''
RFID LOCKER CODE BASE
578 WIRELESS NETWORKS

Authors: Dalston J. "Slad" Karto, ... , ..., ...

'''

import sqlite3
from datetime import datetime

'''

# # # # # # # LOCKER CLASS WOOOOOO!!! # # # # # # #  #
 #Main attributes:
  - Locker ID
  - Master Tag
  - Lock (Boolean State)
  - Current User Tag
'''
class Locker:
    def __init__(self, locker_id, master_tag):
        self.locker_id = locker_id
        self.master_tag = master_tag
        self.locked = True  # Assume locker starts in a locked state
        self.current_user_tag = None

    def lock(self):
        self.locked = True
        print(f"Locker {self.locker_id} is now locked.")

    def unlock(self):
        self.locked = False
        print(f"Locker {self.locker_id} is now unlocked.")

    
    def toggle_lock(self, rfid_tag):
        """
        Logic Controller. 
        Checks if the card (UID) that is tapped is either the Master Card, or the currently assigned tag
        """
        if rfid_tag == self.master_tag:
            # Always toggle lock/unlock if the master tag is scanned
            if self.locked:
                self.unlock()
            else:
                self.lock()
        elif rfid_tag == self.current_user_tag:
            # Toggle based on the user's tag
            if self.locked:
                self.unlock()
            else:
                self.lock()
        elif self.current_user_tag is None and self.locked:
            # Assign the first user who scans an RFID when the locker is locked
            self.current_user_tag = rfid_tag
            self.unlock()
            print(
                f"Locker {self.locker_id}: RFID {rfid_tag} is now assigned to this locker."
            )
        else:
            print(f"Access Denied for RFID Tag: {rfid_tag}")

    
    def current_state(self): 
        return "locked" if self.locked else "unlocked"


# Initialize the SQLite database to track locker states
def init_locker_db():
    '''
    LOCKER DATABASE (SQL) YEAHHHHHHH!!!!!!!
    '''
    conn = sqlite3.connect("locker_data.db")
    c = conn.cursor()

    # Create a table for storing locker states
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS locker_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            locker_id TEXT NOT NULL,
            user_tag TEXT,
            timestamp TEXT NOT NULL,
            state TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# Log locker state changes to the database
def log_locker_state(locker_id, user_tag, state):
    
    conn = sqlite3.connect("locker_data.db")
    c = conn.cursor()

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert the locker state into the database
    c.execute(
        """
        INSERT INTO locker_log (locker_id, user_tag, timestamp, state)
        VALUES (?, ?, ?, ?)
    """,
        (locker_id, user_tag, timestamp, state),
    )

    conn.commit()
    conn.close()

    print(f"Logged Locker {locker_id} - RFID Tag {user_tag} - State: {state}")


def read_rfid_tags(serial_in, locker):
    """
    Reads RFID tags from the simulated serial input, processes them with the locker system,
    and logs any changes in the locker state to the database.
    """
    while True:
        # Simulate reading from a serial input
        serial_in.seek(0)  # Move cursor back to the start to read new data
        rfid_tag = serial_in.readline().strip()

        if rfid_tag:
            # Process the RFID tag with the locker
            prev_state = locker.current_state()
            locker.toggle_lock(rfid_tag)
            new_state = locker.current_state()

            # If the state has changed, log the change
            if prev_state != new_state:
                log_locker_state(locker.locker_id, rfid_tag, new_state)

        # Clear the simulated input after reading
        serial_in.truncate(0)
        serial_in.seek(0)

        # Simulate processing delay
        time.sleep(1)


import io
import random
import threading
import time

# Simulate a list of RFID tags
rfid_tags = ["123456789ABC", "987654321DEF", "A1B2C3D4E5F6", "556677889900"]

# Create a simulated serial output using StringIO
simulated_serial_out = io.StringIO()


def simulate_rfid_reader(serial_out):
    """
    Simulates RFID reader by writing random RFID tags to the serial output.
    """
    while True:
        # Simulate the RFID tag being read
        rfid_tag = random.choice(rfid_tags)

        # Write the RFID tag to the simulated serial output
        serial_out.write(rfid_tag + "\n")
        serial_out.seek(0)  # Reset the cursor to the start

        print(f"Simulated RFID Reader: Sent tag {rfid_tag}")

        # Simulate a delay between tag reads
        time.sleep(2)



import sqlite3

def view_locker_history():
    """
    Connects to the SQLite database and retrieves all locker log history.
    Displays the locker ID, user RFID, timestamp, and state.
    """
    conn = sqlite3.connect('locker_data.db')
    c = conn.cursor()
    
    # Retrieve all records from the locker_log table
    c.execute('SELECT * FROM locker_log')
    rows = c.fetchall()

    # Display the history
    print("Locker History:")
    print("ID | Locker ID | User RFID | Timestamp | State")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    
    conn.close()



# if __name__ == "__main__":
#     # Initialize the SQLite database for locker state logging
#     init_locker_db()
#
#     # Define the master RFID tag for the locker
#     master_rfid_tag = "A1B2C3D4E5F6"
#
#     # Initialize a locker with a master RFID tag
#     locker = Locker(locker_id="1", master_tag=master_rfid_tag)
#
#     # Run the RFID reader simulation in the background
#     reader_thread = threading.Thread(
#         target=simulate_rfid_reader, args=(simulated_serial_out,)
#     )
#     reader_thread.daemon = True
#     reader_thread.start()
#
#     # Run the RFID processing system with locker management
#     processing_thread = threading.Thread(
#         target=read_rfid_tags, args=(simulated_serial_out, locker)
#     )
#     processing_thread.daemon = True
#     processing_thread.start()
#
#     try:
#         # Keep the main program running to allow the background threads to simulate the system
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Simulation terminated.")
