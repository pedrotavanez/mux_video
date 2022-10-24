# Touchstream <-> Mux Video API

Inside video/helpers there's a config file, it contains the API keys for Touchstream and Mux, you will only need to update the Mux API credentials, I've done the TS part for you.

```
mux_token_id = ""
mux_secret = (
        ""
    )
```

Then you will need to update the mapping between Touchstream Channels and Mux Live streams/Assets

```
options["mapping"] = {
    "Touchstream e2e Path": "Mux Live Stream ID",
    "f0258b6685684c113bad94d91b8fa02a": "KAKGCRT3zSBTs6IK004dxJ3pp82FxdBXJUQ3aTxmWFxQ"
}
```
The key should be the Touchstream Channel Key (obtainable from Admin menu or by right-clicking in the Touchstream End-To-End Tiles)

Once you have it all
```
pip3 install -r requirements.txt
python3 video/live.py
```