# Ansible Deployment Framework — Project Overview

## 文件统计
- **总数**: 36 个文件
- **角色**: 11 个 (common, postgres, etcd, patroni, node_exporter, pg_exporter, blackbox_exporter, prometheus, alertmanager, grafana, dingtalk, keepalived)
- **Playbook**: 5 个 (site.yml, common.yml, monitoring.yml, alerting.yml, pg-patroni.yml)

## 快速使用

### 1. 在 VM 46 上初始化 Ansible
```bash
bash ansible-deploy/install_ansible.sh
```

### 2. 编辑配置（3 个文件）
| 文件 | 改什么 |
|------|--------|
| `inventory.yml` | 两台目标机器的 IP + SSH 密码 |
| `group_vars/all.yml` | 数据库密码、Grafana 密码、钉钉 token |
| `group_vars/physical.yml` | 物理机网卡名（如自动检测失败） |

### 3. 部署
```bash
# 一键全部部署
ansible-playbook -i inventory.yml site.yml

# 或分步部署（推荐首次使用）
ansible-playbook -i inventory.yml common.yml          # 系统初始化
ansible-playbook -i inventory.yml monitoring.yml        # 监控栈
ansible-playbook -i inventory.yml alerting.yml          # 告警+HA
```

## 部署后的成果

| 组件 | 部署在哪 | 访问方式 |
|------|---------|---------|
| PG16 + Patroni 高可用 | 两台机器 | `patronictl -c /etc/patroni/ha.yml list` |
| Prometheus | VM | `http://VM_IP:9090/classic/targets` |
| Grafana + 3 张 Dashboard | VM | `http://VM_IP:3000` (admin/你设的密码) |
| Alertmanager | VM | `http://VM_IP:9093` |
| Node Exporter | 两台机器 | `:9100` |
| PG Exporter | 两台机器 | `:9187` |
| Keepalived PG VIP | 两台机器 | VIP 自动指向 Leader |

## 可带走的部分
✅ 全部 36 个配置文件、脚本、模板
✅ 3 张 Grafana Dashboard JSON
✅ 8 条 Prometheus 告警规则
✅ DingTalk Webhook 桥脚本
✅ 完整项目文档

❌ 不包含：MOM 业务程序、数据库业务数据、授权证书
