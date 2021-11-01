from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2Instance, EKS
from diagrams.aws.network import ALB, Route53HostedZone, VPC, VpnGateway
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.compute import Deployment, Pod, ReplicaSet
from diagrams.k8s.network import Ingress, Service
from diagrams.onprem.ci import GitlabCI
from diagrams.onprem.client import Users
from diagrams.onprem.gitops import ArgoCD
from diagrams.onprem.network import Consul
from diagrams.onprem.security import Vault
from diagrams.saas.identity import Okta


with Diagram("Company SAAS Cloud Infrastructure ", show=False):

    # eks cluster 1 (engineering tools)
    with Cluster("EKS-1"):
        albArgo = ALB("ALB-Argo-CD")
        albGitlab = ALB("ALB-Gitlab")
        eks = EKS("EKS")
        consul = Consul("Consul")
        vault = Vault("Vault")
        with Cluster("Namespace: argocd"):
            argocd = ArgoCD("Argo-CD")
        with Cluster("Namespace: gitlab"):
            gitlabci = GitlabCI("Gitlab-CI")
    
    # eks cluster 2 (saas development environment)
    with Cluster("EKS-2"):
        albDev = ALB("ALB-Dev")
        eks = EKS("EKS")
        consul = Consul("Consul")
        vault = Vault("Vault")
        with Cluster("Namespace: dev"):
            ingressDev = Ingress("sass.dev.company.com")
            network = ingressDev >> Service("Service")
            network >> [Pod("SAAS-Pod-1"),
                        Pod("SAAS-Pod-2"),
                        Pod("SAAS-Pod-3")] << ReplicaSet("Replica-Set") << Deployment("Deployment") << HPA("HPA")

    # eks cluster 3 (saas stage environment)
    with Cluster("EKS-3"):
        albStage = ALB("ALB-Stage")
        eks = EKS("EKS")
        consul = Consul("Consul")
        vault = Vault("Vault")
        with Cluster("Namespace: stage"):
            ingressStage = Ingress("saas.stage.company.com")
            network = ingressStage >> Service("Service")
            network >> [Pod("SAAS-Pod-1"),
                        Pod("SAAS-Pod-2"),
                        Pod("SAAS-Pod-3")] << ReplicaSet("Replica-Set") << Deployment("Deployment") << HPA("HPA")

    # eks cluster 4 (saas production environment)
    with Cluster("EKS-4"):
        albProd = ALB("ALB-Prod")
        eks = EKS("EKS")
        consul = Consul("Consul")
        vault = Vault("Vault")
        with Cluster("Namespace: prod"):
            ingressProd = Ingress("saas.prod.company.com")
            network = ingressProd >> Service("Service")
            network >> [Pod("SAAS-Pod-1"),
                        Pod("SAAS-Pod-2"),
                        Pod("SAAS-Pod-3")] << ReplicaSet("Replica-Set") << Deployment("Deployment") << HPA("HPA")

    # aws infrastructure
    authcicd = Okta("CI/CD Authentication")
    authvpn = Okta("VPN Authentication")
    client = Users("Clients")
    domainArgocd = Route53HostedZone("argocd.company.com")
    domainDev = Route53HostedZone("saas.dev.company.com")
    domainGitlab = Route53HostedZone("gitlab.company.com")
    domainProd = Route53HostedZone("saas.prod.company.com")
    domainStage = Route53HostedZone("saas.stage.company.com") 
    vpc = VPC("Virtual Private Network")
    vpn = VpnGateway("vpn.company.com")

    # infrastructure flows
    connect = client >> authvpn >> vpn >> vpc
    domaincicd = domainGitlab - domainArgocd
    pipeline = connect >> domaincicd >> [albGitlab, albArgo] >> authcicd >> [gitlabci, argocd]
    pipelineDev = pipeline >> albDev >> ingressDev
    pipelineStage = pipeline >> albStage >> ingressStage
    pipelineProd = pipeline >> albProd >> ingressProd
    vpcDev = connect >> domainDev >> albDev >> ingressDev
    vpcStage = connect >> domainStage >> albStage >> ingressStage
    vpcProd = connect >> domainProd >> albProd >> ingressProd