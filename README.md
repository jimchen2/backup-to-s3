## Build

```
docker build --no-cache -t jimchen2/backup-mongo-github .
```

## Start

Configure `env`

```
docker run -d --restart always --env-file .env jimchen2/backup-mongo-github:latest
```

1. Every shallow backup shall be removed on a next full backup.
2. Every full backup shall be put into a prefix /full folder in the bucket
3. Bucket shall follow hierarchy yy/mm/dd/hhmmss
4. Schedule a background job to repeatedly trigger these 2 functions.
