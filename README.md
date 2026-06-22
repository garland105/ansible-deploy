# PG16 HA + Prometheus 全栈监控 — Ansible 自动化部署框架

一键部署 PostgreSQL 16 双机高可用集群 + Prometheus/Grafana 全栈监控 + 钉钉告警。

## 用法

```bash
# 1. 改 3 个文件（见下方说明）
# 2. 一条命令部署
ansible-playbook -i inventory.yml site.yml

# 或分步部署
ansible-playbook -i inventory.yml common.yml        # 系统初始化
ansible-playbook -i inventory.yml pg-patroni.yml    # PG 高可用
ansible-playbook -i inventory.yml monitoring.yml    # 监控栈
ansible-playbook -i inventory.yml alerting.yml      # 告警 + HA
```

## 部署前必须改的文件

每次部署到新环境，以下 3 个文件必须按实际情况修改：

### 1. `inventory.yml` — 主机清单

```yaml
physical:                     # 第一台机器（PG Leader）
  hosts:
    server:
      ansible_host: 192.168.1.51     # ← 改 IP
      ansible_user: a                # ← 改 SSH 用户名
      ansible_ssh_pass: '1'          # ← 改 SSH 密码
      physical_ip: 192.168.1.51      # ← 改物理机真实 IP

vm:                           # 第二台机器（PG Replica + 监控中心）
  hosts:
    vm-host:
      ansible_host: 192.168.1.46     # ← 改 IP
      ansible_user: root             # ← 改 SSH 用户名
      ansible_ssh_pass: '1'          # ← 改 SSH 密码
```

### 2. `group_vars/all.yml` — 全局变量

```yaml
# --- 必须改的 ---
pg_admin_password: admin_pass      # PG 超级用户密码
pg_repl_password: repl_pass        # PG 复制用户密码
monitor_password: monitor          # PG 监控用户密码
grafana_admin_password: admin123   # Grafana 管理员密码
dingtalk_token: ""                 # 钉钉机器人 token（留空不启用）

# --- 按需改的 ---
pg_vip: 192.168.1.200              # PG 虚拟 IP（Keepalived 用）
physical_interface: ""             # 物理机网卡（留空自动检测）
download_mirror: "https://ghp.ci/" # GitHub 下载镜像（国内加速）
```

### 3. `group_vars/physical.yml` — 物理机变量

```yaml
physical_hostname: server           # 主机名
keepalived_interface: "eth0"        # 网卡名（如果自动检测失败）
```

## 部署后的功能

| 功能 | 验证方式 |
|------|---------|
| PG 双机主从 | `patronictl -c /etc/patroni/ha.yml list` |
| 自动故障切换 | 关掉 Leader 的 PG，Replica 30 秒内升为 Leader |
| Grafana 仪表盘 | `http://VM_IP:3000`（3 张 Dashboard） |
| Prometheus 指标 | `http://VM_IP:9090/classic/targets` |
| 钉钉告警 | 触发一条告警规则，钉钉群收到通知 |
| Keepalived VIP | `ip a | grep <VIP>` 查看 VIP 在哪台机器 |

## 前置条件

- 两台空白 **Ubuntu 24.04 Server**（最小安装即可）
- 两台机器网络互通（同网段）
- 一台机器上装了 **Ansible**（或在控制节点上装）
- 控制节点能 SSH 密码登录目标机器

## 文件结构

```
ansible-deploy/
├── install_ansible.sh          # 控制节点初始化脚本
├── inventory.yml                # ← 主机清单（每次部署改）
├── site.yml                     # 入口：一键部署全部
├── common.yml                   # 系统初始化
├── pg-patroni.yml               # PG 高可用
├── monitoring.yml               # 监控栈
├── alerting.yml                 # 告警 + HA
└── group_vars/
    ├── all.yml                  # ← 全局变量（每次部署改）
    ├── physical.yml             # ← 物理机变量
    └── vm.yml                   # VM 变量
```

## 组件版本

| 组件 | 版本 | 安装方式 |
|------|------|---------|
| PostgreSQL | 16 | apt |
| Patroni | 4.1.3 | VM: apt / 物理机: venv |
| etcd | 3.4.36 | snap |
| Prometheus | 2.55.1 | 二进制 |
| Grafana | 11.5.1 | deb |
| Alertmanager | 0.27.0 | 二进制 |
| Node Exporter | 1.8.2 | 二进制 |
| PG Exporter | 0.15.0 | 二进制 |
| Blackbox Exporter | 0.25.0 | 二进制 |
