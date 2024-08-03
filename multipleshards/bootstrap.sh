# Conjunto 1: Criar a Estrutura de Pastas
mkdir -p apps/base
mkdir -p apps/controlplane/shard-1
mkdir -p apps/controlplane/shard-2
mkdir -p apps/controlplane2/shard-3
mkdir -p apps/controlplane2/shard-4
mkdir -p argocd/applications
mkdir -p .github/workflows

# Conjunto 2: Criar Arquivos Base do Kustomize

cat <<EOF > apps/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - helm-chart.yaml

generatorOptions:
  disableNameSuffixHash: true
EOF

cat <<EOF > apps/base/helm-chart.yaml
apiVersion: builtin
kind: HelmChartInflationGenerator
metadata:
  name: extratosvcs
helmGlobals:
  chartHome: "https://url-do-helm-chart-base"
helmCharts:
  - name: extratosvcs
    version: 1.0.0
    releaseName: extratosvcs
    valuesFile: values.yaml
EOF

cat <<EOF > apps/base/values.yaml
replicaCount: 1

image:
  repository: busybox
  pullPolicy: IfNotPresent
  tag: "latest"

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "1"

env:
  shard: "1"
  appName: "show-time"
  cluster: "default-cluster"
  appVersion: "1.0.0"
EOF

cat <<EOF > apps/base/show-time-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.env.appName }}-deployment
  labels:
    app: {{ .Values.env.appName }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.env.appName }}
  template:
    metadata:
      labels:
        app: {{ .Values.env.appName }}
    spec:
      containers:
      - name: {{ .Values.env.appName }}
        image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
        command: ["/bin/sh", "-c"]
        args: ["while true; do date; sleep 5; done"]
        resources:
          limits:
            cpu: {{ .Values.resources.limits.cpu }}
            memory: {{ .Values.resources.limits.memory }}
          requests:
            cpu: {{ .Values.resources.requests.cpu }}
            memory: {{ .Values.resources.requests.memory }}
        env:
        - name: SHARD
          value: {{ .Values.env.shard }}
        - name: APP_NAME
          value: {{ .Values.env.appName }}
        - name: CLUSTER
          value: {{ .Values.env.cluster }}
        - name: APP_VERSION
          value: {{ .Values.env.appVersion }}
      affinity:
        nodeAffinity: {{ toYaml .Values.nodeAffinity | indent 8 }}
EOF

# Conjunto 3: Criar Arquivos de Configuração por Shard
cat <<EOF > apps/controlplane/shard-1/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
patches:
  - values-onebox.yaml
  - values-normal.yaml
EOF

cat <<EOF > apps/controlplane/shard-1/values-onebox.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "1"
env:
  - name: SHARD
    value: "1"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "1"
  app: "show-time"
  cluster: "controlplane"
  version: "<appversion>"
EOF

cat <<EOF > apps/controlplane/shard-1/values-normal.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "1"
env:
  - name: SHARD
    value: "1"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "1"
  app: "show-time"
  cluster: "controlplane"
  version: "<appversion>"
EOF

# Conjunto 4: Criar Arquivos de Configuração para os Demais Shards
cat <<EOF > apps/controlplane/shard-2/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
patches:
  - values-onebox.yaml
  - values-normal.yaml
EOF

cat <<EOF > apps/controlplane/shard-2/values-onebox.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "2"
env:
  - name: SHARD
    value: "2"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "2"
  app: "show-time"
  cluster: "controlplane"
  version: "<appversion>"
EOF

cat <<EOF > apps/controlplane/shard-2/values-normal.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "2"
env:
  - name: SHARD
    value: "2"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "2"
  app: "show-time"
  cluster: "controlplane"
  version: "<appversion>"
EOF

cat <<EOF > apps/controlplane2/shard-3/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
patches:
  - values-onebox.yaml
  - values-normal.yaml
EOF

cat <<EOF > apps/controlplane2/shard-3/values-onebox.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "3"
env:
  - name: SHARD
    value: "3"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane2"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "3"
  app: "show-time"
  cluster: "controlplane2"
  version: "<appversion>"
EOF

cat <<EOF > apps/controlplane2/shard-3/values-normal.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "3"
env:
  - name: SHARD
    value: "3"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane2"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "3"
  app: "show-time"
  cluster: "controlplane2"
  version: "<appversion>"
EOF

cat <<EOF > apps/controlplane2/shard-4/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
  - ../../base
patches:
  - values-onebox.yaml
  - values-normal.yaml
EOF

cat <<EOF > apps/controlplane2/shard-4/values-onebox.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "4"
env:
  - name: SHARD
    value: "4"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane2"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "4"
  app: "show-time"
  cluster: "controlplane2"
  version: "<appversion>"
EOF

cat <<EOF > apps/controlplane2/shard-4/values-normal.yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
      - matchExpressions:
          - key: shard
            operator: In
            values:
              - "4"
env:
  - name: SHARD
    value: "4"
  - name: APP_NAME
    value: "show-time"
  - name: CLUSTER
    value: "controlplane2"
  - name: APP_VERSION
    value: "<appversion>"
labels:
  shard: "4"
  app: "show-time"
  cluster: "controlplane2"
  version: "<appversion>"
EOF

# Conjunto 5: Criar Arquivos do ArgoCD

cat <<EOF > argocd/app-of-apps.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app-of-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/sudopablosilva/mynewrepository'
    targetRevision: HEAD
    path: argocd/applications
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

cat <<EOF > argocd/applications/controlplane.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: controlplane
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/sudopablosilva/mynewrepository'
    targetRevision: HEAD
    path: apps/controlplane
  destination:
    server: 'https://controlplane-cluster-url'
    namespace: controlplane
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

cat <<EOF > argocd/applications/controlplane2.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: controlplane2
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/sudopablosilva/mynewrepository'
    targetRevision: HEAD
    path: apps/controlplane2
  destination:
    server: 'https://controlplane2-cluster-url'
    namespace: controlplane2
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

# Conjunto 6: Criar o GitHub Actions Workflow
cat <<EOF > .github/workflows/deployment.yaml
name: Deploy to Shards

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set app version
      run: echo "APP_VERSION=$(date +%Y%m%d%H%M%S)" >> $GITHUB_ENV

    - name: Deploy in sequence
      run: |
        shards=("1" "2" "3" "4")
        workloads=("onebox" "normal")
        clusters=("controlplane" "controlplane" "controlplane2" "controlplane2")

        for i in ${!shards[@]}; do
          shard=${shards[$i]}
          cluster=${clusters[$i]}

          for workload in ${workloads[@]}; do
            echo "Deploying to shard $shard ($workload) on cluster $cluster"

            kubectl apply -f argocd/applications/shard-${shard}-${workload}.yaml

            # Wait for rollout (using Argo Rollouts)
            kubectl argo rollouts get rollout extratosvcs -n extratoonline --watch

            # Check alarms
            # Adicione aqui a lógica para verificar o alarme composto

            # Bake time
            sleep 600
          done
        done
EOF
