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

export TAG=2026-07-08a

podman build --tag rlocker-nginx:${TAG} -f ./Dockerfile

podman tag rlocker-nginx:${TAG} quay.io/ocsci/rlocker-nginx:${TAG}

podman push rlocker-nginx:${TAG} quay.io/ocsci/rlocker-nginx:${TAG}
```


# tags

## 2026-07-08a - update system packages to fix various CVEs

## 2026-04-23 - PR#86 Disable niceScroll on html

## 2026-03-25a - django5 update

## 2026-03-24a - updated
