# Build rlocker-nginx image

In the repository root:
```
source venv/bin/activate
export DJANGO_SECRET='....'
python manage.py collectstatic --noinput
deactivate
```

In the `nginx` directory:

```
podman login quay.io...

export TAG=2026-03-25a

podman build --tag rlocker-nginx:${TAG} -f ./Dockerfile

podman tag rlocker-nginx:${TAG} quay.io/ocsci/rlocker-nginx:${TAG}

podman push rlocker-nginx:${TAG} quay.io/ocsci/rlocker-nginx:${TAG}
```


# tags
## 2026-03-25a - django5 update

## 2026-03-24a - updated
