# XFM Offload Model

This repository contains a model of XFM's conditional, random, and fallback
access mechanisms. It allows users to calculate the number of offloads
corresponding to each type for different memory system configurations.

Currently supported memory types include:
- [`DDR4 4GB 2400 MHz`]

[`xfm\_access\_model.py`] contains code to generate a figure of CPU Fallbacks
Conditional Accesses and Random Accesses for an XFM Accelerated Memory Module
supporting 3 Row Accesses or 5 Row accesses for each REF

- [`xfm\_access\_model.py`](./xfm_access_model.py) prints out the statistics
to the command line in addition to generating `XFM\_Access\_Distribution.png`
showing a visual distribution

# Running the script
```bash
python3 xfmaccess_model.py
```

## More information

For more information see our MICRO 2023 paper
