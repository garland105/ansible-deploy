#!/bin/bash
# ============================================================
# install_ansible.sh
# 在 VM 46（控制节点）上初始化 Ansible 环境
# 用法: bash install_ansible.sh
# ============================================================
set -euo pipefail

echo ">>> [1/4] 更新 apt 源..."
apt update -y

echo ">>> [2/4] 安装 Ansible..."
apt install -y ansible

echo ">>> [3/4] 验证安装..."
ansible --version | head -1

echo ">>> [4/4] 测试连通性（请在 inventory.yml 中修改 IP 后执行）..."
echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "  使用步骤："
echo "  1. 编辑 inventory.yml 填入两台目标机器的 IP"
echo "  2. 编辑 group_vars/all.yml 修改密码和 token"
echo "  3. 运行: ansible-playbook -i inventory.yml site.yml"
echo ""
echo "  单独部署监控栈:"
echo "    ansible-playbook -i inventory.yml monitoring.yml"
echo ""
echo "  单独部署告警链路:"
echo "    ansible-playbook -i inventory.yml alerting.yml"
echo ""
