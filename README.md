# MouseMinder

A fun tool to help you stop fidgeting with your mouse. If you move your mouse too much without clicking, MouseMinder will give you a playful warning and repeatedly drag your cursor towards the center of the screen for a timeout, showing a random emoji as feedback.

## Features

-   Detects excessive mouse movement without clicking.
-   Shows a humorous emoji indicator in the console.
-   Repeatedly drags the mouse cursor towards the center of the screen during timeout.
-   Tiered timeout system (warning, short lock, long lock).
-   Customizable sensitivity, timeout durations, and messages via `config.json`.
-   Cross-platform support (Windows, macOS, Linux).

## Installation & Usage

### Prerequisites

-   Python 3.7 or higher
-   `pynput` library (for mouse/keyboard monitoring)

### Steps

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/mouseminder.git
    cd mouseminder
    ```

2.  **(Recommended) Create a virtual environment:**

    ```bash
    python3 -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install pynput
    ```
    
    Note: On some Linux systems, you might need to use `pip install --user pynput` or `pip install --break-system-packages pynput` if you encounter permission issues.

4.  **Run the application:**

    ```bash
    python3 mouseminder.py
    ```

    The application will start monitoring your mouse movements. 
    - An emoji indicator will appear in the console when fidgeting is detected.
    - After two offenses, it will drag your mouse to the center for a short timeout.
    - After three offenses, it will drag your mouse to the center for a longer timeout.

To stop the application, use `Ctrl+C` in the terminal where it's running.

## Configuration

You can customize MouseMinder's behavior by editing the `config.json` file:

-   Adjust sensitivity (`low`, `medium`, `high`)
-   Set timeout durations (in seconds)
-   Customize messages displayed in pop-ups
-   Enable/disable sound effects (not yet implemented)
-   Add applications to a whitelist (not yet implemented)

See `config.json` for the default settings and `docs/CONFIGURATION.md` for more details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.