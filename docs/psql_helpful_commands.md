# Setup
Verify PSQL is running: `sudo systemctl status postgresql`
Connect from local: `sudo -u postgres psql`
Create user: 
`CREATE USER lydon_admin_test WITH PASSWORD 'aL9123pcxZ#__popNo_ERFDSfo0o!123ddddd_123CJK';` # Keeping a password in plain test is obviously a terrible idea. 
`ALTER USER lydon_admin_test WITH SUPERUSER;`
Restart PSQL: `sudo systemctl restart postgresql`
Check listening port: `SHOW port;`

# Connect 
psql -h localhost -U lydon_admin_test -d postgres

# Create DB 
CREATE DATABASE gho_db;

# Temporary permissions to connect from Dev VM
sudo visudo
add: carlydon ALL=(ALL) NOPASSWD: /usr/bin/psql