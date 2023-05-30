# ale to Resolve CSV

This converts an ALE file from an alexa to a CSV that will bring in more Metadata than Resolve sees in the MXF files.

I mainly wrote it because Resolve was not seeing the sensor FPS for off speed shots. Then I had it fix the Camera #, as the production I am working on has a \_ after the camera number.

Then the filenames weren't matching, as I was getting HDE versions, and the HDE has a \_h instead of \_a in the filename. So this will detect which version it is, and make the filenames match, if the MXF files are in the same folder as the ALE.

## Usage

```bash
./ale2ResolveCSV <AleFile.ale> <Optional destination CSV file.csv>
```

If there is no destination specified, it will put a CSV on your desktop.

This has only been tested on a mac running Python 3.11.3

I used the decode of the ALE from https://gist.github.com/simonwagner/0ca407314bea9862ce6b15903fdcca87
