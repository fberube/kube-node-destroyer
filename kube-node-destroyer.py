#!/usr/bin/env python
import sys
import getopt
import ovh
import pprint

def new_ovh_client():
    return ovh.Client(
        endpoint='ovh-eu',
        application_key='xxxx',
        application_secret='xxxx',
        consumer_key='xxxx'
    )

def get_project(ovhClient):
    return ovhClient.get('/cloud/project')

def get_project_properties(ovhClient, projectId):
    return ovhClient.get(f'/cloud/project/{projectId}')

def get_kube_cluster(ovhClient, projectId):
    return ovhClient.get(f'/cloud/project/{projectId}/kube')

def get_kube_cluster_properties(ovhClient, projectId, kubeId):
    return ovhClient.get(f'/cloud/project/{projectId}/kube/{kubeId}')

def get_kube_cluster_nodes(ovhClient, projectId, kubeId):
    return ovhClient.get(f'/cloud/project/{projectId}/kube/{kubeId}/node')

def delete_kube_cluster_node(ovhClient, projectId, kubeId, nodeId):
    ovhClient.delete(f'/cloud/project/{projectId}/kube/{kubeId}/node/{nodeId}')

def _post_process_opts(opts):
    d = dict()
    if opts is None:
        return d
    for item in opts:
        d[item[0]] = item[1]
    return d

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # default dryRun
    dryRun = True
    inParams = dict()
    # get opts
    try:
        opts, args = getopt.getopt(argv[1:], "w")
        inParams = _post_process_opts(opts)
    except getopt.GetoptError as optErr:
        pass
    if "-w" in inParams:
        dryRun = False

    # end get opts
    ovhClient = new_ovh_client()
    try:
        # get project
        for projectId in get_project(ovhClient):
            pInfo = get_project_properties(ovhClient, projectId)
            print("""[project] {0} ({1})""".format(pInfo['description'], projectId))
            for kubeId in get_kube_cluster(ovhClient, projectId):
                kInfo = get_kube_cluster_properties(ovhClient, projectId, kubeId)
                print("""[kube] {0} (projectId={1},kubeId={2})""".format(kInfo['name'], projectId, kubeId))
                if ( kInfo['name'] == 'Production' ):
                    print("""[SKIPPING] kube [{0}] (projectId={1},kubeId={2})""".
                        format(kInfo['name'], projectId, kubeId))
                    continue
                # get nodes
                for kubeNode in get_kube_cluster_nodes(ovhClient, projectId, kubeId):
                    if dryRun:
                        print("""[node] about to delete [{0}] (projectId={1},kubeId={2},nodeId={3})""".
                            format(kubeNode['name'], projectId, kubeId, kubeNode['id']))
                        continue
                    try:
                        print("""[node] deleting [{0}] (projectId={1},kubeId={2},nodeId={3})""".
                            format(kubeNode['name'], projectId, kubeId, kubeNode['id']))
                        delete_kube_cluster_node(ovhClient, projectId, kubeId, kubeNode['id'])
                    except ovh.exceptions.APIError as err:
                        print(err)
                        return 2
                    return 0

    except ovh.exceptions.APIError as err:
        print(err)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
