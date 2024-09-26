# radio-playlist
Create a Spotify playlist from a local radio station.

For more information, see my [blog post](http://www.acjensen.com/radio-playlist/).

### Prerequisites

1. Create a file "secret.py" with client secrets for ARC cloud recognizer and Spotify
  ```python
  from dataclasses import dataclass

  @dataclass
  class ARC:
      access_key = "82640bba7076975b5fcaf79d00795d16"
      access_secret = "JaLNPFDhjQbAuJyQKU8HfU6xZU2YzwzTFFiPH3Z7"

  @dataclass
  class Spotify:
      client_id = "10432503769b49b99aecc7acf15c1821"
      client_secret = "a1c5ce5b2d80496f91ed6210182bbff2"
  ```
2. Update `radio_playlist.py` with your own radio stream URL and public spotify playlist ID.

### Install dependencies

```sh
pip3 install -r requirements.txt
```

### Run the script

```sh
python3 radio_playlist.py
```