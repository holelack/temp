#include <bits/stdc++.h>
using namespace std;
const int MAX = 17, INF = 1e9;
int N, M;
vector<vector<int>> adj;
vector<vector<int>> edge;
vector<vector<int>> dist; //. table
vector<vector<int>> parent; // table
vector<int> level;

void initTree(int v, int p) {
    if (p == -1) level[v] = 0;
    else level[v] = level[p] + 1;
    parent[v][0] = p;
    for (int i = 0; i < adj[v].size(); i++) {
        int nv = adj[v][i];
        if (nv == p) continue;
        dist[v][0] = edge[v][i];
        initTree(nv, v);
    }
}

void getTable() {
    for (int depth = MAX; depth >= 1; depth--) {
        for (int node = 0; node < N; node++) {
            parent[node][depth] = parent[parent[node][depth-1]][depth-1];
            dist[node][depth] = dist[node][depth-1] + dist[parent[node][depth-1]][depth-1];
        }
    }
}

pair<int,int> lca(int& a, int& b) {
    int res = 0;
    if (level[a] > level[b]) swap(a,b);
    if (level[a] != level[b] ) {
        for (int depth = MAX; depth >= 0; depth--) {
            if (parent[b][depth] == -1) continue;
            if (level[a] <= level[parent[b][depth]]) {
                res += dist[b][depth];
                b = parent[b][depth];
            }
        }
    }

    int ret;
    if (a != b) {
        for (int depth = MAX; depth >= 0; depth--) {
            if (parent[a][depth] != parent[b][depth]) {
                res += dist[a][depth];
                a = parent[a][depth];
                res += dist[b][depth];
                b= parent[b][depth];
            } else {
                res += dist[a][depth] + dist[b][depth];
                ret = parent[a][depth];
            }
        }
    }
    return make_pair(ret, res);
}

int KthNode(int a, int b, int k) {
    int cnt = 0;
    if (level[a] >= k) {
        for (int depth = MAX; depth >= 0; depth--) {
            if (cnt + (1<<depth) <= k) a = parent[a][depth];
        }
    }
    else cnt = KthNode(lca(a,b).first, b, k-cnt);
}

int main() {
    cin >> N;
    adj.resize(N);
    edge.resize(N);
    dist.assign(N, vector<int>(MAx+1, INF));
    parent.assign(N, vector<int>(MAX+1, -1));
    level.resize(N);
    for (int i = 0; i < N; i++) {
        int a,b,w;
        adj[a].emplace_back(b);
        adj[b].emplace_back(a);
        edge[a].emplace_back(w);
        edge[b].emplace_back(w);
    }
    initTree(0, -1);
    getTable();

    cin >> M;
    int cmd, u, v, k;
    for (int i = 0; i < M; i++) {
        cin >> cmd;
        if (cmd == 1) {
            cin >> u >> v;
            cout << 
        }
    }
    

    return 0;
}
