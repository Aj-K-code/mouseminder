## Installation

### Prerequisites

-   Python 3.7 or higher
-   `pip` (Python package installer)

### Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/mouseminder.git
    cd mouseminder
    ```

2.  **(Optional but recommended) Create a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application with Python:

```bash
python mouseminder.py
```

The application will start monitoring your mouse movements in the background. An icon might appear in your system tray or a small window might open to indicate it's running.

To stop the application, you can usually close the window or use `Ctrl+C` in the terminal where it's running (if it's running in the foreground).