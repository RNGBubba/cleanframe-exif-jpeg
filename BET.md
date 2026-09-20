# CleanFrame EXIF

Offer: a local, dependency-light command-line tool that strips EXIF metadata from JPEGs before sharing.

Price: free/open-source; optional support or custom packaging can be offered later without requiring a hosted service.

30-day path: publish the new public repository, document the one-command workflow, and share it with privacy-conscious developers and photographers through useful technical discussions (no spam or fake reviews).

Human click: a user must choose and run the command locally; no credentials, network service, or automatic upload is involved.

GitHub: https://github.com/RNGBubba/cleanframe-exif-jpeg

Artifact: `cleanframe/cli.py` with pytest regression coverage in `tests/test_cli.py`.

Security behavior: only JPEG input is accepted; EXIF is not copied; existing destinations require `--force`; destination symlinks and same-file input/output are rejected; output is written atomically through a temporary file.
