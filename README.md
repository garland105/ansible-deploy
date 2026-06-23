# PG16 HA + Prometheus 全栈监控 — Ansible 自动化部署框架

一键部署 PostgreSQL 16 双机高可用集群 + Prometheus/Grafana 全栈监控 + 钉钉告警。

**关键规则：剧本本身的代码（`roles/*`）不改，所有环境配置都在 `inventory.yml` 和 `group_vars/` 里改。**

## 部署前必须改的文件

每次部署到新环境，以下文件必须按实际情况修改。

### 1. `inventory.yml` — 主机清单

**修改：IP 地址与 SSH 用户**

```bash
nano inventory.yml
```

将以下值改为当前环境的实际值：

```yaml
physical:
  hosts:
    server:
      ansible_host: 192.168.1.51     # ← 改为 Leader 机器 IP
      ansible_user: a                # ← 改为 SSH 用户名
      physical_ip: 192.168.1.51      # ← 改为 Leader 机器真实 IP

vm:
  hosts:
    vm-host:
      ansible_host: 192.168.1.46     # ← 改为 Replica 机器 IP
      ansible_user: root             # ← 改为 SSH 用户名
```

### 2. `group_vars/all.yml` — 全局配置变量

**修改：密码、Token、虚拟 IP、网段**

```bash
nano group_vars/all.yml
```

#### 必须改的（密码/Token）

| 变量 | 说明 | 改为什么 |
|------|------|---------|
| `pg_admin_password` | PG 超级用户密码 | 设一个强密码 |
| `pg_repl_password` | PG 复制用户密码 | 设一个强密码 |
| `monitor_password` | PG 监控用户密码 | 设一个密码 |
| `postgres_password` | postgres 系统用户密码 | 设一个密码 |
| `grafana_admin_password` | Grafana 管理员密码 | 设一个密码 |
| `dingtalk_token` | 钉钉机器人 token | 填入真实 token（留空则不发告警） |

示例：
```yaml
pg_admin_password: MyStr0ng!Pass
pg_repl_password: ReplP@ss2024
monitor_password: m0n1t0r
postgres_password: p0stgr3s
grafana_admin_password: Gr@fana2024
dingtalk_token: "你的钉钉机器人token"
```

#### 按实际网络改的

| 变量 | 说明 | 改为什么 |
|------|------|---------|
| `pg_vip` | 虚拟 IP | 改为和机器同网段的空闲 IP |
| `pg_network_subnet` | PG 允许访问的内网网段 | 改为实际网段（如 `10.0.0.0/8`） |
| `keepalived_vrrp_id` | VRRP 路由器 ID（1-255） | 同网络内不能重复 |
| `keepalived_vrrp_pass` | Keepalived 认证密码 | 设一个密码 |
| `download_mirror` | GitHub 下载镜像 | 国内网络改成可用镜像 |

示例（NAT 模式 192.168.222.x 网段）：
```yaml
pg_vip: 192.168.222.200
pg_network_subnet: 192.168.0.0/16
keepalived_vrrp_id: 52
keepalived_vrrp_pass: my_vrrp_pass
```

### 3. `group_vars/physical.yml` — Leader 专用变量

```bash
nano group_vars/physical.yml
```

| 变量 | 说明 | 改为什么 |
|------|------|---------|
| `physical_hostname` | 物理机主机名 | 按需设置 |
| `patroni_data_dir` | PG 数据目录 | 默认即可，除非你要改路径 |

### 4. `group_vars/vm.yml` — Replica 专用变量

```bash
nano group_vars/vm.yml
```

| 变量 | 说明 | 改为什么 |
|------|------|---------|
| `vm_hostname` | VM 主机名 | 按需设置 |
| `patroni_data_dir` | PG 数据目录 | 默认即可 |

## 部署命令

```bash
# 完整部署
ansible-playbook -i inventory.yml site.yml

# 或分步部署（推荐，便于定位问题）
ansible-playbook -i inventory.yml common.yml        # 系统初始化
ansible-playbook -i inventory.yml pg-patroni.yml    # PG 高可用
ansible-playbook -i inventory.yml monitoring.yml    # 监控栈
ansible-playbook -i inventory.yml alerting.yml      # 告警 + HA
```

## 验证

| 功能 | 命令 |
|------|------|
| PG 集群状态 | `patronictl -c /etc/patroni/ha.yml list` |
| Grafana | `http://VM_IP:3000`（3 张预置 Dashboard） |
| Prometheus 目标 | `http://VM_IP:9090/targets`（6 个抓取目标） |
| 钉钉告警 | 停掉一个 Exporter，1 分钟后钉钉收到通知 |
| Keepalived VIP | `ip a \| grep <VIP>` |

## 前置条件

- 两台 **Ubuntu 24.04 Server**（已开启 SSH）
- 两台机器网络互通
- 控制节点（Replica 那台）装了 Ansible
- 控制节点能 SSH 免密登录目标机器（建议先配好 SSH key）

## 文件结构

```
ansible-deploy/
├── inventory.yml          # ← 主机清单（每次部署改）
├── site.yml               # 入口：一键部署全部
├── common.yml             # 系统初始化
├── pg-patroni.yml         # PG 高可用
├── monitoring.yml         # 监控栈
├── alerting.yml           # 告警 + HA
├── group_vars/
│   ├── all.yml            # ← 全局变量（密码/token/网段）
│   ├── physical.yml       # ← Leader 变量
│   └── vm.yml             # ← Replica 变量
└── roles/                 # 剧本代码（不改）
```
