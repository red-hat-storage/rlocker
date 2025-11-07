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

export TAG=test-01

podman build --tag rlocker-nginx:${TAG} -f ./Dockerfile

podman tag rlocker-nginx:${TAG} quay.io/ocsci/rlocker-nginx:${TAG}

podman push rlocker-nginx:${TAG} quay.io/ocsci/rlocker-nginx:${TAG}
```
