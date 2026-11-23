# Minikube Dev Pod with a Mounted Project Directory

Minikube runs in its own VM or container, so the pod can't see your files directly. The fix has two parts: mount your directory into the minikube node, then have the pod use that node path as a `hostPath` volume.

## 1. Pod file

Save this as `pod.yaml`. The mount path is fixed at `/mnt/workspace`, so no `envsubst` is needed.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: python-dev
  labels:
    app: python-dev
spec:
  containers:
    - name: python
      image: python:3.14-slim
      command: ["sh", "-c", "sleep infinity"]
      workingDir: /workspace
      stdin: true
      tty: true
      resources:
        requests:
          cpu: 250m
          memory: 256Mi
        limits:
          cpu: "1"
          memory: 2Gi
      volumeMounts:
        - name: workspace
          mountPath: /workspace
  volumes:
    - name: workspace
      hostPath:
        path: /mnt/workspace
        type: Directory
```

## 2. Mount your directory into minikube

Run this from your project directory, in its own terminal:

```sh
minikube mount "$PWD":/mnt/workspace
```

**Leave this command running.** The mount disappears when the process stops. Wait until it prints that it is mounting and serving files before continuing.

### Alternative: mount at cluster start

If you'd rather not keep a terminal open, mount when creating the cluster:

```sh
minikube start --mount --mount-string="$PWD:/mnt/workspace"
```

This is only applied at start, so for an existing cluster you'll need `minikube stop` and then run the command above, or `minikube delete` to recreate it.

## 3. Create the pod

In another terminal:

```sh
kubectl apply -f pod.yaml
kubectl wait --for=condition=Ready pod/python-dev
```

## 4. Verify the mount

```sh
kubectl exec python-dev -- ls /workspace
```

You should see your project files. To confirm it's a live two-way mount:

```sh
touch test.txt
kubectl exec python-dev -- ls /workspace/test.txt
```

## 5. Connect VS Code

- **Kubernetes extension:** right-click the pod, then choose **Attach Visual Studio Code**.
- **Dev Containers extension:** run **Dev Containers: Attach to Running Kubernetes Container**.

Then open `/workspace` in the attached window.

## 6. VENV
python -m venv ~/venvs/transformer
source ~/venvs/transformer/bin/activate.fish


## Troubleshooting

| Problem | Fix |
|---|---|
| Pod stuck in `ContainerCreating` with a `hostPath` error | The mount isn't running or the path is wrong. Check that `minikube mount` is still active and that `minikube ssh -- ls /mnt/workspace` shows your files. |
| Directory looks empty in the pod | Restart `minikube mount`, then delete and re-apply the pod. |
| Permission errors writing files | Re-run the mount with explicit ownership: `minikube mount --uid 0 --gid 0 "$PWD":/mnt/workspace` |
| Changes not showing up | Make sure you ran the mount from the intended directory, since `$PWD` is resolved when the command starts. |

## Cleanup

```sh
kubectl delete pod python-dev
```

Then stop the `minikube mount` process with `Ctrl+C`.