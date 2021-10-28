#!/bin/bash
getent group aiobfd || groupadd -g 502 aiobfd
getent passwd aiobfd || useradd -d /var/lib/aiobfd --no-create-home -g 502 -u 502 aiobfd

exit 0
