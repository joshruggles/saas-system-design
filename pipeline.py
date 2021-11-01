from diagrams import Diagram, Edge
from diagrams.aws.compute import EKS
from diagrams.custom import Custom
from diagrams.onprem.ci import GitlabCI
from diagrams.onprem.client import Users
from diagrams.onprem.gitops import ArgoCD
from diagrams.saas.identity import Okta


with Diagram("Company SAAS Pipeline", show=False):

    # pipeline actions & endpoints
    argocd = ArgoCD("Argo-CD")
    client = Users("Clients")
    eks = EKS("Elastic Kubernetes Service")
    gitlabci = GitlabCI("Gitlab-CI")
    gitlabRegistry = GitlabCI("Gitlab-Registry")
    gitlabRunner = Custom("Gitlab Runners", "./resources/gitlab_runner.png")
    git_merge = Custom("Merge", "./resources/git_merge.png")
    saas_repo = Custom("SaaS Application Repository", "./resources/git_repository.png")
    saas_manifests_repo = Custom("SaaS Manifests Repository", "./resources/git_repository.png")


    # pipeline flows
    merge = client >> git_merge
    Application_Pipeline = merge >> Edge(label="SaaS application code\n i.e. Dockerfiles, gitlab-ci.yml, etc.\n ") >> \
        saas_repo >> Edge(label="Gitlab runners\n Webhooks\n ") >> gitlabci >> Edge(label="Build container images\n Tag container images\n ") >> \
        gitlabRunner >> Edge(label="Push container Images\n ") >> gitlabRegistry
    Infrastructure_Pipeline = merge >> Edge(label="SaaS infrastructure code\n i.e. helm code, kubernetes manifests, values.yaml etc.\n ") >> \
        saas_manifests_repo >> Edge(label="Update kubernetes manifest\n ")
    argocd >> Edge(label="Sync helm/manifests/values state with EKS\n ") << saas_manifests_repo
    eks << Edge(label="Deploy helm/manifests/vaules updates to EKS\n ") << argocd