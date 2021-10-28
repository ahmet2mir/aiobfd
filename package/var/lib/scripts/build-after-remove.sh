#!/bin/bash
if [ "$1" == "0" ]; then
   getent passwd aiobfd && userdel -f aiobfd
fi

exit 0
