Docker:

Every shallow backup shall be removed on a next full backup.

Every full backup shall be put into a prefix /full folder in the bucket

Bucket shall follow hierarchy yy/mm/dd/hhmmss

Schedule a background job to repeatedly trigger these 2 functions.
