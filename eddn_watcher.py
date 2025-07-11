import zmq
import zlib
import json
import argparse

# EDDN relay address
EDDN_RELAY = "tcp://eddn.edcd.io:9500"

def main():
    """
    Connects to the EDDN feed and prints messages to the console.
    """
    parser = argparse.ArgumentParser(description="EDDN Watcher")
    parser.add_argument(
        '--exploration',
        action='store_true',
        help='If set, only exploration events are shown.'
    )
    parser.add_argument(
        '--new-systems',
        action='store_true',
        help='If set, only exploration events are shown.'
    )
    parser.add_argument(
        '--docking',
        action='store_true',
        help='If set, only docking events are shown.'
    )
    args = parser.parse_args()

    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    # Set subscription to all messages
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
    
    # Set a timeout for receiving messages to avoid blocking indefinitely
    subscriber.setsockopt(zmq.RCVTIMEO, 600000)

    print(f"Connecting to EDDN at {EDDN_RELAY}...")
    subscriber.connect(EDDN_RELAY)
    print("Connected to EDDN. Waiting for messages...")

    try:
        while True:
            try:
                # Receive a raw message
                raw_message = subscriber.recv()

                if raw_message:
                    # Decompress the message
                    decompressed_message = zlib.decompress(raw_message)
                    
                    # Decode from UTF-8 and load as JSON
                    message = json.loads(decompressed_message.decode('utf-8'))
                    message_content = message.get('message', {})
                    event = message_content.get('event')

                    if args.exploration:
                        fss_events = [
                            "CodexEntry",
                            "FSSDiscoveryScan",
                            "Scan",
                            "FSSAllBodiesFound",
                            "FSSBodySignals",
                            "FSSDiscoveryScan",
                            "FSSSignalDiscovered",
                            "MaterialCollected",
                            "MaterialDiscarded",
                            "MaterialDiscovered",
                            "MultiSellExplorationData",
                            "NavBeaconScan",
                            "BuyExplorationData",
                            "SAAScanComplete",
                            "SAASignalsFound",
                            "ScanBaryCentre",
                            "SellExplorationData"
                        ]
                        
                        if event == "FSSDiscoveryScan":
                            print(json.dumps(message, indent=2))

                    elif args.new_systems:
                        # Use local files to persist discovered systems and their JSON objects
                        discovered_systems_file = "discovered_systems.txt"
                        discovered_systems_json_file = "discovered_systems.json"

                        # Load previously discovered systems into a set
                        try:
                            with open(discovered_systems_file, "r") as f:
                                discovered_systems = set(line.strip() for line in f if line.strip())
                        except FileNotFoundError:
                            discovered_systems = set()

                        # Load previously saved system JSON objects into a dict
                        try:
                            with open(discovered_systems_json_file, "r") as f:
                                discovered_systems_json = json.load(f)
                        except (FileNotFoundError, json.JSONDecodeError):
                            discovered_systems_json = {}

                        if event == "Scan":
                            was_discovered = message_content.get('WasDiscovered', False)
                            system_name = message_content.get('StarSystem', 'Unknown System')
                            star_type = message_content.get('StarType')
                            scan_type = message_content.get('ScanType')
                            if (
                                not was_discovered
                                and system_name not in discovered_systems
                                and star_type is not None
                                and scan_type != "NavBeaconDetail"
                            ):
                                print(f"New system discovered: {system_name}")
                                print(f"Star type: {star_type}")
                                print(f"Stellar mass: {message_content.get('StellarMass', 'Unknown Stellar Mass')}")
                                position = message_content.get('StarPos')
                                print(f"Position: X: {position[0]}, Y: {position[1]}, Z: {position[2]}")
                                print(f"----------------------------------------------------------------")
                                # Add the system to the set and append to the file
                                discovered_systems.add(system_name)
                                with open(discovered_systems_file, "a") as f:
                                    f.write(system_name + "\n")
                                # Save the JSON object for this system
                                discovered_systems_json[system_name] = message
                                with open(discovered_systems_json_file, "w") as f:
                                    json.dump(discovered_systems_json, f, indent=2)

                    elif args.docking:
                        docking_events = [
                            "DockingCancelled", 
                            "DockingDenied", 
                            "DockingGranted", 
                            "DockingRequested", 
                            "DockingTimeout"
                        ]

                        if event in docking_events:
                            station_name = message_content.get('StationName', 'Unknown Station')
                            
                            if event == "DockingGranted":
                                landing_pad = message_content.get('LandingPad', 'N/A')
                                print(f"Docking granted on landing pad {landing_pad} at {station_name}.")
                            elif event == "DockingDenied":
                                reason = message_content.get('Reason', 'No reason specified')
                                print(f"Docking denied at {station_name}. Reason: {reason}")
                            elif event == "DockingRequested":
                                print(f"Docking requested at {station_name}.")
                            elif event == "DockingCancelled":
                                print(f"Docking cancelled at {station_name}.")
                            elif event == "DockingTimeout":
                                print(f"Docking request at {station_name} timed out.")
                    else:
                        # Default behavior: print all messages
                        print(json.dumps(message, indent=2))

            except zmq.Again:
                print("No message received in the last 10 minutes. Still listening...")
                # If you want the script to exit on timeout, you can break here.
                # For now, it will just keep listening.

    except KeyboardInterrupt:
        print("\nDisconnecting from EDDN.")
    finally:
        subscriber.close()
        context.term()
        print("Connection closed.")

if __name__ == "__main__":
    main() 