## Configuration

MouseMinder can be configured using a `config.json` file located in the project root directory. If this file is not present, default settings will be used.

### Default Configuration

If no `config.json` is found, the following defaults will be used:

```json
{
  "sensitivity": "medium",
  "timeouts": {
    "short": 5,
    "long": 15
  },
  "messages": [
    "Chill out!",
    "Focus, padawan!",
    "Stop the wiggle!",
    "Productivity police: You're under arrest!"
  ],
  "enable_sound": false,
  "whitelist": []
}
```

### Configuration Options

-   `sensitivity` (string): Adjusts how easily fidgeting is detected. Options: `"low"`, `"medium"`, `"high"`.
-   `timeouts` (object): Duration of timeouts in seconds.
    -   `short` (integer): Duration of the short timeout.
    -   `long` (integer): Duration of the long timeout.
-   `messages` (array of strings): List of humorous messages displayed by the emoji.
-   `enable_sound` (boolean): Enable or disable sound effects during timeout.
-   `whitelist` (array of strings): List of application window titles or process names where MouseMinder will be inactive.

### Creating a Custom Configuration

1.  Create a file named `config.json` in the project root directory.
2.  Copy the default configuration above into the file.
3.  Modify the values according to your preferences.
4.  Save the file and restart MouseMinder.

Example `config.json` for high sensitivity and longer timeouts:

```json
{
  "sensitivity": "high",
  "timeouts": {
    "short": 10,
    "long": 30
  },
  "messages": [
    "ENOUGH!",
    "Control yourself!",
    "The mouse is not a toy!"
  ],
  "enable_sound": true,
  "whitelist": ["Steam", "Blender"]
}
```