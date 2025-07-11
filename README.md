# EDDN Watcher

A simple Python-based command-line tool to connect to the Elite Dangerous Data Network (EDDN) and monitor the live data feed in your terminal.

## Description

This tool connects to the EDDN's ZeroMQ relay to stream real-time game events. It can display all incoming messages or be configured to filter for specific event types, such as new system discoveries or station docking events.

## Setup Instructions

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/dbarkman/EDDN_Watcher.git
    cd EDDN_Watcher
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *On Windows, use `venv\Scripts\activate`*

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run the script with several optional flags to filter the EDDN feed.

*   **Show all messages (default):**
    ```bash
    python eddn_watcher.py
    ```

*   **Show only exploration and FSS/DSS events:**
    ```bash
    python eddn_watcher.py --exploration
    ```

*   **Show only newly discovered systems:**
    This mode will track and display only systems that are being discovered for the first time, saving a local log file of discovered systems, called discovered_systems.json.
    ```bash
    python eddn_watcher.py --new-systems
    ```

*   **Show only docking events:**
    ```bash
    python eddn_watcher.py --docking
    ``` 