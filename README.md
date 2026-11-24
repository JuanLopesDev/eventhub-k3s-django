# EventHub - Django no K3s

CRUD de eventos para a atividade **Implantação de Aplicação Django em Kubernetes com K3s**. Além do CRUD pedido para o projeto, há um cadastro e uma consulta de contatos (nome, e-mail e mensagem), que atende literalmente ao formulário solicitado no enunciado.

## Requisitos do enunciado atendidos

| Exigência | Implementação |
|---|---|
| 2 VMs Azure, rede privada | `k3s-server` (VM1) + `k3s-agent` (VM2); instruções abaixo |
| Control Plane sem app | K3s mantém o taint do servidor; manifests ainda usam `nodeSelector: workload=true` |
| Django + MySQL | Aplicação Django, `mysql:8.4`, Service `mysql-service` |
| Form nome, e-mail, mensagem | `/contatos/novo/` e `/contatos/` |
| Consulta de registros | Lista de contatos e lista/pesquisa de eventos |
| Imagem publicada no Docker Hub | passo `docker push` abaixo |
| Deployment Django/MySQL | `k8s/03-mysql.yaml`, `k8s/04-django.yaml` |
| NodePort 30080 | Service `django-service` |
| ClusterIP 3306 | Service `mysql-service` |
| PV/PVC MySQL | `k8s/02-mysql-storage.yaml` |
| Persistência | PV `hostPath` de 5 GiB, com política `Retain` |
| Escala e resiliência | roteiro de evidências abaixo |

## Arquitetura

```text
Internet -> IP público VM2:30080 -> django-service (NodePort)
                                      -> 1..3 Pods Django -> mysql-service:3306 (ClusterIP)
                                                               -> Pod MySQL -> PVC -> PV (/opt/k3s-data/mysql)

VM1: K3s Server / Control Plane, somente gerenciamento
VM2: K3s Agent / Worker, rótulo workload=true, todos os Pods da aplicação
```

## Execução local com Docker

Instale Docker Desktop e, na raiz do projeto, execute:

```powershell
docker compose up --build
```

Abra `http://localhost:8000`. Para interromper, use `docker compose down`. Para apagar também os dados locais de teste, use `docker compose down -v` (ação destrutiva apenas no volume local).

### Publicação no Docker Hub

Substitua `SEU_USUARIO` pelo usuário Docker Hub. Não publique segredos.

```powershell
docker login
docker buildx build --platform linux/arm64 -t juanlopess/eventos-django:1.0.0 --push .
```

O comando publica diretamente a imagem ARM64 no Docker Hub. Isso é necessário porque as VMs Azure deste projeto usam arquitetura ARM64. O manifesto `k8s/04-django.yaml` já aponta para `juanlopess/eventos-django:1.0.0`.

## Azure for Students: infraestrutura econômica

Recomendação técnica (o PDF não especifica SKU): use **Ubuntu Server 22.04 LTS Gen2**, região mais próxima, e `Standard_B2s` em cada VM (2 vCPU, 4 GiB RAM). É uma escolha viável para K3s + MySQL no worker; desligue/desaloque as VMs quando não estiver usando os créditos. Se o crédito não comportar duas B2s, teste B1s, mas 1 GiB no worker é apertado para MySQL e 3 réplicas.

No Azure Portal:

1. Crie um Resource Group, por exemplo `rg-k3s-eventos`.
2. Crie uma VNet, por exemplo `vnet-k3s`, com subnet `10.10.0.0/24`.
3. Crie `vm1-k3s-control` e `vm2-k3s-worker` na mesma VNet/subnet, ambas com a imagem Ubuntu Server 22.04 LTS Gen2 e autenticação por chave SSH. Um disco Standard SSD de 30 GiB basta para o laboratório.
4. Mantenha IP público nas duas VMs para SSH, mas restrinja a regra TCP 22 do NSG ao **seu IP público**. Na VM2, adicione regra de entrada TCP `30080`, também limitada ao seu IP durante o teste. Não exponha 3306 nem 6443 à Internet.
5. Os IPs privados da VNet são usados para a comunicação entre os nós. Permita dentro da VNet TCP 6443, 10250 e UDP 8472 (Flannel VXLAN); a regra padrão `VirtualNetwork` geralmente já cobre isso.

Conecte-se, substituindo IP e usuário definidos no Portal:

```powershell
ssh azureuser@IP_PUBLICO_VM1
ssh azureuser@IP_PUBLICO_VM2
```

## Instalação do K3s

> Execute cada comando na máquina indicada. K3s já instala e configura seu runtime `containerd`, kubectl e kubelet internamente; portanto, **não** instale kubeadm/kubelet/kubectl separadamente. Isso segue a tecnologia explicitamente exigida pelo PDF.

### VM1 - Control Plane

```bash
sudo apt update && sudo apt upgrade -y
curl -sfL https://get.k3s.io | sh -s - server --node-name vm1-k3s-control --write-kubeconfig-mode 644 --node-taint node-role.kubernetes.io/control-plane=true:NoSchedule
sudo kubectl get nodes
sudo cat /var/lib/rancher/k3s/server/node-token
```

Anote o token exibido e o IP **privado** da VM1 (`hostname -I`).

### VM2 - Worker

```bash
sudo apt update && sudo apt upgrade -y
curl -sfL https://get.k3s.io | K3S_URL=https://IP_PRIVADO_VM1:6443 K3S_TOKEN=TOKEN_DA_VM1 sh -
```

Volte à VM1 e valide/rotule o Worker. Não remova o taint do Control Plane: isto impede Pods da aplicação nele.

```bash
sudo kubectl get nodes -o wide
sudo kubectl label node vm2-k3s-worker workload=true
sudo kubectl describe node vm1-k3s-control | grep -A2 Taints
```

## Implantação no cluster

Na sua máquina, copie os manifests para a VM1 (`scp -r k8s azureuser@IP_VM1:~/`) ou clone o repositório GitHub nela. Na VM1:

```bash
cd ~/k8s
cp 01-secret.example.yaml 01-secret.yaml
nano 01-secret.yaml                 # crie senhas/SECRET_KEY exclusivos; não envie ao Git
sudo kubectl apply -f 00-namespace.yaml
sudo kubectl apply -f 01-secret.yaml
sudo kubectl apply -f 02-mysql-storage.yaml
sudo kubectl apply -f 03-mysql.yaml
sudo kubectl apply -f 04-django.yaml
sudo kubectl -n eventos get nodes,pods,services,pv,pvc -o wide
```

O PV `hostPath` só deve ser usado neste laboratório de nó único de trabalho: ele grava no disco da VM2. Em produção, a recomendação técnica seria Azure Disk CSI ou Azure Files, mas isso não é necessário para a arquitetura didática do PDF.

Abra `http://IP_PUBLICO_VM2:30080`. A dashboard mostra o hostname do Pod que atendeu a requisição, evidenciando o balanceamento quando houver réplicas.

## Roteiro de testes e evidências para entrega

Faça capturas de tela/terminal de cada item, incluindo data e o endereço da aplicação quando possível.

```bash
# 1. nós, Pods e Services solicitados explicitamente
sudo kubectl -n eventos get nodes,pods,services -o wide

# 2. confirmar que ambos os workloads ficaram no Worker
sudo kubectl -n eventos get pods -o wide

# 3. registrar e consultar dados no navegador
# Acesse http://IP_PUBLICO_VM2:30080/contatos/novo/ e /contatos/

# 4. persistência: anote um registro, reinicie o Pod e confira no navegador
sudo kubectl -n eventos delete pod -l app=mysql
sudo kubectl -n eventos get pods -w

# 5. escalar Django, atualizar diversas vezes e observar HOSTNAME na dashboard
sudo kubectl -n eventos scale deployment django --replicas=3
sudo kubectl -n eventos get pods -o wide

# 6. autorrecuperação: substitua pelo nome de um Pod Django
sudo kubectl -n eventos delete pod NOME_DO_POD_DJANGO
sudo kubectl -n eventos get pods -w

# 7. retornar ao estado inicial
sudo kubectl -n eventos scale deployment django --replicas=1
```

Entregue: código-fonte, Dockerfile, manifests YAML, print da aplicação/cadastro/consulta, persistência antes/depois do reinício, `kubectl get nodes,pods,services -o wide`, desenho da arquitetura deste README e a URL/print da imagem no Docker Hub. Cada integrante deve seguir o procedimento individual de envio definido pelo professor.

## Segurança e manutenção

- `01-secret.yaml` é deliberadamente ignorado pelo Git; aplique-o no cluster sem versionar credenciais.
- Para gerar uma chave Django: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.
- Em produção, use `DEBUG=False`, hosts explícitos, HTTPS e um armazenamento CSI; este repositório é orientado ao laboratório acadêmico.

## Autores

- Juan Lopes Silverio
- Marcelo Henrique Costa
