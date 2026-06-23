import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.222.129', username='user2', password='2')

cmds = [
    'PGPASSWORD=admin_pass psql -h 192.168.222.128 -U admin -d postgres -c "CREATE ROLE monitor WITH LOGIN PASSWORD \'monitor_2026\';" 2>&1',
    'PGPASSWORD=admin_pass psql -h 192.168.222.128 -U admin -d postgres -c "GRANT pg_monitor TO monitor;" 2>&1',
    'PGPASSWORD=monitor_2026 psql -h 192.168.222.128 -U monitor -d postgres -c "SELECT current_user;" 2>&1',
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(f"$ psql -h 192.168.222.128 ...")
    if out: print(out.strip())
    if err: print(f"ERR: {err.strip()}")

client.close()
